import Foundation

/// Per-channel sampling-health bookkeeping.
///
/// iOS backgrounding and Core Motion delivery caps can silently throttle or
/// drop samples (proposal, Challenge 3). The harness measures its own health
/// so degraded sessions are visible in the export, never silent.
struct ChannelHealth: Codable, Sendable {
    let channel: ChannelID
    var sampleCount: Int = 0
    var firstT: TimeInterval?
    var lastT: TimeInterval?
    /// Largest gap between consecutive samples, seconds.
    var maxGap: TimeInterval = 0
    var nominalRate: Double?

    init(channel: ChannelID, nominalRate: Double?) {
        self.channel = channel
        self.nominalRate = nominalRate
    }

    mutating func record(t: TimeInterval) {
        if let last = lastT { maxGap = max(maxGap, t - last) }
        if firstT == nil { firstT = t }
        lastT = t
        sampleCount += 1
    }

    /// Fraction of expected samples that never arrived (0 when unknown).
    /// O1 success criterion: < 0.02 over a >= 30-minute session.
    var dropFraction: Double {
        guard let rate = nominalRate, let first = firstT, let last = lastT,
              last > first else { return 0 }
        let expected = (last - first) * rate
        guard expected > 0 else { return 0 }
        return max(0, 1.0 - Double(sampleCount) / expected)
    }
}
