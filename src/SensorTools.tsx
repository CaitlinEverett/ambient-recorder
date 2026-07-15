import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { runHealthCheck, ChannelCheck } from './health';
import { runCalibration, saveBaseline, Baseline } from './calibrate';
import { CHANNEL_BY_ID, describeDerivation } from './channels';
import CovariateLightModule from '../modules/covariate-light/src/CovariateLightModule';
import CovariateMicModule from '../modules/covariate-mic/src/CovariateMicModule';

// Device-level sensor tools — a pre-flight health check and an at-rest baseline
// calibration. Self-contained (owns its own state) so it can live on both the
// Home screen and the record screen.

const ACCENT = '#4fb3c4';
const hasLight = CovariateLightModule != null;
const hasMic = CovariateMicModule != null;

export default function SensorTools({ experimentID = 'device' }: { experimentID?: string }) {
  const [checking, setChecking] = useState(false);
  const [healthChecks, setHealthChecks] = useState<ChannelCheck[] | null>(null);
  const [calibrating, setCalibrating] = useState(false);
  const [calibRemaining, setCalibRemaining] = useState(0);
  const [baseline, setBaseline] = useState<Baseline | null>(null);

  async function runCheck() {
    setChecking(true);
    try {
      setHealthChecks(await runHealthCheck({ hasLight, hasMic }));
    } finally {
      setChecking(false);
    }
  }

  async function runCalibrate() {
    setBaseline(null);
    setCalibrating(true);
    const secs = 20;
    setCalibRemaining(secs);
    const iv = setInterval(() => setCalibRemaining((r) => Math.max(0, r - 1)), 1000);
    try {
      const b = await runCalibration({ seconds: secs, experimentID: experimentID.trim() || 'device' });
      await saveBaseline(b);
      setBaseline(b);
    } finally {
      clearInterval(iv);
      setCalibrating(false);
    }
  }

  return (
    <View style={styles.wrap}>
      <Pressable onPress={runCheck} disabled={checking} style={styles.btn}>
        <Text style={styles.btnText}>{checking ? 'checking sensors…' : '🔍 Check sensors'}</Text>
      </Pressable>
      {healthChecks && (
        <View style={styles.panel}>
          {healthChecks.map((h) => {
            const def = CHANNEL_BY_ID[h.channel];
            const derived = def?.kind === 'derived';
            const method = def ? describeDerivation(def) : null;
            return (
              <View key={h.channel} style={[styles.row, derived && styles.derivedRow]}>
                {derived ? (
                  <Text style={styles.derivedArrow}>↳</Text>
                ) : (
                  <Text style={[styles.dot, { color: h.status === 'ok' ? '#7fd8b0' : h.status === 'warn' ? '#e0b070' : '#e08a7a' }]}>●</Text>
                )}
                <View style={styles.rowBody}>
                  <View style={styles.rowLine}>
                    <Text style={[styles.ch, derived && styles.chDerived]}>{def?.label ?? h.channel}</Text>
                    <Text style={styles.detail}>{h.detail}</Text>
                  </View>
                  {method && <Text style={styles.method}>{method}</Text>}
                </View>
              </View>
            );
          })}
        </View>
      )}
      <Pressable onPress={runCalibrate} disabled={calibrating} style={styles.btn}>
        <Text style={styles.btnText}>
          {calibrating ? `calibrating… hold still · ${calibRemaining}s` : '⚖ Calibrate baseline (20 s at rest)'}
        </Text>
      </Pressable>
      {baseline && (
        <View style={styles.panel}>
          {baseline.channels.map((b) => {
            const def = CHANNEL_BY_ID[b.channel];
            const derived = def?.kind === 'derived';
            const unit = def?.unit ?? '';
            const md = def?.decimals ?? 3;
            const method = def ? describeDerivation(def) : null;
            return (
              <View key={b.channel} style={[styles.row, derived && styles.derivedRow]}>
                {derived && <Text style={styles.derivedArrow}>↳</Text>}
                <View style={styles.rowBody}>
                  <View style={styles.rowLine}>
                    <Text style={[styles.ch, derived && styles.chDerived]}>{def?.label ?? b.channel}</Text>
                    <Text style={styles.detail}>
                      bias {Number.isFinite(b.mean) ? b.mean.toFixed(md) : '—'} {unit} · noise ±{Number.isFinite(b.noiseFloor) ? b.noiseFloor.toFixed(4) : '—'}
                    </Text>
                  </View>
                  {method && <Text style={styles.method}>{method}</Text>}
                </View>
              </View>
            );
          })}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 8 },
  btn: { paddingVertical: 11, borderRadius: 10, borderWidth: 1, borderColor: '#23262d', alignItems: 'center', backgroundColor: '#161a1f' },
  btnText: { color: ACCENT, fontSize: 14, fontWeight: '600' },
  panel: { backgroundColor: '#161a1f', borderRadius: 12, borderWidth: 1, borderColor: '#23262d', paddingVertical: 4 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 7, paddingHorizontal: 12 },
  derivedRow: { paddingLeft: 26, paddingVertical: 5 },
  dot: { fontSize: 12 },
  derivedArrow: { width: 12, color: '#5b616e', fontSize: 12 },
  rowBody: { flex: 1 },
  rowLine: { flexDirection: 'row', alignItems: 'baseline', gap: 8 },
  ch: { width: 46, color: '#e9ebf0', fontSize: 13, fontWeight: '600', fontFamily: 'Menlo' },
  chDerived: { color: '#9aa1ad', fontWeight: '500' },
  detail: { flex: 1, color: '#9aa1ad', fontSize: 12.5 },
  method: { color: '#5b616e', fontSize: 10.5, fontStyle: 'italic', marginTop: 2 },
});
