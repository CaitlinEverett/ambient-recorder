// Vibration meter — derives a "vibration level" channel from raw accelerometer
// samples. Gravity (and slow orientation drift) is estimated with a low-pass
// filter and subtracted out; what's left is the fast/dynamic component, which
// gets summarized as an RMS + peak reading over a short rolling window. This
// is the same trick most phone "vibrometer" apps use — not a calibrated
// instrument, but a reasonable stand-in per the proposal's commodity-sensor framing.
//
// Usage: feed every raw accelerometer sample through push(x, y, z). When a
// window closes, push() returns a VibrationSample — ingest that into the
// recorder as the 'vibration' channel, values: [rms, peak]. Timing is
// self-contained (own monotonic clock), so no need to pass the recorder's
// session-relative t through — the window boundary is independent of it.

export interface VibrationSample {
  rms: number; // RMS magnitude of gravity-removed acceleration over the window, g
  peak: number; // peak magnitude in the window, g
  n: number; // raw accel samples that went into this window
}

// Low-pass coefficient for the gravity estimate. Closer to 1 = slower to
// track orientation changes = more of the real signal leaks into "gravity"
// and gets removed. At accel ~50 Hz this cutoff sits comfortably below
// typical hand/vibration frequencies (a few Hz and up).
const GRAVITY_ALPHA = 0.9;

function monotonicMs(): number {
  const p = (globalThis as any).performance;
  return typeof p?.now === 'function' ? p.now() : Date.now();
}

export class VibrationMeter {
  private readonly windowMs: number;
  private gx = 0;
  private gy = 0;
  private gz = 0;
  private initialized = false;
  private sumSq = 0;
  private peak = 0;
  private n = 0;
  private windowStart: number | null = null;

  constructor(windowMs = 200) {
    this.windowMs = windowMs;
  }

  /** Feed one raw accelerometer sample (x/y/z in g). */
  push(x: number, y: number, z: number): VibrationSample | null {
    const t = monotonicMs();
    if (!this.initialized) {
      this.gx = x;
      this.gy = y;
      this.gz = z;
      this.initialized = true;
      this.windowStart = t;
      return null;
    }

    this.gx = GRAVITY_ALPHA * this.gx + (1 - GRAVITY_ALPHA) * x;
    this.gy = GRAVITY_ALPHA * this.gy + (1 - GRAVITY_ALPHA) * y;
    this.gz = GRAVITY_ALPHA * this.gz + (1 - GRAVITY_ALPHA) * z;

    const dx = x - this.gx;
    const dy = y - this.gy;
    const dz = z - this.gz;
    const mag = Math.sqrt(dx * dx + dy * dy + dz * dz);

    this.sumSq += mag * mag;
    this.peak = Math.max(this.peak, mag);
    this.n++;

    if (this.windowStart === null) this.windowStart = t;

    if (t - this.windowStart >= this.windowMs) {
      const out: VibrationSample = {
        rms: this.n > 0 ? Math.sqrt(this.sumSq / this.n) : 0,
        peak: this.peak,
        n: this.n,
      };
      this.sumSq = 0;
      this.peak = 0;
      this.n = 0;
      this.windowStart = t;
      return out;
    }
    return null;
  }
}
