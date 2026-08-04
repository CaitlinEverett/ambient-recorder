// Channel registry — the single source of truth for what a channel is called,
// whether it's a direct sensor reading or something computed from one, and (for
// derived channels) exactly how. health.ts/calibrate.ts/SensorTools.tsx key their
// data by ChannelId and look up display metadata here, so a new derived channel
// (or a change to an existing one's parameters) is defined in one place instead
// of three. `params` doubles as the seed for a future per-channel settings UI —
// today they're read-only display, but the shape is already "the knobs."

import { ChannelId } from './schema';

export type ChannelKind = 'direct' | 'derived';

export interface ChannelDef {
  id: ChannelId;
  label: string; // short display name, e.g. 'vib'
  unit: string;
  decimals: number; // display precision
  kind: ChannelKind;
  derivedFrom?: ChannelId; // set when kind === 'derived'
  method?: string; // human-readable derivation description
  params?: Record<string, number>; // the derivation's knobs
  defaultEnabled: boolean; // whether a new experiment records this channel by default
}

export const CHANNELS: ChannelDef[] = [
  { id: 'accelerometer', label: 'accel', unit: 'g', decimals: 3, kind: 'direct', defaultEnabled: true },
  {
    id: 'vibration',
    label: 'vib',
    unit: 'g RMS',
    decimals: 3,
    kind: 'derived',
    derivedFrom: 'accelerometer',
    method: 'RMS of gravity-subtracted accelerometer magnitude over a rolling window',
    params: { windowMs: 200, gravityAlpha: 0.9 },
    defaultEnabled: true,
  },
  { id: 'magnetometer', label: 'mag', unit: 'µT', decimals: 1, kind: 'direct', defaultEnabled: true },
  { id: 'barometer', label: 'baro', unit: 'hPa', decimals: 2, kind: 'direct', defaultEnabled: true },
  { id: 'light', label: 'light', unit: 'EV', decimals: 2, kind: 'direct', defaultEnabled: true },
  { id: 'micLevel', label: 'mic', unit: 'dBFS', decimals: 1, kind: 'direct', defaultEnabled: true },
];

export const CHANNEL_BY_ID: Partial<Record<ChannelId, ChannelDef>> = Object.fromEntries(
  CHANNELS.map((c) => [c.id, c])
);

export const DEFAULT_ENABLED_CHANNELS: ChannelId[] = CHANNELS.filter((c) => c.defaultEnabled).map((c) => c.id);

export function childrenOf(id: ChannelId): ChannelDef[] {
  return CHANNELS.filter((c) => c.derivedFrom === id);
}

/** Native-module-backed channels (light, mic) are only usable in a dev client, not Expo Go. */
export function isChannelAvailable(id: ChannelId, native: { hasLight: boolean; hasMic: boolean }): boolean {
  if (id === 'light') return native.hasLight;
  if (id === 'micLevel') return native.hasMic;
  return true;
}

/** One-line "derived from X · how" caption for a derived channel's UI row. */
export function describeDerivation(def: ChannelDef): string | null {
  if (def.kind !== 'derived' || !def.method) return null;
  const parent = def.derivedFrom ? (CHANNEL_BY_ID[def.derivedFrom]?.label ?? def.derivedFrom) : '?';
  const params = def.params
    ? Object.entries(def.params)
        .map(([k, v]) => `${k}=${v}`)
        .join(', ')
    : '';
  return `derived from ${parent} · ${def.method}${params ? ` (${params})` : ''}`;
}
