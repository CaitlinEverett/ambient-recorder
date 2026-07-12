import Foundation
import CoreMotion

/// Barometric pressure via CMAltimeter (proposal ref [14]).
/// values: [pressure_kPa, relativeAltitude_m]
/// Foundation for the door/HVAC-transient signal (Wu et al. [5]).
final class BarometerChannel: SensorChannel {
    let id: ChannelID = .barometer
    let nominalRate: Double? = nil  // event-driven, ~1 Hz delivery; irregular
    private let altimeter = CMAltimeter()
    private let queue = OperationQueue()

    func start(clock: SharedClock, sink: @escaping (Sample) -> Void) throws {
        guard CMAltimeter.isRelativeAltitudeAvailable() else {
            throw ChannelError.unavailable(id)
        }
        queue.maxConcurrentOperationCount = 1
        altimeter.startRelativeAltitudeUpdates(to: queue) { [id] data, _ in
            guard let data else { return }
            sink(Sample(t: clock.now(), channel: id,
                        values: [data.pressure.doubleValue,
                                 data.relativeAltitude.doubleValue]))
        }
    }

    func stop() { altimeter.stopRelativeAltitudeUpdates() }
}
