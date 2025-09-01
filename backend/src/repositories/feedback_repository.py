"""Feedback Repository for M6: Feedback Capture & Persistence System

Minimal, cleaned implementation without duplicated definitions.
"""

import json
import os
import tempfile
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog
import asyncio

try:
    from backend.src.models.feedback import FeedbackItem, FeedbackSummary
except Exception:
    from ..models.feedback import FeedbackItem, FeedbackSummary

logger = structlog.get_logger()

# Global lock registry to coordinate writes across repository instances
_GLOBAL_FEEDBACK_LOCKS: Dict[str, threading.Lock] = {}

def _get_global_lock_for_path(path: Path) -> threading.Lock:
    key = str(path.resolve())
    if key not in _GLOBAL_FEEDBACK_LOCKS:
        _GLOBAL_FEEDBACK_LOCKS[key] = threading.Lock()
    return _GLOBAL_FEEDBACK_LOCKS[key]


class SyncAwaitable:
    def __init__(self, value):
        self._value = value

    def __await__(self):
        async def _wrap():
            return self._value

        return _wrap().__await__()

    def __len__(self):
        return len(self._value)

    def __iter__(self):
        return iter(self._value)

    def __getitem__(self, item):
        return self._value[item]

    def __bool__(self):
        return bool(self._value)

    def __repr__(self):
        return repr(self._value)


class FeedbackRepository(ABC):
    @abstractmethod
    def save_feedback(self, feedback: FeedbackItem):
        raise NotImplementedError

    @abstractmethod
    def get_feedback_by_session(self, session_id: str):
        raise NotImplementedError

    @abstractmethod
    def get_feedback_summary(self, days_back: int = 30):
        raise NotImplementedError

    @abstractmethod
    def get_all_feedback(self, limit: int = 1000):
        raise NotImplementedError

    @abstractmethod
    def cleanup_old_feedback(self, days_to_keep: int = 90):
        raise NotImplementedError


class FileBasedFeedbackRepository(FeedbackRepository):
    def __init__(self, storage_path: str = "data/feedback", max_file_size_mb: float = 10.0):
        self.storage_path = Path(storage_path)
        self.max_file_size_mb = max_file_size_mb
        self._lock = threading.RLock()
        self._current_file_path: Optional[Path] = None
        self._ensure_storage_directory()

    def _maybe_awaitable(self, value):
        try:
            asyncio.get_running_loop()
            return SyncAwaitable(value)
        except RuntimeError:
            return value

    def _ensure_storage_directory(self) -> None:
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_current_file_path(self) -> Path:
        if self._current_file_path is None:
            today = datetime.now().strftime("%Y-%m-%d")
            self._current_file_path = self.storage_path / f"feedback_{today}.json"
        return self._current_file_path

    def _set_current_file_path(self, file_path: Path) -> None:
        self._current_file_path = file_path

    def _atomic_write(self, file_path: Path, data: List[Dict[str, Any]]) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_fd, temp_path = tempfile.mkstemp(dir=file_path.parent, prefix=f"{file_path.stem}_", suffix=".tmp")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as tmp:
                json.dump(data, tmp, indent=2, ensure_ascii=False)

            temp_path_obj = Path(temp_path)
            retries = 5
            for attempt in range(retries):
                try:
                    temp_path_obj.replace(file_path)
                    break
                except PermissionError:
                    if attempt < retries - 1:
                        import time
                        time.sleep(0.02 * (attempt + 1))
                        continue
                    raise
        finally:
            if Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                except OSError:
                    pass

    def _read_feedback_file(self, file_path: Path) -> List[Dict[str, Any]]:
        if not file_path.exists():
            return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _get_all_feedback_files(self) -> List[Path]:
        if not self.storage_path.exists():
            return []
        files = [p for p in self.storage_path.glob("feedback_*.json") if p.is_file()]
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return files


    def save_feedback(self, feedback: FeedbackItem):
        try:
            global_lock = _get_global_lock_for_path(self.storage_path)
            # Ensure only one process/thread writes to the target file at a time
            with global_lock:
                with self._lock:
                    file_path = self._get_current_file_path()
                    existing = self._read_feedback_file(file_path)
                    item = feedback.model_dump()
                    tentative = existing + [item]
                    try:
                        size_mb = len(json.dumps(tentative, ensure_ascii=False).encode('utf-8')) / (1024 * 1024)
                    except Exception:
                        size_mb = 0.0

                    if size_mb > self.max_file_size_mb and existing:
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        file_path = self.storage_path / f"feedback_{timestamp}.json"
                        self._set_current_file_path(file_path)
                        to_write = [item]
                    else:
                        to_write = tentative

                    self._atomic_write(file_path, to_write)

            return self._maybe_awaitable(True)
        except Exception:
            return self._maybe_awaitable(False)

    def get_feedback_by_session(self, session_id: str):
        try:
            results = []
            for file_path in self._get_all_feedback_files():
                for item in self._read_feedback_file(file_path):
                    if item.get('session_id') == session_id:
                        try:
                            results.append(FeedbackItem(**item))
                        except Exception:
                            continue

            results.sort(key=lambda x: x.timestamp, reverse=True)
            return self._maybe_awaitable(results)
        except Exception:
            return self._maybe_awaitable([])

    def get_all_feedback(self, limit: int = 1000):
        try:
            results = []
            for file_path in self._get_all_feedback_files():
                for item in self._read_feedback_file(file_path):
                    try:
                        results.append(FeedbackItem(**item))
                    except Exception:
                        continue
                    if len(results) >= limit:
                        break

            results.sort(key=lambda x: x.timestamp, reverse=True)
            return self._maybe_awaitable(results[:limit])
        except Exception:
            return self._maybe_awaitable([])

    def get_feedback_summary(self, days_back: int = 30):
        try:
            cutoff = datetime.now() - timedelta(days=days_back)
            all_feedback = self.get_all_feedback(limit=10000)
            if isinstance(all_feedback, SyncAwaitable):
                all_feedback = all_feedback._value

            recent = [f for f in all_feedback if f.timestamp >= cutoff]
            total = len(recent)
            if total == 0:
                return self._maybe_awaitable(FeedbackSummary())

            confirm = sum(1 for f in recent if getattr(f.action, 'value', None) == 'confirm')
            reject = sum(1 for f in recent if getattr(f.action, 'value', None) == 'reject')
            adjust = sum(1 for f in recent if getattr(f.action, 'value', None) == 'adjust')

            strategy_counts = {}
            for f in recent:
                strategy_counts[f.strategy_id] = strategy_counts.get(f.strategy_id, 0) + 1

            summary = FeedbackSummary(
                total_feedback=total,
                confirm_count=confirm,
                reject_count=reject,
                adjust_count=adjust,
                strategy_feedback_counts=strategy_counts,
                action_distribution={'confirm': confirm, 'reject': reject, 'adjust': adjust},
                average_feedback_per_session=(total / len(set(f.session_id for f in recent))) if recent else 0,
                most_feedback_strategy=max(strategy_counts, key=strategy_counts.get) if strategy_counts else None,
                recent_feedback_trend=[],
            )

            return self._maybe_awaitable(summary)
        except Exception:
            return self._maybe_awaitable(FeedbackSummary())

    def cleanup_old_feedback(self, days_to_keep: int = 90):
        try:
            cutoff = datetime.now() - timedelta(days_to_keep)
            deleted = 0
            for file_path in self._get_all_feedback_files():
                data = self._read_feedback_file(file_path)
                kept = []
                for item in data:
                    ts = item.get('timestamp')
                    try:
                        dt = datetime.fromisoformat(ts) if ts else None
                    except Exception:
                        dt = None
                    if dt and dt >= cutoff:
                        kept.append(item)

                removed = len(data) - len(kept)
                deleted += removed
                if removed > 0:
                    if kept:
                        self._atomic_write(file_path, kept)
                    else:
                        try:
                            file_path.unlink()
                        except OSError:
                            pass

            return self._maybe_awaitable(deleted)
        except Exception:
            return self._maybe_awaitable(0)