// Saved sessions — lists the exported JSON files in Documents, newest first, so
// the home screen can show recent runs and re-share them.

import * as FileSystem from 'expo-file-system/legacy';

export interface SavedSession {
  name: string;
  uri: string;
}

export async function listSessions(): Promise<SavedSession[]> {
  const dir = FileSystem.documentDirectory;
  if (!dir) return [];
  try {
    const names = await FileSystem.readDirectoryAsync(dir);
    return names
      .filter((n) => n.startsWith('covariate_') && n.endsWith('.json'))
      .sort() // filenames carry an ISO timestamp -> lexical sort is chronological
      .reverse() // newest first
      .map((name) => ({ name, uri: dir + name }));
  } catch {
    return [];
  }
}
