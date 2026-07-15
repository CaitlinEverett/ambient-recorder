export type LightSampleEvent = {
  /**
   * Seconds on an arbitrary per-device monotonic clock (native
   * CACurrentMediaTime), NOT a Unix/Date.now() epoch. Not yet reconciled
   * with the JS-side session clock — the App.tsx session/export layer that
   * would do that doesn't exist yet.
   */
  t: number;
  /**
   * Raw EXIF BrightnessValue (~log2 luminance, unitless) — same value and
   * units as the native ambient-recorder prototype's LightChannel.
   */
  brightnessValue: number;
};

export type CovariateLightModuleEvents = {
  onSample: (event: LightSampleEvent) => void;
};
