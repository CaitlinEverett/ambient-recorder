import SwiftUI

/// One-sided segmented level meter — the shared primitive for any "how much
/// right now" channel: mic dBFS and accelerometer vibration RMS both use it.
///
/// Deliberately NOT a waveform. Bars only rise from a baseline; there is no
/// mirrored negative half, because a mirrored squiggle reads as "we recorded
/// your audio" and we never do (privacy invariant a). Drive it at the session
/// UI rate (~4 Hz), never per sample — see RecordingSession's throttle and
/// docs/mockups.md §5.
struct LevelMeter: View {
    /// Current reading and the range to show it against, in the value's own
    /// units (e.g. -70...-10 dBFS for mic, 0...0.5 g for vibration).
    let value: Double
    let range: ClosedRange<Double>
    var segments: Int = 20
    var tint: Color = Theme.accent

    private var fraction: Double {
        let span = range.upperBound - range.lowerBound
        guard span > 0 else { return 0 }
        return min(max((value - range.lowerBound) / span, 0), 1)
    }

    var body: some View {
        Canvas { context, size in
            let gap = 2.0
            let width = (size.width - gap * Double(segments - 1)) / Double(segments)
            guard width > 0 else { return }
            let lit = Int((fraction * Double(segments)).rounded(.down))
            for i in 0..<segments {
                let x = Double(i) * (width + gap)
                let rect = CGRect(x: x, y: 0, width: width, height: size.height)
                context.fill(Path(rect), with: .color(i < lit ? tint : Theme.track))
            }
        }
        .frame(height: Theme.meterHeight)
        .accessibilityElement()
        .accessibilityLabel("Level meter")
    }
}

#Preview {
    VStack(spacing: 24) {
        LevelMeter(value: -46, range: -70 ... -10)      // mic, quiet room
        LevelMeter(value: 0.021, range: 0 ... 0.5,      // vibration, at rest
                   tint: Theme.warn)
    }
    .padding()
}
