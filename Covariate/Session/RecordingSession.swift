import Foundation
import UIKit

/// Owns one recording session: starts all channels on a shared clock, fans
/// their samples into one buffer, tracks sampling health, and exports a
/// SessionRecord on stop.
///
/// Skeleton scope: samples buffer in memory and are written once on stop.
/// Week-1 hardening: stream to disk incrementally so a killed app loses
/// seconds, not the session. (TODO, tracked in README roadmap.)
@MainActor
final class RecordingSession: ObservableObject {
    @Published private(set) var isRecording = false
    @Published private(set) var stats: [ChannelID: ChannelHealth] = [:]
    @Published private(set) var latest: [ChannelID: Sample] = [:]
    @Published private(set) var startedChannels: [ChannelID] = []
    @Published private(set) var failedChannels: [ChannelID: String] = [:]
    @Published var lastExportURL: URL?

    private var channels: [SensorChannel] = []
    private var clock: SharedClock?
    private var samples: [Sample] = []
    private var health: [ChannelID: ChannelHealth] = [:]
    private let intake = DispatchQueue(label: "covariate.intake")
    private var lastUIPush: TimeInterval = 0
    private var startedWall = Date()

    func start(experimentID: String, condition: String, site: String, notes: String) {
        guard !isRecording else { return }
        let clock = SharedClock()
        self.clock = clock
        samples = []
        health = [:]
        stats = [:]
        latest = [:]
        startedChannels = []
        failedChannels = [:]
        startedWall = clock.anchorWall
        sessionMeta = (experimentID, condition, site, notes)

        channels = [
            BarometerChannel(),
            AccelerometerChannel(),
            MagnetometerChannel(),
            LightChannel(),
            MicLevelChannel(),
        ]
        for channel in channels {
            health[channel.id] = ChannelHealth(channel: channel.id,
                                               nominalRate: channel.nominalRate)
            do {
                try channel.start(clock: clock) { [weak self] sample in
                    self?.ingest(sample)
                }
                startedChannels.append(channel.id)
            } catch {
                failedChannels[channel.id] = error.localizedDescription
            }
        }
        isRecording = true
        UIApplication.shared.isIdleTimerDisabled = true  // bench sessions run long
    }

    func stop() {
        guard isRecording, let clock else { return }
        for channel in channels { channel.stop() }
        isRecording = false
        UIApplication.shared.isIdleTimerDisabled = false

        let (experimentID, condition, site, notes) = sessionMeta
        // Drain the intake queue before snapshotting.
        intake.sync {}
        let record = SessionRecord(
            meta: .init(
                schemaVersion: "0.1.0",
                experimentID: experimentID,
                condition: condition,
                site: site,
                device: UIDevice.current.model,
                osVersion: UIDevice.current.systemVersion,
                appVersion: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "dev",
                startedAtWall: clock.anchorWall,
                endedAtWall: Date(),
                notes: notes
            ),
            health: Array(health.values).sorted { $0.channel.rawValue < $1.channel.rawValue },
            samples: samples
        )
        do {
            lastExportURL = try Exporter.write(record)
        } catch {
            failedChannels[.external] = "export failed: \(error.localizedDescription)"
        }
    }

    private var sessionMeta: (String, String, String, String) = ("", "", "", "")

    private nonisolated func ingest(_ sample: Sample) {
        intake.async { [weak self] in
            guard let self else { return }
            Task { @MainActor in
                self.samples.append(sample)
                self.health[sample.channel]?.record(t: sample.t)
                // Throttle UI publishing to ~4 Hz; the buffer takes every sample.
                if sample.t - self.lastUIPush > 0.25 {
                    self.lastUIPush = sample.t
                    self.stats = self.health
                    self.latest[sample.channel] = sample
                }
            }
        }
    }
}
