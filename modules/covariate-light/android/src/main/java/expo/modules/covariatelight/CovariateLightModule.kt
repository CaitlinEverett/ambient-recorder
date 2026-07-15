package expo.modules.covariatelight

import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

/**
 * Ambient light sensing on Android is out of scope for this module — the
 * proposal's implementation approach (EXIF BrightnessValue read from an
 * AVCaptureVideoDataOutput session) is iOS/AVFoundation-specific. This stub
 * reports the feature as unavailable so JS call sites degrade the same way
 * they already do for barometer-unavailable devices, instead of hitting a
 * native "method not found" error.
 */
class CovariateLightModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("CovariateLight")

    Events("onSample")

    AsyncFunction("isAvailable") {
      false
    }

    AsyncFunction("requestPermissionsAsync") {
      mapOf("granted" to false, "status" to "unavailable")
    }

    AsyncFunction("start") {
      throw Exception("Ambient light sensing is not implemented on Android in this module.")
    }

    Function("stop") {
      // no-op
    }
  }
}
