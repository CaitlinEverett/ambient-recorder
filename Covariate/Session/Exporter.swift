import Foundation

/// Writes a SessionRecord to Documents as pretty-printed JSON.
/// Filename: covariate_<experimentID>_<ISO8601>.json — importable as a
/// notebook entry (O1) and the unit of the released dataset (deliverable 3).
enum Exporter {
    static func write(_ record: SessionRecord) throws -> URL {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(record)

        let stamp = ISO8601DateFormatter().string(from: record.meta.startedAtWall)
            .replacingOccurrences(of: ":", with: "-")
        let safeID = record.meta.experimentID
            .replacingOccurrences(of: "/", with: "-")
            .replacingOccurrences(of: " ", with: "_")
        let name = "covariate_\(safeID.isEmpty ? "session" : safeID)_\(stamp).json"

        let docs = FileManager.default.urls(for: .documentDirectory,
                                            in: .userDomainMask)[0]
        let url = docs.appendingPathComponent(name)
        try data.write(to: url, options: .atomic)
        return url
    }
}
