import ExpoModulesCore
import AVFoundation
import ImageIO

/// Ambient light via camera EXIF brightness metadata.
///
/// iOS exposes no public ambient-light-sensor API, so this reads the
/// `BrightnessValue` the camera pipeline attaches to every frame's EXIF
/// metadata via a minimal, low-power capture session — no pixel data is
/// inspected, and no photos or video are ever stored.
///
/// Ported from the native Swift prototype's `LightChannel`
/// (ambient-recorder repo, Covariate/Channels/LightChannel.swift). The
/// sensing logic below is intentionally close to a line-for-line port; only
/// the SharedClock/Sample/ChannelID harness types from that prototype are
/// swapped out, since this module has no dependency on that harness.
public class CovariateLightModule: Module {
  private let controller = LightSensorController()

  public func definition() -> ModuleDefinition {
    Name("CovariateLight")

    Events("onSample")

    AsyncFunction("isAvailable") { () -> Bool in
      AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back) != nil
    }

    AsyncFunction("requestPermissionsAsync") { () async -> [String: Any] in
      await CovariateLightModule.requestCameraPermission()
    }

    AsyncFunction("start") { () throws in
      try self.controller.start { [weak self] sample in
        self?.sendEvent("onSample", [
          "t": sample.t,
          "brightnessValue": sample.brightnessValue,
        ])
      }
    }

    Function("stop") {
      self.controller.stop()
    }

    OnDestroy {
      self.controller.stop()
    }
  }

  private static func requestCameraPermission() async -> [String: Any] {
    let status = AVCaptureDevice.authorizationStatus(for: .video)
    let granted: Bool
    switch status {
    case .authorized:
      granted = true
    case .notDetermined:
      granted = await AVCaptureDevice.requestAccess(for: .video)
    default:
      granted = false
    }
    return ["granted": granted, "status": granted ? "granted" : "denied"]
  }
}

/// Owns the AVCaptureSession + delegate. Kept separate from the Expo Module
/// class so the sensing logic mirrors the native prototype's `LightChannel`
/// as closely as possible.
private final class LightSensorController: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
  struct LightSample {
    let t: Double
    let brightnessValue: Double
  }

  /// Throttle to ~5 Hz; the camera delivers far more frames than we need and
  /// EXIF brightness is quantized in whole EV-ish steps anyway. Matches the
  /// native prototype's `nominalRate`.
  private let nominalRate: Double = 5.0
  private let session = AVCaptureSession()
  private let queue = DispatchQueue(label: "covariate.light")
  private var onSample: ((LightSample) -> Void)?
  private var lastEmit: TimeInterval = -1

  func start(onSample: @escaping (LightSample) -> Void) throws {
    guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
          let input = try? AVCaptureDeviceInput(device: device) else {
      throw CovariateLightError.unavailable
    }
    self.onSample = onSample
    lastEmit = -1

    session.beginConfiguration()
    session.sessionPreset = .low // metadata is all we need; minimize power draw
    guard session.canAddInput(input) else {
      session.commitConfiguration()
      throw CovariateLightError.unavailable
    }
    session.addInput(input)

    let output = AVCaptureVideoDataOutput()
    output.alwaysDiscardsLateVideoFrames = true
    output.setSampleBufferDelegate(self, queue: queue)
    guard session.canAddOutput(output) else {
      session.commitConfiguration()
      throw CovariateLightError.unavailable
    }
    session.addOutput(output)
    session.commitConfiguration()

    queue.async { [session] in session.startRunning() }
  }

  func stop() {
    onSample = nil
    queue.async { [session] in session.stopRunning() }
  }

  func captureOutput(_ output: AVCaptureOutput,
                      didOutput sampleBuffer: CMSampleBuffer,
                      from connection: AVCaptureConnection) {
    guard let onSample else { return }
    // NOTE: CACurrentMediaTime() is monotonic but per-device/per-boot — it is
    // NOT the same epoch as JS's Date.now(). The RN session/export layer
    // (not yet built) needs to reconcile native-clock timestamps from this
    // module and expo-audio against whatever clock the JS side stamps
    // accel/mag/baro with. Flagging here rather than silently picking
    // something that may not line up later.
    let t = CACurrentMediaTime()
    // Camera delivers ~15-30 fps; throttle to nominalRate.
    if lastEmit >= 0, t - lastEmit < 1.0 / nominalRate { return }
    guard let attachments = CMCopyDictionaryOfAttachments(
            allocator: nil, target: sampleBuffer,
            attachmentMode: kCMAttachmentMode_ShouldPropagate) as? [String: Any],
          let exif = attachments[kCGImagePropertyExifDictionary as String] as? [String: Any],
          let brightness = exif[kCGImagePropertyExifBrightnessValue as String] as? Double
    else { return }
    lastEmit = t
    onSample(LightSample(t: t, brightnessValue: brightness))
  }
}

private enum CovariateLightError: Error, LocalizedError {
  case unavailable

  var errorDescription: String? {
    switch self {
    case .unavailable:
      return "Ambient light sensing is unavailable on this device (no back camera, or the camera session could not be configured)."
    }
  }
}
