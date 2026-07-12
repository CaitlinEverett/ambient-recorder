import Foundation

/// A source of timestamped samples. Implementations wrap one sensor API and
/// deliver every reading through `sink`, stamped with the shared clock.
///
/// Contract:
/// - `start` is called once per session; `stop` must fully release the sensor.
/// - `sink` may be called from any queue; the session serializes downstream.
/// - Channels report their nominal rate so SamplingHealth can compute drops.
protocol SensorChannel: AnyObject {
    var id: ChannelID { get }
    /// Nominal samples per second this channel is configured to deliver.
    /// Channels that are event-driven or irregular return nil.
    var nominalRate: Double? { get }
    func start(clock: SharedClock, sink: @escaping (Sample) -> Void) throws
    func stop()
}

enum ChannelError: Error, LocalizedError {
    case unavailable(ChannelID)
    case permissionDenied(ChannelID)

    var errorDescription: String? {
        switch self {
        case .unavailable(let id): return "\(id.rawValue) is not available on this device"
        case .permissionDenied(let id): return "\(id.rawValue) permission denied"
        }
    }
}
