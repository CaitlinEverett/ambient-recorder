import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Experiment } from './experiments';
import { SavedSession } from './sessions';

const ACCENT = '#4fb3c4';

export default function HomeScreen(props: {
  experiments: Experiment[];
  sessions: SavedSession[];
  onCreate: (name: string) => void;
  onPick: (exp: Experiment) => void;
  onShare: (uri: string) => void;
}) {
  const { experiments, sessions, onCreate, onPick, onShare } = props;
  const [newName, setNewName] = useState('');

  return (
    <View style={styles.app}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <Text style={styles.brand}>Co<Text style={{ color: ACCENT }}>variate</Text></Text>
        <Text style={styles.subtitle}>experiments &amp; sessions</Text>

        <Text style={styles.section}>EXPERIMENTS</Text>
        <View style={styles.card}>
          <View style={styles.newRow}>
            <TextInput
              style={styles.input} value={newName} onChangeText={setNewName}
              placeholder="New experiment name" placeholderTextColor="#5b616e"
              autoCapitalize="none" autoCorrect={false}
            />
            <Pressable
              disabled={!newName.trim()}
              onPress={() => { onCreate(newName.trim()); setNewName(''); }}
              style={[styles.addBtn, !newName.trim() && { opacity: 0.4 }]}
            >
              <Text style={styles.addBtnText}>+ New</Text>
            </Pressable>
          </View>
          {experiments.length === 0 && (
            <Text style={styles.empty}>No experiments yet — create one to start a session.</Text>
          )}
          {experiments.map((e) => (
            <Pressable key={e.id} onPress={() => onPick(e)} style={styles.expRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.expName}>{e.name}</Text>
                {!!e.notes && <Text style={styles.expNotes} numberOfLines={1}>{e.notes}</Text>}
              </View>
              <Text style={styles.expGo}>▶ session</Text>
            </Pressable>
          ))}
        </View>

        <Text style={styles.section}>RECENT SESSIONS</Text>
        <View style={styles.card}>
          {sessions.length === 0 && <Text style={styles.empty}>No exported sessions yet.</Text>}
          {sessions.slice(0, 15).map((s) => (
            <Pressable key={s.uri} onPress={() => onShare(s.uri)} style={styles.sessRow}>
              <Text style={styles.sessName} numberOfLines={1}>
                {s.name.replace('covariate_', '').replace('.json', '')}
              </Text>
              <Text style={styles.sessShare}>share</Text>
            </Pressable>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  app: { flex: 1, backgroundColor: '#0e1013' },
  scroll: { padding: 22, paddingTop: 72, gap: 12 },
  brand: { color: '#e9ebf0', fontSize: 30, fontWeight: '800', letterSpacing: -0.5 },
  subtitle: { color: '#9aa1ad', fontSize: 13, marginTop: -10, letterSpacing: 0.4, marginBottom: 6 },
  section: { color: '#5b616e', fontSize: 11, fontWeight: '700', letterSpacing: 0.9, marginTop: 8 },
  card: { backgroundColor: '#161a1f', borderRadius: 14, padding: 8, borderWidth: 1, borderColor: '#23262d' },
  newRow: { flexDirection: 'row', gap: 8, padding: 4 },
  input: { flex: 1, color: '#e9ebf0', fontSize: 15, backgroundColor: '#0e1013', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 10, borderWidth: 1, borderColor: '#23262d' },
  addBtn: { backgroundColor: ACCENT, borderRadius: 8, paddingHorizontal: 16, justifyContent: 'center' },
  addBtnText: { color: '#08121a', fontSize: 14, fontWeight: '700' },
  empty: { color: '#5b616e', fontSize: 13, padding: 12 },
  expRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, paddingHorizontal: 12, borderTopWidth: 1, borderTopColor: '#23262d' },
  expName: { color: '#e9ebf0', fontSize: 15, fontWeight: '600' },
  expNotes: { color: '#9aa1ad', fontSize: 12.5, marginTop: 2 },
  expGo: { color: ACCENT, fontSize: 13, fontWeight: '600' },
  sessRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 11, paddingHorizontal: 12, gap: 10, borderTopWidth: 1, borderTopColor: '#23262d' },
  sessName: { flex: 1, color: '#c8ccd4', fontSize: 12.5, fontFamily: 'Menlo' },
  sessShare: { color: ACCENT, fontSize: 12.5, fontWeight: '600' },
});
