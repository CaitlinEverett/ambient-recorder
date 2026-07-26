// SessionRecorder — buffers every sample in memory, tracks per-channel health,
// and assembles a schema-v0.1.3 SessionRecord on stop. Port of the Swift
// RecordingSession/SessionRecord/Exporter (see the covariate-ios-native archive).
//
// Scope note: samples buffer in memory and are written once on stop, same as the
// original skeleton. Incremental disk streaming (crash-safe long sessions) is a
// later hardening step, not this piece.

import * as Device from 'expo-device';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import {
  ChannelHealth,
  ChannelId,
  LocationFix,
  NOMINAL_RATE,
  SCHEMA_VERSION,
  Sample,
  SessionRecord,
} from './schema';

type Health = { count: number; firstT: number | null; lastT: number | null; maxGap: number };

function monotonicMs(): number {
  const p = (globalThis as any).performance;
  return typeof p?.now === 'function' ? p.now() : Date.now();
}

export class SessionRecorder {
  private samples: Sample[] = [];
  private health: Partial<Record<ChannelId, Health>> = {};
  private startedMs = 0;
  private startedWall = new Date();

  start() {
    this.samples = [];
    this.health = {};
    this.startedMs = monotonicMs();
    this.startedWall = new Date();
  }

  /** Record one reading. Timestamped `t` = seconds since start (monotonic). */
  ingest(channel: ChannelId, values: number[]) {
    const t = (monotonicMs() - this.startedMs) / 1000;
    this.samples.push({ t, channel, values });
    let h = this.health[channel];
    if (!h) {
      h = { count: 0, firstT: null, lastT: null, maxGap: 0 };
      this.health[channel] = h;
    }
    if (h.lastT !== null) h.maxGap = Math.max(h.maxGap, t - h.lastT);
    if (h.firstT === null) h.firstT = t;
    h.lastT = t;
    h.count++;
  }

  get sampleCount(): number {
    return this.samples.length;
  }

  private buildHealth(): ChannelHealth[] {
    return (Object.keys(this.health) as ChannelId[])
      .map((channel) => {
        const h = this.health[channel]!;
        const rate = NOMINAL_RATE[channel];
        let dropFraction = 0;
        if (rate && h.firstT !== null && h.lastT !== null && h.lastT > h.firstT) {
          const expected = (h.lastT - h.firstT) * rate;
          if (expected > 0) dropFraction = Math.max(0, 1 - h.count / expected);
        }
        return {
          channel,
          sampleCount: h.count,
          firstT: h.firstT,
          lastT: h.lastT,
          maxGap: h.maxGap,
          nominalRate: rate,
          dropFraction,
        };
      })
      .sort((a, b) => a.channel.localeCompare(b.channel));
  }

  build(input: { experimentID: string; condition: string; site: string; notes: string; placement?: string; location?: LocationFix | null }): SessionRecord {
    return {
      meta: {
        schemaVersion: SCHEMA_VERSION,
        experimentID: input.experimentID,
        condition: input.condition,
        site: input.site,
        notes: input.notes,
        placement: input.placement?.trim() ? input.placement.trim() : undefined,
        location: input.location ?? undefined,
        device: Device.modelName ?? 'unknown',
        osVersion: `${Device.osName ?? ''} ${Device.osVersion ?? ''}`.trim(),
        appVersion: 'mvp',
        startedAtWall: this.startedWall.toISOString(),
        endedAtWall: new Date().toISOString(),
      },
      health: this.buildHealth(),
      samples: this.samples,
    };
  }
}

/** Write a record to a JSON file in Documents and open the share sheet. */
export async function exportRecord(record: SessionRecord): Promise<{ uri: string; name: string }> {
  const safeId = (record.meta.experimentID || 'session').replace(/[^\w.-]+/g, '_');
  const stamp = record.meta.startedAtWall.replace(/[:.]/g, '-');
  const name = `covariate_${safeId}_${stamp}.json`;
  const uri = (FileSystem.documentDirectory ?? '') + name;
  await FileSystem.writeAsStringAsync(uri, JSON.stringify(record, null, 2));
  // Writes only — sharing is triggered separately by a user tap (presenting the
  // iOS share sheet from an explicit gesture avoids the blank/hung-sheet issue).
  return { uri, name };
}

export async function shareUri(uri: string): Promise<void> {
  if (await Sharing.isAvailableAsync()) {
    await Sharing.shareAsync(uri, { mimeType: 'application/json', dialogTitle: 'Covariate session' });
  }
}
