import SwiftUI

/// The whole design system, on purpose: one accent color, a status palette, and
/// a spacing scale. Native SwiftUI components do the rest (Form, List, Gauge,
/// ProgressView, SF Symbols). Custom-drawing is reserved for data marks — see
/// LevelMeter and docs/mockups.md. No gradients, glows, or spring motion.
enum Theme {

    // MARK: Color
    /// App accent (asset catalog `AccentColor`; also set as the global accent in
    /// project.yml so native controls tint to match).
    static let accent = Color("AccentColor")
    /// Unlit meter segments / inactive track.
    static let track = Color.gray.opacity(0.3)

    // Sampling-health status, mapped to the O1 <2% drop gate.
    static let ok = Color.green
    static let warn = Color.orange
    static let bad = Color.red

    /// Status color for a channel's drop fraction against the O1 gate.
    /// <2% pass, 2–5% warn, >5% fail. Used by the live rows and the summary.
    static func gate(_ dropFraction: Double) -> Color {
        switch dropFraction {
        case ..<0.02: return ok
        case ..<0.05: return warn
        default: return bad
        }
    }

    // MARK: Spacing (pt)
    static let xs: CGFloat = 4
    static let s: CGFloat = 8
    static let m: CGFloat = 16
    static let l: CGFloat = 24

    // MARK: Shape
    static let radius: CGFloat = 10
    static let meterHeight: CGFloat = 14
}
