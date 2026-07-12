import SwiftUI

/// Skeleton UI: session metadata in, live channel health out, JSON export.
/// Deliberately minimal — the reliability study is the contribution, and
/// polish is the first thing cut (proposal, Project Plan). Not final UI.
struct ContentView: View {
    @StateObject private var session = RecordingSession()
    @State private var experimentID = ""
    @State private var condition = "controlled"
    @State private var site = ""
    @State private var notes = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Experiment") {
                    TextField("Experiment ID", text: $experimentID)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)
                    Picker("Condition", selection: $condition) {
                        Text("Controlled").tag("controlled")
                        Text("Disturbed").tag("disturbed")
                    }
                    TextField("Site (e.g. chicago-kitchen)", text: $site)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)
                    TextField("Notes", text: $notes)
                }

                Section("Channels") {
                    ForEach(ChannelID.allCases.filter { $0 != .external }, id: \.self) { id in
                        ChannelRow(id: id,
                                   health: session.stats[id],
                                   sample: session.latest[id],
                                   failure: session.failedChannels[id])
                    }
                }

                Section {
                    if session.isRecording {
                        Button(role: .destructive) {
                            session.stop()
                        } label: {
                            Label("Stop & Export", systemImage: "stop.circle.fill")
                                .frame(maxWidth: .infinity)
                        }
                    } else {
                        Button {
                            session.start(experimentID: experimentID,
                                          condition: condition,
                                          site: site,
                                          notes: notes)
                        } label: {
                            Label("Start Session", systemImage: "record.circle")
                                .frame(maxWidth: .infinity)
                        }
                        .disabled(experimentID.isEmpty)
                    }
                }

                if let url = session.lastExportURL {
                    Section("Last export") {
                        ShareLink(item: url) {
                            Label(url.lastPathComponent, systemImage: "square.and.arrow.up")
                        }
                    }
                }
            }
            .navigationTitle("Covariate")
        }
    }
}

private struct ChannelRow: View {
    let id: ChannelID
    let health: ChannelHealth?
    let sample: Sample?
    let failure: String?

    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(id.rawValue).font(.body.monospaced())
                if let failure {
                    Text(failure).font(.caption).foregroundStyle(.red)
                } else if let sample {
                    Text(sample.values.map { String(format: "%.3f", $0) }
                            .joined(separator: "  "))
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                }
            }
            Spacer()
            if let health {
                VStack(alignment: .trailing) {
                    Text("\(health.sampleCount)")
                        .font(.caption.monospaced())
                    if health.dropFraction > 0.02 {
                        Text(String(format: "%.1f%% drop", health.dropFraction * 100))
                            .font(.caption2).foregroundStyle(.orange)
                    }
                }
            }
        }
    }
}

#Preview {
    ContentView()
}
