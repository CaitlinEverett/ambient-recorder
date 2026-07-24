// Saved sessions — lists sessions out of SQLite, newest first, so the home
// screen can show recent runs and re-share/email them. (Previously scanned
// exported JSON files in Documents; now reads the sessions table instead —
// see src/db.ts.)

import { listSessions as listSessionRows, SessionRow } from './db';

export type SavedSession = SessionRow;

export async function listSessions(): Promise<SavedSession[]> {
  try {
    return await listSessionRows();
  } catch {
    return [];
  }
}
