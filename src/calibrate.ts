// Calibration — a guided at-rest capture that measures each channel's bias (mean)
// and NOISE FLOOR (standard deviation). These are the numbers the study consumes:
// H2 tests "bias within the channel's noise floor," H1 tests against a baseline.
// Answers the proposal's "commodity sensors ship uncalibrated" point directly.

import { Accelerometer, Barometer, Magnetometer } from 'expo-sensors';
import * as FileSystem from 'expo-file-system/legacy';

export interface ChannelBaseline {
  channel: string;
  n: number;
  mean: number; // mean magnitude (accel g, mag µT, baro hPa)
  noiseFloor: number; // std of magnitude
  rate: number; // Hz
}

export interface Baseline {
  kind: 'baseline';
  schemaVersion: string;
  experimentID: string;
  durationS: number;
  capturedAt: string; // ISO 8601
  channels: ChannelBaseline[];
}

const mag3 = (x: number, y: number, z: number) => Math.sqrt(x * x + y * y + z * z);

function stats(vals: number[]): { mean: number; std: number } {
  const n = vals.length;
  if (n === 0) return { mean: NaN, std: NaN };
  const mean = vals.reduce((a, b) => a + b, 0) / n;
  const variance = vals.reduce((a, b) => a + (b - mean) * (b - mean), 0) / n;
  return { mean, std: Math.sqrt(variance) };
}

export async function runCalibration(opts: { seconds?: number; experimentID: string }): Promise<Baseline> {
  const seconds = opts.seconds ?? 20;
  const aMags: number[] = [];
  const mMags: number[] = [];
  const pVals: number[] = [];

  try { await Accelerometer.requestPermissionsAsync(); } catch {}
  Accelerometer.setUpdateInterval(20);
  Magnetometer.setUpdateInterval(40);
  const subs = [
    Accelerometer.addListener((d) => aMags.push(mag3(d.x, d.y, d.z))),
    Magnetometer.addListener((d) => mMags.push(mag3(d.x, d.y, d.z))),
    Barometer.addListener((d: any) => pVals.push(d.pressure)),
  ];
  await new Promise((resolve) => setTimeout(resolve, seconds * 1000));
  subs.forEach((s) => s.remove());

  const mk = (channel: string, vals: number[]): ChannelBaseline => {
    const { mean, std } = stats(vals);
    return { channel, n: vals.length, mean, noiseFloor: std, rate: vals.length / seconds };
  };

  return {
    kind: 'baseline',
    schemaVersion: '0.1.1',
    experimentID: opts.experimentID,
    durationS: seconds,
    capturedAt: new Date().toISOString(),
    channels: [mk('accelerometer', aMags), mk('magnetometer', mMags), mk('barometer', pVals)],
  };
}

export async function saveBaseline(b: Baseline): Promise<{ uri: string; name: string }> {
  const safeId = (b.experimentID || 'session').replace(/[^\w.-]+/g, '_');
  const stamp = b.capturedAt.replace(/[:.]/g, '-');
  const name = `covariate_baseline_${safeId}_${stamp}.json`;
  const uri = (FileSystem.documentDirectory ?? '') + name;
  await FileSystem.writeAsStringAsync(uri, JSON.stringify(b, null, 2));
  return { uri, name };
}
