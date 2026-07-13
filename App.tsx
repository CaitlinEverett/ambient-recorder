import { useEffect, useRef, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Accelerometer, Barometer, Magnetometer } from 'expo-sensors';
import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake';
import CovariateLightModule from './modules/covariate-light/src/CovariateLightModule';
import CovariateMicModule from './modules/covariate-mic/src/CovariateMicModule';
import { useEventListener } from 'expo';

// Covariate MVP — proves the sensor loop on a phone via a custom Dev Client
// (SDK 54). Reads accelerometer, magnetometer, barometer, ambient light, and
// mic level live and tracks per-channel sample counts over a timed session.
// Light and mic level come from two small local native modules
// (modules/covariate-light, modules/covariate-mic) since Expo Go can't load
// custom native code — accel/mag/baro stay on expo-sensors. BLE (external
// module) is still not wired up.

type Vec = { x: number; y: number; z: number };
const ACCENT = '#4fb3c4';
const fmt = (n: number, d = 2) => (Number.isFinite(n) ? n.toFixed(d) : '—');

export default function App() {
  const [recording, setRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [accel, setAccel] = useState<Vec>({ x: 0, y: 0, z: 0 });
  const [mag, setMag] = useState<Vec>({ x: 0, y: 0, z: 0 });
  const [pressure, setPressure] = useState<number>(NaN);
  const [altitude, setAltitude] = useState<number>(NaN);
  const [baroOk, setBaroOk] = useState<boolean | null>(null);
  const [brightness, setBrightness] = useState<number>(NaN);
  const [lightOk, setLightOk] = useState<boolean | null>(null);
  const [dBFS, setDBFS] = useState<number>(NaN);
  const [micOk, setMicOk] = useState<boolean | null>(null);
  const [counts, setCounts] = useState({ accel: 0, mag: 0, baro: 0, light: 0, mic: 0 });

  const subs = useRef<{ remove: () => void }[]>([]);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const c = useRef({ accel: 0, mag: 0, baro: 0, light: 0, mic: 0 });

  useEffect(() => {
    Barometer.isAvailableAsync().then(setBaroOk).catch(() => setBaroOk(false));
    CovariateLightModule.isAvailable().then(setLightOk).catch(() => setLightOk(false));
    return () => { stop(); };
  }, []);

  // Native modules deliver samples as events, not addListener() subscriptions
  // like expo-sensors — wire them with useEventListener instead of pushing
  // onto `subs`. Guarding on `recording` keeps counts from ticking while idle.
  useEventListener(CovariateLightModule, 'onSample', (event) => {
    if (!recording) return;
    c.current.light++;
    setBrightness(event.brightnessValue);
  });

  useEventListener(CovariateMicModule, 'onSample', (event) => {
    if (!recording) return;
    c.current.mic++;
    setDBFS(event.dBFS);
  });

  async function start() {
    c.current = { accel: 0, mag: 0, baro: 0, light: 0, mic: 0 };
    setCounts({ ...c.current });
    setElapsed(0);

    try { await Accelerometer.requestPermissionsAsync(); } catch {}
    Accelerometer.setUpdateInterval(20); // ~50 Hz
    Magnetometer.setUpdateInterval(40);  // ~25 Hz

    subs.current = [
      Accelerometer.addListener((d) => { c.current.accel++; setAccel(d); }),
      Magnetometer.addListener((d) => { c.current.mag++; setMag(d); }),
      Barometer.addListener((d: any) => {
        c.current.baro++;
        setPressure(d.pressure);
        if (typeof d.relativeAltitude === 'number') setAltitude(d.relativeAltitude);
      }),
    ];

    if (lightOk) {
      try {
        const perm = await CovariateLightModule.requestPermissionsAsync();
        if (perm.granted) await CovariateLightModule.start();
        else setLightOk(false);
      } catch { setLightOk(false); }
    }

    if (micOk !== false) {
      try {
        const perm = await CovariateMicModule.requestPermissionsAsync();
        if (perm.granted) { await CovariateMicModule.start(); setMicOk(true); }
        else setMicOk(false);
      } catch { setMicOk(false); }
    }

    timer.current = setInterval(() => {
      setElapsed((e) => e + 1);
      setCounts({ ...c.current });
    }, 1000);

    await activateKeepAwakeAsync();
    setRecording(true);
  }

  async function stop() {
    subs.current.forEach((s) => s.remove());
    subs.current = [];
    if (timer.current) { clearInterval(timer.current); timer.current = null; }
    CovariateLightModule.stop();
    CovariateMicModule.stop();
    deactivateKeepAwake();
    setRecording(false);
  }

  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');
  const rate = (n: number) => (elapsed > 0 ? `${(n / elapsed).toFixed(0)} Hz` : '—');

  const rows: [string, string, string, number][] = [
    ['accel', `${fmt(accel.x)}  ${fmt(accel.y)}  ${fmt(accel.z)}`, 'g', counts.accel],
    ['mag', `${fmt(mag.x, 1)}  ${fmt(mag.y, 1)}  ${fmt(mag.z, 1)}`, 'µT', counts.mag],
    ['baro', baroOk === false ? 'unavailable' : `${fmt(pressure, 2)}  ·  Δalt ${fmt(altitude, 1)}m`, 'hPa', counts.baro],
    ['light', lightOk === false ? 'unavailable' : fmt(brightness, 2), 'EV', counts.light],
    ['mic', micOk === false ? 'unavailable' : fmt(dBFS, 1), 'dBFS', counts.mic],
  ];

  return (
    <View style={styles.app}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.brand}>Co<Text style={{ color: ACCENT }}>variate</Text></Text>
        <Text style={styles.subtitle}>sensor MVP · dev client</Text>

        <View style={styles.timerBox}>
          <Text style={styles.timer}>{mm}:{ss}</Text>
          <Text style={styles.timerLabel}>{recording ? '● recording' : 'idle'}</Text>
        </View>

        <View style={styles.table}>
          <View style={[styles.row, styles.head]}>
            <Text style={[styles.ch, styles.dim]}>ch</Text>
            <Text style={[styles.val, styles.dim]}>value</Text>
            <Text style={[styles.n, styles.dim]}>n / rate</Text>
          </View>
          {rows.map(([ch, val, unit, n]) => (
            <View key={ch} style={styles.row}>
              <Text style={styles.ch}>{ch}</Text>
              <View style={styles.val}>
                <Text style={styles.valText}>{val}</Text>
                <Text style={styles.unit}>{unit}</Text>
              </View>
              <View style={styles.n}>
                <Text style={styles.nText}>{n}</Text>
                <Text style={styles.unit}>{rate(n)}</Text>
              </View>
            </View>
          ))}
        </View>

        <Pressable
          onPress={recording ? stop : start}
          style={[styles.btn, { backgroundColor: recording ? '#c0392b' : ACCENT }]}
        >
          <Text style={styles.btnText}>{recording ? '■  Stop' : '▶  Start recording'}</Text>
        </Pressable>

        <Text style={styles.foot}>
          accel · mag · barometer · light · mic level, all live. Disk export and
          BLE still need building — that's what's left before a real session.
        </Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: '#0e1013' },
  scroll: { padding: 22, paddingTop: 72, gap: 18 },
  brand: { color: '#e9ebf0', fontSize: 30, fontWeight: '800', letterSpacing: -0.5 },
  subtitle: { color: '#9aa1ad', fontSize: 13, marginTop: -10, letterSpacing: 0.4 },
  timerBox: { alignItems: 'center', paddingVertical: 18 },
  timer: { color: '#e9ebf0', fontSize: 56, fontWeight: '700', fontVariant: ['tabular-nums'] },
  timerLabel: { color: '#9aa1ad', fontSize: 13, marginTop: 2 },
  table: { backgroundColor: '#161a1f', borderRadius: 14, padding: 6, borderWidth: 1, borderColor: '#23262d' },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 12, gap: 8 },
  head: { paddingVertical: 8 },
  dim: { color: '#5b616e', fontSize: 12 },
  ch: { width: 52, color: '#e9ebf0', fontSize: 15, fontWeight: '600', fontFamily: 'Menlo' },
  val: { flex: 1, flexDirection: 'row', alignItems: 'baseline', gap: 6 },
  valText: { color: '#e9ebf0', fontSize: 15, fontFamily: 'Menlo', fontVariant: ['tabular-nums'] },
  unit: { color: '#5b616e', fontSize: 11 },
  n: { width: 88, flexDirection: 'row', alignItems: 'baseline', justifyContent: 'flex-end', gap: 6 },
  nText: { color: '#e9ebf0', fontSize: 14, fontFamily: 'Menlo', fontVariant: ['tabular-nums'] },
  btn: { borderRadius: 12, paddingVertical: 16, alignItems: 'center' },
  btnText: { color: '#08121a', fontSize: 17, fontWeight: '700' },
  foot: { color: '#5b616e', fontSize: 12.5, lineHeight: 18, textAlign: 'center', paddingHorizontal: 10 },
});
