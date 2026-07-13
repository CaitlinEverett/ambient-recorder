import { NativeModule, requireNativeModule } from 'expo';

declare class CovariateLightModule extends NativeModule<{}> {}

export default requireNativeModule<CovariateLightModule>('CovariateLight');
