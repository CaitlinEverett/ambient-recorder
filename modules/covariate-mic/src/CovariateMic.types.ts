export type MicSampleEvent = {
  /**
   * Seconds on an arbitrary per-device monotonic clock (native
   * CACurrentMediaTime), NOT a Unix/Date.now() epoch. Same caveat as
   * CovariateLight's LightSampleEvent.t — not yet reconciled with the
   * JS-side session clock.
   */
  t: number;
  /** RMS sound level in dBFS (0 dBFS = full scale; typical quiet room ~ -50 to -40). */
  dBFS: number;
};

export type CovariateMicModuleEvents = {
  onSample: (event: MicSampleEvent) => void;
};
