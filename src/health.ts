// Pre-flight sensor health check — sample accel/mag/baro briefly, then judge
// present / at-rate / sane before trusting a recording. This is the "can I trust
// this run" gate (the pre-flight check from the original mockups). Native
// light/mic are reported from module presence (deep-checked in the dev client).

import { Accelerometer, Barometer, Magnetometer } from 'expo-sensors';
import { VibrationMeter, VibrationSample } from './vibration';

export type HealthStatus = 'ok' | 'warn' | 'fail';
export interface ChannelCheck {
  channel: string;
  status: HealthStatus;
  detail: string;
  derivedFrom?: string; // set when this isn't its own sensor — computed from another channel's raw stream
}

const mag3 = (x: number, y: number, z: number) => Math.sqrt(x * x + y * y + z * z);

export async function runHealthCheck(opts: {
  ms?: number;
  hasLight: boolean;
  hasMic: boolean;
}): Promise<ChannelCheck[]> {
  const ms = opts.ms ?? 3000;
  // Store the last *magnitude* (a number) directly from each listener — avoids a
  // TS closure-narrowing pitfall and is all the sane-check needs.
  let aMag = NaN, mMag = NaN, pLast = NaN;
  let aN = 0, mN = 0, pN = 0;
  const vMeter = new VibrationMeter(200); // same window as the live 'vibration' channel
  const vibWindows: VibrationSample[] = [];

  try { await Accelerometer.requestPermissionsAsync(); } catch {}
  Accelerometer.setUpdateInterval(20);
  Magnetometer.setUpdateInterval(40);
  const subs = [
    Accelerometer.addListener((d) => {
      aMag = mag3(d.x, d.y, d.z); aN++;
      const v = vMeter.push(d.x, d.y, d.z);
      if (v) vibWindows.push(v);
    }),
    Magnetometer.addListener((d) => { mMag = mag3(d.x, d.y, d.z); mN++; }),
    Barometer.addListener((d: any) => { pLast = d.pressure; pN++; }),
  ];
  await new Promise((resolve) => setTimeout(resolve, ms));
  subs.forEach((s) => s.remove());

  const secs = ms / 1000;
  const out: ChannelCheck[] = [];

  // Accelerometer — present, ~50 Hz, total ≈ 1 g at rest.
  if (aN === 0) {
    out.push({ channel: 'accel', status: 'fail', detail: 'no data — motion permission?' });
  } else {
    const rate = aN / secs;
    const sane = aMag >= 0.7 && aMag <= 1.3;
    out.push({
      channel: 'accel',
      status: rate >= 25 && sane ? 'ok' : 'warn',
      detail: `${rate.toFixed(0)} Hz · |a| ${aMag.toFixed(2)} g${sane ? '' : ' — expect ≈1 g at rest'}`,
    });
  }

  // Vibration — not its own sensor: derived from the accelerometer stream above, so
  // presence just tracks accel. What's worth checking is that windows are actually
  // closing at the expected 5 Hz and that at-rest RMS is small (a high floor here
  // usually means the phone is being handled/jostled, not that anything's broken).
  if (aN === 0) {
    out.push({ channel: 'vib', derivedFrom: 'accel', status: 'fail', detail: 'no accel data — derived channel unavailable' });
  } else {
    const expectedWindows = Math.floor(ms / 200);
    const gotWindows = vibWindows.length;
    const meanRms = gotWindows > 0 ? vibWindows.reduce((a, w) => a + w.rms, 0) / gotWindows : NaN;
    const sane = Number.isFinite(meanRms) && meanRms < 0.05;
    out.push({
      channel: 'vib',
      derivedFrom: 'accel',
      status: gotWindows >= expectedWindows - 1 && sane ? 'ok' : 'warn',
      detail: `${gotWindows}/${expectedWindows} windows · rest RMS ${meanRms.toFixed(3)} g${sane ? '' : ' — expect ≈0 at rest'}`,
    });
  }

  // Magnetometer — present, ~25 Hz, magnitude 25–65 µT (Earth's field).
  if (mN === 0) {
    out.push({ channel: 'mag', status: 'fail', detail: 'no data' });
  } else {
    const rate = mN / secs;
    const sane = mMag >= 20 && mMag <= 70;
    out.push({
      channel: 'mag',
      status: rate >= 12 && sane ? 'ok' : 'warn',
      detail: `${rate.toFixed(0)} Hz · |B| ${mMag.toFixed(0)} µT${sane ? '' : ' — expect 25–65'}`,
    });
  }

  // Barometer — present, pressure 300–1100 hPa.
  if (pN === 0) {
    out.push({ channel: 'baro', status: 'fail', detail: 'no data / no barometer on this device' });
  } else {
    const sane = pLast >= 300 && pLast <= 1100;
    out.push({
      channel: 'baro',
      status: sane ? 'ok' : 'warn',
      detail: `${pLast.toFixed(1)} hPa${sane ? '' : ' — out of range'}`,
    });
  }

  // Native channels — presence only here (Expo Go can't load them).
  out.push({
    channel: 'light',
    status: opts.hasLight ? 'ok' : 'warn',
    detail: opts.hasLight ? 'native module present' : 'dev build only (Expo Go)',
  });
  out.push({
    channel: 'mic',
    status: opts.hasMic ? 'ok' : 'warn',
    detail: opts.hasMic ? 'native module present' : 'dev build only (Expo Go)',
  });

  return out;
}
