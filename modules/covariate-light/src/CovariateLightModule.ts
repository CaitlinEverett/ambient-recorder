import { NativeModule, requireNativeModule } from 'expo';
import type { CovariateLightModuleEvents } from './CovariateLight.types';

declare class CovariateLightModule extends NativeModule<CovariateLightModuleEvents> {
  /** True if a back camera is available to derive brightness from. */
  isAvailable(): Promise<boolean>;
  /** Prompts for camera permission if not yet determined (iOS only; always unavailable on Android). */
  requestPermissionsAsync(): Promise<{ granted: boolean; status: string }>;
  /** Starts the capture session. Samples arrive via the 'onSample' event, not a return value. */
  start(): Promise<void>;
  stop(): void;
}

export default requireNativeModule<CovariateLightModule>('CovariateLight');
