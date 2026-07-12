import Foundation
import AVFAudio

/// Sound LEVEL via an AVAudioEngine input tap (proposal ref [16]).
/// values: [rms_dBFS]
///
/// Privacy invariant (Ethics statement): audio buffers are reduced to a single
/// RMS number in-place and never written anywhere. There is no recording file,
/// by construction — this channel cannot leak audio.
/// Building block of reimplemented hack #2 (noise half of light/noise logger).
final class MicLevelChannel: SensorChannel {
    let id: ChannelID = .micLevel
    let nominalRate: Double? = 10.0  // ~one RMS frame per 4096 samples @ 44.1k
    private let engine = AVAudioEngine()

    func start(clock: SharedClock, sink: @escaping (Sample) -> Void) throws {
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.record, mode: .measurement)
        try session.setActive(true)

        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        input.installTap(onBus: 0, bufferSize: 4096, format: format) { [id] buffer, _ in
            guard let data = buffer.floatChannelData?[0] else { return }
            let n = Int(buffer.frameLength)
            guard n > 0 else { return }
            var sumSquares: Double = 0
            for i in 0..<n { sumSquares += Double(data[i]) * Double(data[i]) }
            let rms = (sumSquares / Double(n)).squareRoot()
            let dBFS = 20.0 * log10(max(rms, 1e-9))
            sink(Sample(t: clock.now(), channel: id, values: [dBFS]))
        }
        try engine.start()
    }

    func stop() {
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
}
