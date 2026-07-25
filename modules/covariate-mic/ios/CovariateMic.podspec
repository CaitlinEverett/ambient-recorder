Pod::Spec.new do |s|
  s.name           = 'CovariateMic'
  s.version        = '1.0.0'
  s.summary        = 'A sample project summary'
  s.description    = 'A sample project description'
  s.author         = ''
  s.homepage       = 'https://docs.expo.dev/modules/'
  # Must be <= the app's deployment target (Expo SDK 54 default is iOS 15.1,
  # matching ExpoModulesCore). Expo's autolinking SILENTLY SKIPS any pod whose
  # platform requirement exceeds the app target — see
  # expo-modules-autolinking/scripts/ios/autolinking_manager.rb ("Skip if the
  # podspec doesn't include the platform for the current target"). That produces
  # a build that succeeds with the module missing at runtime, which is exactly
  # what the 16.4 left over from the module template caused here. Nothing in
  # CovariateMicModule.swift needs 16.4 (AVAudioEngine long predates it).
  s.platforms      = {
    :ios => '15.1',
    :tvos => '15.1'
  }
  s.source         = { git: '' }
  s.static_framework = true

  s.dependency 'ExpoModulesCore'

  # Swift/Objective-C compatibility
  s.pod_target_xcconfig = {
    'DEFINES_MODULE' => 'YES',
  }

  s.source_files = "**/*.{h,m,mm,swift,hpp,cpp}"
end
