import Foundation
import CoreMotion

/// 3-axis accelerometer via CMMotionManager (proposal ref [15]).
/// values: [x_g, y_g, z_g]
/// This is the vibration-meter building block (reimplemented hack #1);
/// vibration RMS for H1 is computed downstream in analysis, not here.
final class AccelerometerChannel: SensorChannel {
    let id: ChannelID = .accelerometer
    let nominalRate: Double? = 50.0
    private let manager = CMMotionManager()
    private let queue = OperationQueue()

    func start(clock: SharedClock, sink: @escaping (Sample) -> Void) throws {
        guard manager.isAccelerometerAvailable else {
            throw ChannelError.unavailable(id)
        }
        queue.maxConcurrentOperationCount = 1
        manager.accelerometerUpdateInterval = 1.0 / (nominalRate ?? 50.0)
        manager.startAccelerometerUpdates(to: queue) { [id] data, _ in
            guard let a = data?.acceleration else { return }
            sink(Sample(t: clock.now(), channel: id, values: [a.x, a.y, a.z]))
        }
    }

    func stop() { manager.stopAccelerometerUpdates() }
}
