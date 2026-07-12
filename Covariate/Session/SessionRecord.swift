import Foundation

/// Exported session envelope — the "timestamped record tied to a specific
/// experiment" of objective O1. Schema documented in docs/schema.md; the
/// schema itself is a release deliverable (proposal deliverable 6).
struct SessionRecord: Codable {
    struct Meta: Codable {
        let schemaVersion: String
        let experimentID: String
        let condition: String       // "controlled" | "disturbed" | free text
        let site: String            // e.g. "chicago-kitchen"
        let device: String          // model identifier
        let osVersion: String
        let appVersion: String
        let startedAtWall: Date     // wall anchor; alignment uses sync fiducial
        let endedAtWall: Date
        let notes: String
        // v0.1.1 additive, both optional so older records and the current
        // capture path (which doesn't populate them yet) stay valid.
        /// Coarse, dataset-safe location fix at session start (opt-in).
        var location: LocationFix? = nil
        /// Pointer to the optional audio-free reference-video sidecar (opt-in).
        var video: VideoRef? = nil
    }

    /// Coarse location captured once at session start. Region + altitude only —
    /// never raw lat/long, because the record is packaged into a shared dataset.
    /// Altitude contextualizes the barometer baseline; region enables weather
    /// cross-reference for H1/H3. (schema v0.1.1)
    struct LocationFix: Codable {
        let region: String          // reverse-geocoded, e.g. "Chicago, IL, US"
        let altitudeM: Double?      // meters above sea level, if available
        let accuracy: String        // granularity actually stored, e.g. "city"
    }

    /// Pointer to the reference-video sidecar file that lives next to this JSON.
    /// The video is audio-free by construction (its capture session has no audio
    /// input); `hasAudio` is always false and exists to make that auditable.
    /// (schema v0.1.1)
    struct VideoRef: Codable {
        let filename: String        // sibling file, e.g. covariate_..._video.mov
        let codec: String           // e.g. "hevc"
        let resolution: String      // e.g. "1920x1080"
        let fps: Double
        let hasAudio: Bool          // always false — privacy invariant (a)
    }

    let meta: Meta
    let health: [ChannelHealth]
    let samples: [Sample]
}
