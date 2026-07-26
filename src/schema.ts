// Export schema v0.1.3 — mirrors docs/schema.md (the cross-platform contract).
// One session -> one JSON file: covariate_<experimentID>_<ISO8601>.json.

export const SCHEMA_VERSION = '0.1.3';

export type ChannelId =
  | 'barometer'
  | 'accelerometer'
  | 'magnetometer'
  | 'light'
  | 'micLevel'
  | 'vibration' // derived from accelerometer — windowed RMS with gravity removed
  | 'external'
  | 'sync'; // cross-device alignment marker — one sample per emitted sync pulse

/** One reading from one channel. `t` = seconds since session anchor (monotonic). */
export interface Sample {
  t: number;
  channel: ChannelId;
  values: number[];
}

export interface ChannelHealth {
  channel: ChannelId;
  sampleCount: number;
  firstT: number | null;
  lastT: number | null;
  /** Largest gap between consecutive samples, seconds. */
  maxGap: number;
  /** Configured rate, Hz (null = event-driven). */
  nominalRate: number | null;
  /** Derived: 1 - count/expected. O1 gate: < 0.02 over >= 30 min. */
  dropFraction: number;
}

/** Coarse, dataset-safe location — region + altitude only, never raw coordinates. */
export interface LocationFix {
  region: string; // reverse-geocoded, e.g. "Chicago, IL, US"
  altitudeM: number | null; // meters ASL; contextualizes the barometer baseline
  accuracy: string; // granularity stored, e.g. "city"
}

export interface SessionMeta {
  schemaVersion: string;
  experimentID: string;
  condition: string; // "controlled" | "disturbed" | free text
  site: string;
  device: string;
  osVersion: string;
  appVersion: string;
  startedAtWall: string; // ISO 8601
  endedAtWall: string;
  notes: string;
  /**
   * v0.1.3, optional. Where the phone physically sat — surface, material, and
   * what it rests on. Placement changes the coupling between an event and the
   * accelerometer by more than some dose steps do, so a session without it is
   * not comparable to one recorded elsewhere.
   */
  placement?: string;
  location?: LocationFix; // v0.1.1, optional; present only when the user opts in
}

export interface SessionRecord {
  meta: SessionMeta;
  health: ChannelHealth[];
  samples: Sample[];
}

/** Nominal sample rate per channel, Hz. null = event-driven / irregular. */
export const NOMINAL_RATE: Record<ChannelId, number | null> = {
  accelerometer: 50,
  magnetometer: 25,
  barometer: null,
  light: 5,
  micLevel: 10,
  vibration: 5, // 200 ms window
  external: null,
  // Event-driven: emitted only when the operator marks a sync pulse. A
  // nominal rate here would be wrong — it would make dropFraction, which is
  // derived from expected-vs-actual count, meaningless for this channel.
  sync: null,
};
