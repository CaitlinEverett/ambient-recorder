import { useEffect, useRef, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Accelerometer, Barometer, Magnetometer } from 'expo-sensors';
import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake';
import CovariateLightModule from './modules/covariate-light/src/CovariateLightModule';
import CovariateMicModule from './modules/covariate-mic/src/CovariateMicModule';
import { SessionRecorder, exportRecord, shareSession } from './src/recorder';
import { VibrationMeter } from './src/vibration';
import { getCoarseLocation } from './src/location';
import { LocationFix } from './src/schema';
import HomeScreen from './src/HomeScreen';
import { Experiment, createExperiment, listExperiments } from './src/experiments';
import { SavedSession, listSessions } from './src/sessions';
import SensorTools from './src/SensorTools';
import Accordion from './src/Accordion';

// Covariate MVP — runs in Expo Go (accel/mag/baro) or a dev client (all 5).
// Home lists experiments + sessions + device sensor tools; the record screen
// (this component) records a session and exports schema-v0.1.1 JSON.

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
  const [vibRms, setVibRms] = useState<number>(NaN);
  const [counts, setCounts] = useState({ accel: 0, mag: 0, baro: 0, light: 0, mic: 0, vibration: 0 });

  // Session metadata (schema meta).
  const [experimentID, setExperimentID] = useState('');
  const [condition, setCondition] = useState<'controlled' | 'disturbed'>('controlled');
  const [site, setSite] = useState('');
  const [notes, setNotes] = useState('');
  const [locationOn, setLocationOn] = useState(false);

  const [exporting, setExporting] = useState(false);
  const [lastExport, setLastExport] = useState<{ id: string; name: string; count: number } | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);
  const [screen, setScreen] = useState<'home' | 'record'>('home');
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [sessions, setSessions] = useState<SavedSession[]>([]);

  const subs = useRef<{ remove: () => void }[]>([]);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const c = useRef({ accel: 0, mag: 0, baro: 0, light: 0, mic: 0, vibration: 0 });
  const rec = useRef(new SessionRecorder());
  const vibMeter = useRef<VibrationMeter | null>(null);
  const locationRef = useRef<LocationFix | null>(null);

  useEffect(() => {
    Barometer.isAvailableAsync().then(setBaroOk).catch(() => setBaroOk(false));
    if (CovariateLightModule) {
      CovariateLightModule.isAvailable().then(setLightOk).catch(() => setLightOk(false));
    }
    refreshHome();
    return () => { stopSensors(); };
  }, []);

  async function start() {
    c.current = { accel: 0, mag: 0, baro: 0, light: 0, mic: 0, vibration: 0 };
    setCounts({ ...c.current });
    setElapsed(0);
    setLastExport(null);
    setExportError(null);
    rec.current.start();
    vibMeter.current = new VibrationMeter(200); // 200ms window -> matches NOMINAL_RATE.vibration (5 Hz)
    // Capture location in the BACKGROUND — never block sensor start on the GPS fix.
    locationRef.current = null;
    if (locationOn) {
      getCoarseLocation()
        .then((fix) => { locationRef.current = fix; })
        .catch(() => { locationRef.current = null; });
    }

    try { await Accelerometer.requestPermissionsAsync(); } catch {}
    Accelerometer.setUpdateInterval(20); // ~50 Hz
    Magnetometer.setUpdateInterval(40);  // ~25 Hz

    subs.current = [
      Accelerometer.addListener((d) => {
        c.current.accel++; setAccel(d); rec.current.ingest('accelerometer', [d.x, d.y, d.z]);
        const v = vibMeter.current?.push(d.x, d.y, d.z);
        if (v) {
          c.current.vibration++; setVibRms(v.rms);
          rec.current.ingest('vibration', [v.rms, v.peak]);
        }
      }),
      Magnetometer.addListener((d) => {
        c.current.mag++; setMag(d); rec.current.ingest('magnetometer', [d.x, d.y, d.z]);
      }),
      Barometer.addListener((d: any) => {
        c.current.baro++;
        setPressure(d.pressure);
        const alt = typeof d.relativeAltitude === 'number' ? d.relativeAltitude : 0;
        if (typeof d.relativeAltitude === 'number') setAltitude(d.relativeAltitude);
        rec.current.ingest('barometer', [d.pressure, alt]);
      }),
    ];

    // Native modules — dev client only. In Expo Go these are null and skipped.
    if (CovariateLightModule) {
      try {
        const perm = await CovariateLightModule.requestPermissionsAsync();
        if (perm.granted) {
          subs.current.push(CovariateLightModule.addListener('onSample', (e: any) => {
            c.current.light++; setBrightness(e.brightnessValue); rec.current.ingest('light', [e.brightnessValue]);
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
            c.current.mic++; setDBFS(e.dBFS); rec.current.ingest('micLevel', [e.dBFS]);
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

  function stopSensors() {
    subs.current.forEach((s) => s.remove());
    subs.current = [];
    if (timer.current) { clearInterval(timer.current); timer.current = null; }
    CovariateLightModule?.stop();
    CovariateMicModule?.stop();
    deactivateKeepAwake();
    setRecording(false);
  }

  async function stopAndExport() {
    stopSensors();
    const record = rec.current.build({ experimentID: experimentID.trim(), condition, site: site.trim(), notes: notes.trim(), location: locationRef.current });
    setExporting(true);
    try {
      const { id, name } = await exportRecord(record);
      setLastExport({ id, name, count: record.samples.length });
      refreshHome();
    } catch (e) {
      setExportError(e instanceof Error ? e.message : String(e));
    } finally {
      setExporting(false);
    }
  }

  function clearAll() {
    // Fresh session under the SAME experiment — keeps experimentID.
    setCondition('controlled'); setSite(''); setNotes(''); setLocationOn(false);
    setLastExport(null); setExportError(null);
    setElapsed(0); setCounts({ accel: 0, mag: 0, baro: 0, light: 0, mic: 0, vibration: 0 });
    setAccel({ x: 0, y: 0, z: 0 }); setMag({ x: 0, y: 0, z: 0 });
    setPressure(NaN); setAltitude(NaN); setBrightness(NaN); setDBFS(NaN); setVibRms(NaN);
    rec.current = new SessionRecorder();
    vibMeter.current = null;
  }

  async function refreshHome() {
    setExperiments(await listExperiments());
    setSessions(await listSessions());
  }

  async function handleCreate(name: string) {
    const exp = await createExperiment(name);
    setExperiments((prev) => [exp, ...prev]);
    openExperiment(exp);
  }

  function openExperiment(exp: Experiment) {
    setExperimentID(exp.name);
    setLastExport(null);
    setExportError(null);
    setScreen('record');
  }

  function goHome() {
    if (recording) return;
    setScreen('home');
    refreshHome();
  }

  const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const ss = String(elapsed % 60).padStart(2, '0');
  const rate = (n: number) => (elapsed > 0 ? `${(n / elapsed).toFixed(0)} Hz` : '—');
  const nativeVal = (has: boolean, ok: boolean | null, live: string) =>
    !has ? 'dev build' : ok === false ? 'unavailable' : live;

  const rows: [string, string, string, number][] = [
    ['accel', `${fmt(accel.x)}  ${fmt(accel.y)}  ${fmt(accel.z)}`, 'g', counts.accel],
    ['mag', `${fmt(mag.x, 1)}  ${fmt(mag.y, 1)}  ${fmt(mag.z, 1)}`, 'µT', counts.mag],
    ['baro', baroOk === false ? 'unavailable' : `${fmt(pressure, 2)}  ·  Δalt ${fmt(altitude, 1)}m`, 'hPa', counts.baro],
    ['light', nativeVal(hasLight, lightOk, fmt(brightness, 2)), 'EV', counts.light],
    ['mic', nativeVal(hasMic, micOk, fmt(dBFS, 1)), 'dBFS', counts.mic],
    ['vib', fmt(vibRms, 3), 'g RMS', counts.vibration],
  ];

  const canStart = experimentID.trim().length > 0;

  if (screen === 'home') {
    return (
      <HomeScreen
        experiments={experiments}
        sessions={sessions}
        onCreate={handleCreate}
        onPick={openExperiment}
        onShare={(id, name) => shareSession(id, name)}
      />
    );
  }

  return (
    <View style={styles.app}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        {!recording && (
          <Pressable onPress={goHome} style={styles.homeBack}>
            <Text style={styles.homeBackText}>← Home</Text>
          </Pressable>
        )}
        <Text style={styles.brand}>Co<Text style={{ color: ACCENT }}>variate</Text></Text>
        <Text style={styles.subtitle}>
          {experimentID || 'session'} · {hasLight && hasMic ? 'dev client' : 'Expo Go'}
        </Text>

        <View style={styles.condRow}>
          {(['controlled', 'disturbed'] as const).map((cond) => (
            <Pressable key={cond} disabled={recording} onPress={() => setCondition(cond)}
              style={[styles.condBtn, condition === cond && styles.condOn]}>
              <Text style={[styles.condText, condition === cond && styles.condTextOn]}>{cond}</Text>
            </Pressable>
          ))}
        </View>

        {!recording && (
          <Accordion title="details — site · notes · location">
            <TextInput
              style={styles.input} value={site} onChangeText={setSite}
              placeholder="Site (e.g. chicago-kitchen)" placeholderTextColor="#5b616e"
              autoCapitalize="none" autoCorrect={false}
            />
            <TextInput
              style={styles.input} value={notes} onChangeText={setNotes}
              placeholder="Notes" placeholderTextColor="#5b616e"
            />
            <Pressable onPress={() => setLocationOn((v) => !v)}
              style={[styles.locBtn, locationOn && styles.condOn]}>
              <Text style={[styles.condText, locationOn && styles.condTextOn]}>
                📍 {locationOn ? 'location: region + altitude' : 'location: off (tap to enable)'}
              </Text>
            </Pressable>
          </Accordion>
        )}

        {!recording && (
          <Accordion title="sensor tools — check · calibrate">
            <SensorTools experimentID={experimentID} />
          </Accordion>
        )}

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
          onPress={recording ? stopAndExport : start}
          disabled={!recording && !canStart}
          style={[
            styles.btn,
            { backgroundColor: recording ? '#c0392b' : ACCENT },
            !recording && !canStart && styles.btnDisabled,
          ]}
        >
          <Text style={styles.btnText}>{recording ? '■  Stop & export' : '▶  Start recording'}</Text>
        </Pressable>

        {!recording && (
          <Pressable onPress={clearAll} style={styles.clearBtn}>
            <Text style={styles.clearBtnText}>↺  Start over</Text>
          </Pressable>
        )}

        {exporting && <Text style={styles.foot}>saving session…</Text>}
        {!exporting && exportError && (
          <Text style={[styles.foot, { color: '#e08a7a' }]}>export failed: {exportError}</Text>
        )}
        {!exporting && lastExport && (
          <Pressable style={styles.exportRow} onPress={() => shareSession(lastExport.id, lastExport.name)}>
            <Text style={styles.exportText}>✓ saved · {lastExport.count.toLocaleString()} samples</Text>
            <Text style={styles.exportSub}>{lastExport.name}  ·  tap to share</Text>
          </Pressable>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: '#0e1013' },
  scroll: { padding: 22, paddingTop: 60, gap: 12 },
  brand: { color: '#e9ebf0', fontSize: 28, fontWeight: '800', letterSpacing: -0.5 },
  subtitle: { color: '#9aa1ad', fontSize: 13, marginTop: -8, letterSpacing: 0.3 },
  input: { color: '#e9ebf0', fontSize: 15, backgroundColor: '#0e1013', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 10, borderWidth: 1, borderColor: '#23262d' },
  condRow: { flexDirection: 'row', gap: 8 },
  condBtn: { flex: 1, paddingVertical: 10, borderRadius: 8, borderWidth: 1, borderColor: '#23262d', alignItems: 'center' },
  condOn: { backgroundColor: ACCENT, borderColor: ACCENT },
  condText: { color: '#9aa1ad', fontSize: 14, fontWeight: '600' },
  condTextOn: { color: '#08121a' },
  locBtn: { paddingVertical: 9, borderRadius: 8, borderWidth: 1, borderColor: '#23262d', alignItems: 'center' },
  timerBox: { alignItems: 'center', paddingVertical: 6 },
  timer: { color: '#e9ebf0', fontSize: 46, fontWeight: '700', fontVariant: ['tabular-nums'] },
  timerLabel: { color: '#9aa1ad', fontSize: 13, marginTop: 2 },
  table: { backgroundColor: '#161a1f', borderRadius: 14, padding: 6, borderWidth: 1, borderColor: '#23262d' },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, paddingHorizontal: 12, gap: 8 },
  head: { paddingVertical: 6 },
  dim: { color: '#5b616e', fontSize: 12 },
  ch: { width: 52, color: '#e9ebf0', fontSize: 15, fontWeight: '600', fontFamily: 'Menlo' },
  val: { flex: 1, flexDirection: 'row', alignItems: 'baseline', gap: 6 },
  valText: { color: '#e9ebf0', fontSize: 15, fontFamily: 'Menlo', fontVariant: ['tabular-nums'] },
  unit: { color: '#5b616e', fontSize: 11 },
  n: { width: 88, flexDirection: 'row', alignItems: 'baseline', justifyContent: 'flex-end', gap: 6 },
  nText: { color: '#e9ebf0', fontSize: 14, fontFamily: 'Menlo', fontVariant: ['tabular-nums'] },
  btn: { borderRadius: 12, paddingVertical: 15, alignItems: 'center' },
  btnDisabled: { opacity: 0.4 },
  btnText: { color: '#08121a', fontSize: 17, fontWeight: '700' },
  clearBtn: { alignItems: 'center', paddingVertical: 6 },
  clearBtnText: { color: '#9aa1ad', fontSize: 14, fontWeight: '600' },
  homeBack: { paddingBottom: 2 },
  homeBackText: { color: ACCENT, fontSize: 14, fontWeight: '600' },
  exportRow: { backgroundColor: '#12211d', borderRadius: 10, borderWidth: 1, borderColor: '#1f3a30', padding: 12 },
  exportText: { color: '#7fd8b0', fontSize: 14, fontWeight: '600' },
  exportSub: { color: '#5b8a76', fontSize: 12, marginTop: 2 },
  foot: { color: '#5b616e', fontSize: 12.5, lineHeight: 18, textAlign: 'center', paddingHorizontal: 10 },
});
