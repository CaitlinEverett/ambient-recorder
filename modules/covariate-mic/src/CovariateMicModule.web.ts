import { registerWebModule, NativeModule } from 'expo';

// CovariateMicModule is not available on the web platform.
class CovariateMicModule extends NativeModule<{}> {}

export default registerWebModule(CovariateMicModule, 'CovariateMicModule');
