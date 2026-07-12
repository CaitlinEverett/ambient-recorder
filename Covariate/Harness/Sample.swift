import Foundation

/// Identifiers for the five phone channels plus the optional external module.
enum ChannelID: String, Codable, CaseIterable, Sendable {
    case barometer      // kPa, relative altitude m
    case accelerometer  // g, 3-axis
    case magnetometer   // microtesla, 3-axis
    case light          // camera-derived EXIF brightness value (EV-ish, unitless)
    case micLevel       // dBFS RMS — level only, never audio
    case external       // ESP32 + BME280 over BLE (stretch): temp C, RH %, hPa
}

/// One reading from one channel on the shared clock.
struct Sample: Codable, Sendable {
    /// Seconds since session anchor (monotonic shared clock).
    let t: TimeInterval
    let channel: ChannelID
    /// Channel-specific values; meaning and order documented in docs/schema.md.
    let values: [Double]
}
