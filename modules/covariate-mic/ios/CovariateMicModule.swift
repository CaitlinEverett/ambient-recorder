import ExpoModulesCore
import AVFAudio

/// Sound LEVEL via an AVAudioEngine input tap.
///
/// Privacy invariant (matches the project's ethics statement): audio buffers
/// are reduced to a single RMS number in-place and never written anywhere.
/// There is no recording file, by construction — this channel cannot leak
/// audio. AVAudioEngine's tap API hands us in-memory buffers directly; unlike
/// AVAudioRecorder (which expo-audio's high-level recorder wraps), it never
/// creates a file on disk, even transiently.
///
/// Ported from the native Swift prototype's `MicLevelChannel`
/// (ambient-recorder repo, Covariate/Channels/MicLevelChannel.swift).
public class CovariateMicModule: Module {
  private let controller = MicLevelController()

  public func definition() -> ModuleDefinition {
    Name("CovariateMic")

    Events("onSample")

    AsyncFunction("requestPermissionsAsync") { () async -> [String: Any] in
      await CovariateMicModule.requestMicPermission()
    }

    AsyncFunction("start") { () throws in
      try self.controller.start { [weak self] sample in
        self?.sendEvent("onSample", [
          "t": sample.t,
          "dBFS": sample.dBFS,
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

  private static func requestMicPermission() async -> [String: Any] {
    let session = AVAudioSession.sharedInstance()
    switch session.recordPermission {
    case .granted:
      return ["granted": true, "status": "granted"]
    case .undetermined:
      let granted = await withCheckedContinuation { (cont: CheckedContinuation<Bool, Never>) in
        session.requestRecordPermission { granted in cont.resume(returning: granted) }
      }
      return ["granted": granted, "status": granted ? "granted" : "denied"]
    default:
      return ["granted": false, "status": "denied"]
    }
  }
}

/// Owns the AVAudioEngine tap. Kept separate from the Expo Module class so
/// the sensing logic mirrors the native prototype's `MicLevelChannel` as
/// closely as possible.
private final class MicLevelController {
  struct MicSample {
    let t: Double
    let dBFS: Double
  }

  private let engine = AVAudioEngine()
  private var onSample: ((MicSample) -> Void)?

  func start(onSample: @escaping (MicSample) -> Void) throws {
    self.onSample = onSample

    let session = AVAudioSession.sharedInstance()
    try session.setCategory(.record, mode: .measurement)
    try session.setActive(true)

    let input = engine.inputNode
    let format = input.outputFormat(forBus: 0)
    input.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
      guard let data = buffer.floatChannelData?[0] else { return }
      let n = Int(buffer.frameLength)
      guard n > 0 else { return }
      var sumSquares: Double = 0
      for i in 0..<n { sumSquares += Double(data[i]) * Double(data[i]) }
      let rms = (sumSquares / Double(n)).squareRoot()
      let dBFS = 20.0 * log10(max(rms, 1e-9))
      // NOTE: same per-device monotonic-clock caveat as CovariateLight — see
      // that module's comment. Needs reconciling with the JS session clock
      // once the recording/export layer exists.
      self?.onSample?(MicSample(t: CACurrentMediaTime(), dBFS: dBFS))
    }
    try engine.start()
  }

  func stop() {
    onSample = nil
    engine.inputNode.removeTap(onBus: 0)
    engine.stop()
    try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
  }
}
