// Experiments — a session belongs to an experiment (a named study you run many
// times). Stored locally for now.
//
// GUIDE seam: everything goes through list()/create() and each experiment carries
// `source`. Local now; a GUIDE-backed source can slot in later without touching
// callers. When we wire GUIDE, only this file changes.

import AsyncStorage from '@react-native-async-storage/async-storage';
import { ChannelId } from './schema';
import { DEFAULT_ENABLED_CHANNELS } from './channels';

export interface Experiment {
  id: string;
  name: string;
  notes: string;
  createdAt: string; // ISO 8601
  source: 'local' | 'guide';
  enabledChannels: ChannelId[]; // which channels this experiment records
}

const KEY = 'covariate.experiments.v1';

export async function listExperiments(): Promise<Experiment[]> {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    type Stored = Omit<Experiment, 'enabledChannels'> & { enabledChannels?: ChannelId[] };
    const arr = raw ? (JSON.parse(raw) as Stored[]) : [];
    if (!Array.isArray(arr)) return [];
    // Back-fill experiments saved before enabledChannels existed.
    return arr.map((e) => ({ ...e, enabledChannels: e.enabledChannels ?? DEFAULT_ENABLED_CHANNELS }));
  } catch {
    return [];
  }
}

export async function createExperiment(name: string, notes = ''): Promise<Experiment> {
  const exp: Experiment = {
    id: `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`,
    name: name.trim(),
    notes: notes.trim(),
    createdAt: new Date().toISOString(),
    source: 'local',
    enabledChannels: DEFAULT_ENABLED_CHANNELS,
  };
  const all = await listExperiments();
  all.unshift(exp);
  await AsyncStorage.setItem(KEY, JSON.stringify(all));
  return exp;
}

export async function updateExperiment(id: string, patch: Partial<Experiment>): Promise<Experiment[]> {
  const all = await listExperiments();
  const next = all.map((e) => (e.id === id ? { ...e, ...patch } : e));
  await AsyncStorage.setItem(KEY, JSON.stringify(next));
  return next;
}
