import { NativeModule, requireNativeModule } from 'expo';
import type { CovariateMicModuleEvents } from './CovariateMic.types';

declare class CovariateMicModule extends NativeModule<CovariateMicModuleEvents> {
  /** Prompts for microphone permission if not yet determined (iOS only; always unavailable on Android). */
  requestPermissionsAsync(): Promise<{ granted: boolean; status: string }>;
  /** Starts the AVAudioEngine tap. Samples arrive via the 'onSample' event, not a return value. Never writes an audio file. */
  start(): Promise<void>;
  stop(): void;
}

export default requireNativeModule<CovariateMicModule>('CovariateMic');
