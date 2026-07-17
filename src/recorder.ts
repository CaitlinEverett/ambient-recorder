// SessionRecorder — buffers every sample in memory, tracks per-channel health,
// and assembles a schema-v0.1.1 SessionRecord on stop. Port of the Swift
// RecordingSession/SessionRecord/Exporter (see the covariate-ios-native archive).
//
// Scope note: samples buffer in memory and are written once on stop, same as the
// original skeleton. Incremental disk streaming (crash-safe long sessions) is a
// later hardening step, not this piece.

import * as Device from 'expo-device';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { saveSession, getSessionJson } from './db';
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

  build(input: { experimentID: string; condition: string; site: string; notes: string; location?: LocationFix | null }): SessionRecord {
    return {
      meta: {
        schemaVersion: SCHEMA_VERSION,
        experimentID: input.experimentID,
        condition: input.condition,
        site: input.site,
        notes: input.notes,
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

/** Persist a completed record to SQLite (replaces the old write-JSON-file-to-Documents step). */
export async function exportRecord(record: SessionRecord): Promise<{ id: string; name: string }> {
  return saveSession(record);
}

/**
 * Pull a session's JSON back out of SQLite, write it to a *temporary* cache
 * file just long enough to hand off to the OS share sheet (Mail is one of
 * the options there, same as before), then delete the temp file.
 *
 * Note: on iOS, Sharing.shareAsync's promise resolves once the share sheet
 * is dismissed, so the delete-in-finally below is safe there. On Android the
 * share intent can return before the target app has finished reading the
 * file; if you ever see blank/missing attachments on Android specifically,
 * switch the delete to a short delay (e.g. a few seconds) instead of an
 * immediate post-await cleanup.
 */
export async function shareSession(id: string, name: string): Promise<void> {
  const json = await getSessionJson(id);
  if (!json) throw new Error(`Session ${id} not found`);
  const uri = (FileSystem.cacheDirectory ?? '') + name;
  await FileSystem.writeAsStringAsync(uri, json);
  try {
    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(uri, { mimeType: 'application/json', dialogTitle: 'Covariate session' });
    }
  } finally {
    await FileSystem.deleteAsync(uri, { idempotent: true });
  }
}
