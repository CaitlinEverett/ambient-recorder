package expo.modules.covariatemic

import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

/**
 * Stub — Android mic-level capture (e.g. via AudioRecord, computing RMS
 * in-memory the same way the iOS AVAudioEngine tap does) has not been
 * ported yet. Reports unavailable rather than crashing on a missing native
 * method. Flagging as an open item: unclear whether the cross-device
 * reliability study needs Android parity here or is iPhone-only — worth
 * confirming before this ships, since it's a real scope decision, not
 * just an implementation detail.
 */
class CovariateMicModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("CovariateMic")

    Events("onSample")

    AsyncFunction("requestPermissionsAsync") {
      mapOf("granted" to false, "status" to "unavailable")
    }

    AsyncFunction("start") {
      throw Exception("Mic-level sensing is not implemented on Android in this module yet.")
    }

    Function("stop") {
      // no-op
    }
  }
}
