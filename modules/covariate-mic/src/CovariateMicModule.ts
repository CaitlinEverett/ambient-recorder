import { NativeModule, requireOptionalNativeModule } from 'expo';
import type { CovariateMicModuleEvents } from './CovariateMic.types';

declare class CovariateMicModule extends NativeModule<CovariateMicModuleEvents> {
  /** Prompts for microphone permission if not yet determined (iOS only; always unavailable on Android). */
  requestPermissionsAsync(): Promise<{ granted: boolean; status: string }>;
  /** Starts the AVAudioEngine tap. Samples arrive via the 'onSample' event, not a return value. Never writes an audio file. */
  start(): Promise<void>;
  stop(): void;
}

// Optional so the app still loads in Expo Go (module absent -> null); the dev
// client provides the real native module. Callers must null-check.
export default requireOptionalNativeModule<CovariateMicModule>('CovariateMic');
