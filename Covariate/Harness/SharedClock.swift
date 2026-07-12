import Foundation
import QuartzCore

/// A single monotonic timebase shared by every sensor channel in a session.
///
/// All samples are stamped with seconds since the session anchor, taken from
/// `CACurrentMediaTime()` (mach_absolute_time-backed, immune to wall-clock
/// changes). The wall-clock anchor is recorded once so exported records can be
/// aligned across devices; cross-device offset is measured with a physical
/// sync fiducial (tap/flash), not by trusting either clock.
struct SharedClock: Sendable {
    /// Wall-clock time at session start (for export metadata only).
    let anchorWall: Date
    /// Monotonic time at session start.
    let anchorMedia: CFTimeInterval

    init() {
        anchorWall = Date()
        anchorMedia = CACurrentMediaTime()
    }

    /// Seconds elapsed since the session anchor (monotonic).
    func now() -> TimeInterval {
        CACurrentMediaTime() - anchorMedia
    }
}
