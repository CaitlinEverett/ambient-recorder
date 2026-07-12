import Foundation
import CoreMotion

/// 3-axis magnetometer via CMMotionManager (proposal ref [15]).
/// values: [x_uT, y_uT, z_uT]
/// Captures nearby equipment switching (motors, centrifuges) as field shifts.
final class MagnetometerChannel: SensorChannel {
    let id: ChannelID = .magnetometer
    let nominalRate: Double? = 25.0
    private let manager = CMMotionManager()
    private let queue = OperationQueue()

    func start(clock: SharedClock, sink: @escaping (Sample) -> Void) throws {
        guard manager.isMagnetometerAvailable else {
            throw ChannelError.unavailable(id)
        }
        queue.maxConcurrentOperationCount = 1
        manager.magnetometerUpdateInterval = 1.0 / (nominalRate ?? 25.0)
        manager.startMagnetometerUpdates(to: queue) { [id] data, _ in
            guard let f = data?.magneticField else { return }
            sink(Sample(t: clock.now(), channel: id, values: [f.x, f.y, f.z]))
        }
    }

    func stop() { manager.stopMagnetometerUpdates() }
}
