// SQLite-backed session storage — replaces writing one JSON file per session
// to Documents. Each row stores the *whole* SessionRecord as a JSON blob
// rather than normalizing per-sample rows: SessionRecorder.build() doesn't
// change at all, and the only consumers of saved sessions (the home screen
// list, and re-sharing/emailing a session) just need to list and read whole
// records back out, not query inside them. Revisit as normalized rows only
// if on-device SQL analysis across samples becomes a real need.
//
// expo-sqlite is a standard Expo SDK module (unlike covariate-light/mic) —
// it works fine in Expo Go, no dev client required.

import * as SQLite from 'expo-sqlite';
import { SessionRecord } from './schema';

export interface SessionRow {
  id: string;
  experimentId: string;
  startedAtWall: string;
  endedAtWall: string;
  sampleCount: number;
  schemaVersion: string;
}

let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;

function getDb(): Promise<SQLite.SQLiteDatabase> {
  if (!dbPromise) {
    dbPromise = SQLite.openDatabaseAsync('covariate.db').then(async (db) => {
      await db.execAsync(`
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS sessions (
          id TEXT PRIMARY KEY,
          experiment_id TEXT NOT NULL,
          started_at_wall TEXT NOT NULL,
          ended_at_wall TEXT NOT NULL,
          sample_count INTEGER NOT NULL,
          schema_version TEXT NOT NULL,
          record_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at_wall);
      `);
      return db;
    });
  }
  return dbPromise;
}

function makeSessionId(record: SessionRecord): string {
  const safeId = (record.meta.experimentID || 'session').replace(/[^\w.-]+/g, '_');
  const stamp = record.meta.startedAtWall.replace(/[:.]/g, '-');
  return `covariate_${safeId}_${stamp}`;
}

/** Persist a completed session record. Returns the row id + a display/export filename. */
export async function saveSession(record: SessionRecord): Promise<{ id: string; name: string }> {
  const db = await getDb();
  const id = makeSessionId(record);
  const name = `${id}.json`;
  await db.runAsync(
    `INSERT INTO sessions (id, experiment_id, started_at_wall, ended_at_wall, sample_count, schema_version, record_json)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    id,
    record.meta.experimentID,
    record.meta.startedAtWall,
    record.meta.endedAtWall,
    record.samples.length,
    record.meta.schemaVersion,
    JSON.stringify(record)
  );
  return { id, name };
}

/** List saved sessions, newest first — same ordering the old directory scan gave. */
export async function listSessions(): Promise<SessionRow[]> {
  const db = await getDb();
  return db.getAllAsync<SessionRow>(
    `SELECT id, experiment_id as experimentId, started_at_wall as startedAtWall,
            ended_at_wall as endedAtWall, sample_count as sampleCount, schema_version as schemaVersion
     FROM sessions ORDER BY started_at_wall DESC`
  );
}

/** Fetch one session's full JSON blob — used for the export/share flow. */
export async function getSessionJson(id: string): Promise<string | null> {
  const db = await getDb();
  const row = await db.getFirstAsync<{ record_json: string }>(
    `SELECT record_json FROM sessions WHERE id = ?`,
    id
  );
  return row?.record_json ?? null;
}

/** Delete a session row. Not wired into any UI yet — available for a future cleanup/retention feature. */
export async function deleteSession(id: string): Promise<void> {
  const db = await getDb();
  await db.runAsync(`DELETE FROM sessions WHERE id = ?`, id);
}
