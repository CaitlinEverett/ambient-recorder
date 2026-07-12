import Foundation
import AVFoundation
import ImageIO

/// Ambient light via camera EXIF brightness metadata (proposal ref [17]).
/// values: [brightnessValue]  (EXIF BrightnessValue, ~log2 luminance, unitless)
///
/// iOS exposes no public ambient-light-sensor API, so this is the documented
/// workaround (proposal, Challenge 4): run a minimal capture session and read
/// the BrightnessValue the camera pipeline attaches to every frame. No pixel
/// data is inspected, and no photos or video are ever stored.
/// Building block of reimplemented hack #2 (light half of light/noise logger).
final class LightChannel: NSObject, SensorChannel, AVCaptureVideoDataOutputSampleBufferDelegate {
    let id: ChannelID = .light
    let nominalRate: Double? = 5.0
    private let session = AVCaptureSession()
    private let queue = DispatchQueue(label: "covariate.light")
    private var clock: SharedClock?
    private var sink: ((Sample) -> Void)?
    private var lastEmit: TimeInterval = -1

    func start(clock: SharedClock, sink: @escaping (Sample) -> Void) throws {
        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera,
                                                   for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: device) else {
            throw ChannelError.unavailable(id)
        }
        self.clock = clock
        self.sink = sink

        session.beginConfiguration()
        session.sessionPreset = .low  // metadata is all we need; minimize power
        guard session.canAddInput(input) else {
            session.commitConfiguration()
            throw ChannelError.unavailable(id)
        }
        session.addInput(input)
        let output = AVCaptureVideoDataOutput()
        output.alwaysDiscardsLateVideoFrames = true
        output.setSampleBufferDelegate(self, queue: queue)
        guard session.canAddOutput(output) else {
            session.commitConfiguration()
            throw ChannelError.unavailable(id)
        }
        session.addOutput(output)
        session.commitConfiguration()
        queue.async { [session] in session.startRunning() }
    }

    func stop() {
        queue.async { [session] in session.stopRunning() }
    }

    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer,
                       from connection: AVCaptureConnection) {
        guard let clock, let sink else { return }
        let t = clock.now()
        // Camera delivers ~15-30 fps; throttle to nominalRate.
        if lastEmit >= 0, t - lastEmit < 1.0 / (nominalRate ?? 5.0) { return }
        guard let attachments = CMCopyDictionaryOfAttachments(
                allocator: nil, target: sampleBuffer,
                attachmentMode: kCMAttachmentMode_ShouldPropagate) as? [String: Any],
              let exif = attachments[kCGImagePropertyExifDictionary as String] as? [String: Any],
              let brightness = exif[kCGImagePropertyExifBrightnessValue as String] as? Double
        else { return }
        lastEmit = t
        sink(Sample(t: t, channel: id, values: [brightness]))
    }
}
