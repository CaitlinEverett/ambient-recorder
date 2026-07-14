// Export schema v0.1.1 — mirrors docs/schema.md (the cross-platform contract).
// One session -> one JSON file: covariate_<experimentID>_<ISO8601>.json.

export const SCHEMA_VERSION = '0.1.1';

export type ChannelId =
  | 'barometer'
  | 'accelerometer'
  | 'magnetometer'
  | 'light'
  | 'micLevel'
  | 'external';

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
  external: null,
};
