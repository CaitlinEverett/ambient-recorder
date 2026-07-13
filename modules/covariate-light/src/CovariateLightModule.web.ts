import { registerWebModule, NativeModule } from 'expo';

// CovariateLightModule is not available on the web platform.
class CovariateLightModule extends NativeModule<{}> {}

export default registerWebModule(CovariateLightModule, 'CovariateLightModule');
