import { useEffect, useRef, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Accelerometer, Barometer, Magnetometer } from 'expo-sensors';
import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake';
import CovariateLightModule from './modules/covariate-light/src/CovariateLightModule';
import CovariateMicModule from './modules/covariate-mic/src/CovariateMicModule';

// Covariate MVP — runs in BOTH Expo Go and a custom dev client (SDK 54).
// accel/mag/baro use expo-sensors (work everywhere). Ambient light + mic level
// use two local native modules (modules/covariate-light, covariate-mic) that
// only load in a dev client — in Expo Go they resolve to null and their rows
// show "dev build". Build the dev client to light them up. BLE: not wired yet.

type Vec = { x: number; y: number; z: number };
const ACCENT = '#4fb3c4';
const fmt = (n: number, d = 2) => (Number.isFinite(n) ? n.toFixed(d) : '—');
const hasLight = CovariateLightModule != null;
const hasMic = CovariateMicModule != null;

export default function App() {
  const [recording, setRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [accel, setAccel] = useState<Vec>({ x: 0, y: 0, z: 0 });
  const [mag, setMag] = useState<Vec>({ x: 0, y: 0, z: 0 });
  const [pressure, setPressure] = useState<number>(NaN);
  const [altitude, setAltitude] = useState<number>(NaN);
  const [baroOk, setBaroOk] = useState<boolean | null>(null);
  const [brightness, setBrightness] = useState<number>(NaN);
  const [lightOk, setLightOk] = useState<boolean | null>(hasLight ? null : false);
  const [dBFS, setDBFS] = useState<number>(NaN);
  const [micOk, setMicOk] = useState<boolean | null>(hasMic ? null : false);
  const [counts, setCounts] = useState({ accel: 0, mag: 0, baro: 0, light: 0, mic: 0 });

  const subs = useRef<{ remove: () => void }[]>([]);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const c = useRef({ accel: 0, mag: 0, baro: 0, light: 0, mic: 0 });

  useEffect(() => {
    Barometer.isAvailableAsync().then(setBaroOk).catch(() => setBaroOk(false));
    if (CovariateLightModule) {
      CovariateLightModule.isAvailable().then(setLightOk).catch(() => setLightOk(false));
    }
    return () => { stop(); };
  }, []);

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

    // Native modules — dev client only. In Expo Go these are null and skipped.
    if (CovariateLightModule) {
      try {
        const perm = await CovariateLightModule.requestPermissionsAsync();
        if (perm.granted) {
          subs.current.push(CovariateLightModule.addListener('onSample', (e: any) => {
            c.current.light++; setBrightness(e.brightnessValue);
          }));
          await CovariateLightModule.start();
          setLightOk(true);
        } else setLightOk(false);
      } catch { setLightOk(false); }
    }

    if (CovariateMicModule) {
      try {
        const perm = await CovariateMicModule.requestPermissionsAsync();
        if (perm.granted) {
          subs.current.push(CovariateMicModule.addListener('onSample', (e: any) => {
            c.current.mic++; setDBFS(e.dBFS);
          }));
          await CovariateMicModule.start();
          setMicOk(true);
        } else setMicOk(false);
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
    CovariateLightModule?.stop();
    CovariateMicModule?.stop();
    deactivateKeepAwake();
    setRecording(false);
  }

  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');
  const rate = (n: number) => (elapsed > 0 ? `${(n / elapsed).toFixed(0)} Hz` : '—');

  // Native-channel display: "dev build" if the module isn't in this runtime
  // (Expo Go), otherwise the live value (or "unavailable" if permission denied).
  const nativeVal = (has: boolean, ok: boolean | null, live: string) =>
    !has ? 'dev build' : ok === false ? 'unavailable' : live;

  const rows: [string, string, string, number][] = [
    ['accel', `${fmt(accel.x)}  ${fmt(accel.y)}  ${fmt(accel.z)}`, 'g', counts.accel],
    ['mag', `${fmt(mag.x, 1)}  ${fmt(mag.y, 1)}  ${fmt(mag.z, 1)}`, 'µT', counts.mag],
    ['baro', baroOk === false ? 'unavailable' : `${fmt(pressure, 2)}  ·  Δalt ${fmt(altitude, 1)}m`, 'hPa', counts.baro],
    ['light', nativeVal(hasLight, lightOk, fmt(brightness, 2)), 'EV', counts.light],
    ['mic', nativeVal(hasMic, micOk, fmt(dBFS, 1)), 'dBFS', counts.mic],
  ];

  return (
    <View style={styles.app}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.brand}>Co<Text style={{ color: ACCENT }}>variate</Text></Text>
        <Text style={styles.subtitle}>
          sensor MVP · {hasLight && hasMic ? 'dev client · 5 channels' : 'Expo Go · 3 live'}
        </Text>

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
          {hasLight && hasMic
            ? 'accel · mag · barometer · light · mic level, all live. Disk export and BLE still to build.'
            : 'accel · mag · barometer are live now. light + mic need the dev-client build (their native modules) — that’s the next handoff.'}
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
