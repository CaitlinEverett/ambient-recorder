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
    }

    let meta: Meta
    let health: [ChannelHealth]
    let samples: [Sample]
}
