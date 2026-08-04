import { Pressable, StyleSheet, Text, View } from 'react-native';
import { ChannelId } from './schema';
import { CHANNELS, childrenOf, describeDerivation, isChannelAvailable } from './channels';
import CovariateLightModule from '../modules/covariate-light/src/CovariateLightModule';
import CovariateMicModule from '../modules/covariate-mic/src/CovariateMicModule';

// Per-experiment channel toggles — which sensors (and the readings derived from
// them) this experiment records. A derived channel can't be on without its
// parent, so turning a direct channel off takes its derived children with it,
// and turning a derived channel on brings its parent along.

const ACCENT = '#4fb3c4';
const native = { hasLight: CovariateLightModule != null, hasMic: CovariateMicModule != null };

export default function ChannelToggles({
  enabled,
  onChange,
}: {
  enabled: ChannelId[];
  onChange: (next: ChannelId[]) => void;
}) {
  const isOn = (id: ChannelId) => enabled.includes(id);

  function toggle(id: ChannelId, derivedFrom?: ChannelId) {
    if (isOn(id)) {
      const drop = new Set<ChannelId>([id, ...childrenOf(id).map((c) => c.id)]);
      onChange(enabled.filter((c) => !drop.has(c)));
    } else {
      const add = derivedFrom && !isOn(derivedFrom) ? [derivedFrom, id] : [id];
      onChange([...enabled, ...add.filter((c) => !enabled.includes(c))]);
    }
  }

  return (
    <View style={styles.wrap}>
      {CHANNELS.filter((c) => c.kind === 'direct').map((def) => {
        const usable = isChannelAvailable(def.id, native);
        const on = isOn(def.id) && usable;
        return (
          <View key={def.id}>
            <Pressable disabled={!usable} onPress={() => toggle(def.id)} style={styles.row}>
              <View style={[styles.box, on && styles.boxOn, !usable && styles.boxDisabled]}>
                {on && <Text style={styles.check}>✓</Text>}
              </View>
              <Text style={[styles.label, !usable && styles.labelOff]}>{def.label}</Text>
              <Text style={styles.unit}>{usable ? def.unit : 'dev build only (Expo Go)'}</Text>
            </Pressable>
            {childrenOf(def.id).map((kid) => {
              const kidUsable = usable && on;
              const kidOn = isOn(kid.id) && kidUsable;
              return (
                <Pressable
                  key={kid.id}
                  disabled={!kidUsable}
                  onPress={() => toggle(kid.id, def.id)}
                  style={[styles.row, styles.childRow]}
                >
                  <Text style={styles.arrow}>↳</Text>
                  <View style={[styles.box, kidOn && styles.boxOn, !kidUsable && styles.boxDisabled]}>
                    {kidOn && <Text style={styles.check}>✓</Text>}
                  </View>
                  <View style={styles.childBody}>
                    <View style={styles.rowLine}>
                      <Text style={[styles.label, styles.labelChild, !kidUsable && styles.labelOff]}>{kid.label}</Text>
                      <Text style={styles.unit}>{kid.unit}</Text>
                    </View>
                    <Text style={styles.method}>{describeDerivation(kid)}</Text>
                  </View>
                </Pressable>
              );
            })}
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { backgroundColor: '#161a1f', borderRadius: 12, borderWidth: 1, borderColor: '#23262d', paddingVertical: 4 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 9, paddingHorizontal: 12 },
  childRow: { paddingLeft: 26, paddingVertical: 7 },
  arrow: { width: 10, color: '#5b616e', fontSize: 12 },
  box: { width: 18, height: 18, borderRadius: 5, borderWidth: 1.5, borderColor: '#3a3f48', alignItems: 'center', justifyContent: 'center' },
  boxOn: { backgroundColor: ACCENT, borderColor: ACCENT },
  boxDisabled: { opacity: 0.4 },
  check: { color: '#08121a', fontSize: 12, fontWeight: '800' },
  label: { width: 46, color: '#e9ebf0', fontSize: 13, fontWeight: '600', fontFamily: 'Menlo' },
  labelChild: { color: '#9aa1ad', fontWeight: '500' },
  labelOff: { color: '#5b616e' },
  unit: { color: '#5b616e', fontSize: 11.5 },
  childBody: { flex: 1 },
  rowLine: { flexDirection: 'row', alignItems: 'baseline', gap: 8 },
  method: { color: '#5b616e', fontSize: 10.5, fontStyle: 'italic', marginTop: 2 },
});
