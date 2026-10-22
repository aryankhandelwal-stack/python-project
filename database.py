"""SQLite persistence for packets and simulated downlink sessions."""
import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path="orbitlink.db"):
        self.path = str(Path(path))
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                urgency INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'WAITING',
                reason TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal INTEGER NOT NULL,
                battery INTEGER NOT NULL,
                sent INTEGER NOT NULL,
                deferred INTEGER NOT NULL,
                seconds_used REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_packet(self, mode, size_bytes, urgency):
        cur = self.conn.execute(
            "INSERT INTO packets(mode,size_bytes,urgency) VALUES(?,?,?)",
            (mode, size_bytes, urgency),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_packets(self):
        return self.conn.execute("""
            SELECT id, mode, size_bytes, urgency, status, reason
            FROM packets ORDER BY id
        """).fetchall()

    def update_packet(self, packet_id, status, reason):
        self.conn.execute(
            "UPDATE packets SET status=?, reason=? WHERE id=?",
            (status, reason, packet_id),
        )
        self.conn.commit()

    def add_session(self, signal, battery, sent, deferred, seconds_used):
        self.conn.execute(
            "INSERT INTO sessions(signal,battery,sent,deferred,seconds_used) VALUES(?,?,?,?,?)",
            (signal, battery, sent, deferred, seconds_used),
        )
        self.conn.commit()

    def get_sessions(self, limit=20):
        return self.conn.execute("""
            SELECT id, signal, battery, sent, deferred, seconds_used, created_at
            FROM sessions ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()

    def reset(self):
        self.conn.execute("DELETE FROM packets")
        self.conn.execute("DELETE FROM sessions")
        self.conn.commit()

    def close(self):
        self.conn.close()
