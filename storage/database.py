"""
SQLite Database interface for storing runs, metrics, and experimental results.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from orchestration.state import RunState


class Database:
    def __init__(self, db_path: str = "./runs/research_system.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                original_prompt TEXT,
                system_mode TEXT,
                status TEXT,
                current_iteration INTEGER,
                composite_score REAL,
                wcag_pass_rate REAL,
                dark_pattern_count INTEGER,
                total_latency_ms REAL,
                total_tokens INTEGER,
                total_cost_usd REAL,
                structured_prompt_json TEXT,
                evaluation_json TEXT,
                start_time TEXT,
                end_time TEXT
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS iterations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                iteration_number INTEGER,
                composite_score REAL,
                aesthetic_score REAL,
                accessibility_score REAL,
                usability_score REAL,
                ethics_score REAL,
                originality_score REAL,
                created_at TEXT,
                FOREIGN KEY (run_id) REFERENCES runs (run_id)
            )
            """)
            conn.commit()

    def save_run(self, state: RunState):
        eval_metrics = state.evaluation
        with self._get_conn() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO runs (
                run_id, original_prompt, system_mode, status, current_iteration,
                composite_score, wcag_pass_rate, dark_pattern_count,
                total_latency_ms, total_tokens, total_cost_usd,
                structured_prompt_json, evaluation_json, start_time, end_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.run_id,
                state.original_prompt,
                state.system_mode,
                state.status,
                state.current_iteration,
                eval_metrics.composite_score if eval_metrics else 0.0,
                eval_metrics.wcag_pass_rate if eval_metrics else 100.0,
                eval_metrics.dark_pattern_count if eval_metrics else 0,
                state.total_latency_ms,
                state.total_token_usage.total_tokens,
                state.total_token_usage.estimated_cost_usd,
                state.structured_prompt.model_dump_json() if state.structured_prompt else None,
                eval_metrics.model_dump_json() if eval_metrics else None,
                state.start_time,
                state.end_time
            ))

            # Record iteration records
            for it in state.history:
                ev = it.evaluation
                conn.execute("""
                INSERT OR IGNORE INTO iterations (
                    run_id, iteration_number, composite_score,
                    aesthetic_score, accessibility_score, usability_score,
                    ethics_score, originality_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    state.run_id,
                    it.iteration_number,
                    ev.composite_score if ev else 0.0,
                    ev.aesthetic_score if ev else None,
                    ev.accessibility_score if ev else None,
                    ev.usability_score if ev else None,
                    ev.ethics_score if ev else None,
                    ev.originality_score if ev else None,
                    it.created_at
                ))

            conn.commit()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def list_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM runs ORDER BY start_time DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
