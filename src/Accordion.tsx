import { ReactNode, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

// Simple collapsible section — keeps the record screen to one screen by tucking
// secondary controls (details, sensor tools) behind a tap.
export default function Accordion({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <View style={styles.wrap}>
      <Pressable onPress={() => setOpen((o) => !o)} style={styles.header}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.chev}>{open ? '⌄' : '›'}</Text>
      </Pressable>
      {open && <View style={styles.body}>{children}</View>}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { backgroundColor: '#161a1f', borderRadius: 12, borderWidth: 1, borderColor: '#23262d', overflow: 'hidden' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 12, paddingHorizontal: 14 },
  title: { color: '#e9ebf0', fontSize: 14, fontWeight: '600' },
  chev: { color: '#9aa1ad', fontSize: 16 },
  body: { padding: 10, paddingTop: 2, gap: 8 },
});
