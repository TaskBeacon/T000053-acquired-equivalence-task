from __future__ import annotations

import random as _py_random
from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    """Task-specific simulation responder for the acquired-equivalence task."""

    key: str | None = None
    stage1_hit_rate: float = 0.99
    stage2_hit_rate: float = 0.97
    stage3_hit_rate: float = 0.95
    transfer_hit_rate: float = 0.88
    timeout_rate: float = 0.02
    rt_mean_s: float = 0.92
    rt_sd_s: float = 0.22
    rt_min_s: float = 0.18
    continue_rt_s: float = 0.5

    def __post_init__(self) -> None:
        self._rng: Any = None
        self.stage1_hit_rate = max(0.0, min(1.0, float(self.stage1_hit_rate)))
        self.stage2_hit_rate = max(0.0, min(1.0, float(self.stage2_hit_rate)))
        self.stage3_hit_rate = max(0.0, min(1.0, float(self.stage3_hit_rate)))
        self.transfer_hit_rate = max(0.0, min(1.0, float(self.transfer_hit_rate)))
        self.timeout_rate = max(0.0, min(1.0, float(self.timeout_rate)))
        self.rt_mean_s = float(self.rt_mean_s)
        self.rt_sd_s = max(1e-6, float(self.rt_sd_s))
        self.rt_min_s = max(0.0, float(self.rt_min_s))
        self.continue_rt_s = max(self.rt_min_s, float(self.continue_rt_s))

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _sample_normal(self, mean: float, sd: float) -> float:
        rng = self._rng
        if hasattr(rng, "normal"):
            return float(rng.normal(mean, sd))
        return float(rng.gauss(mean, sd))

    def _sample_random(self) -> float:
        rng = self._rng
        if hasattr(rng, "random"):
            return float(rng.random())
        return float(_py_random.random())

    def _pick_valid_key(self, valid_keys: list[str], correct_key: str | None) -> str | None:
        if correct_key and correct_key in valid_keys:
            return correct_key
        if self.key and self.key in valid_keys:
            return self.key
        return valid_keys[0] if valid_keys else None

    def _profile(self, obs: Observation) -> dict[str, Any]:
        task_factors = dict(getattr(obs, "task_factors", {}) or {})
        if not task_factors and isinstance(getattr(obs, "extras", None), dict):
            task_factors = dict(obs.extras.get("task_factors", {}) or {})

        stage_id = str(task_factors.get("stage_id", getattr(obs, "phase", ""))).strip().lower()
        condition_id = str(task_factors.get("condition_id", "")).strip().lower()
        block_idx = int(task_factors.get("block_idx", 0) or 0)
        pair_kind = str(task_factors.get("pair_kind", "")).strip().lower()

        if any(
            token in f"{stage_id} {condition_id}"
            for token in ("instruction", "block_intro", "block_summary", "good_bye")
        ):
            return {
                "task_factors": task_factors,
                "stage_id": stage_id,
                "condition_id": condition_id,
                "hit_rate": 1.0,
                "timeout_rate": 0.0,
                "rt_mean_s": self.continue_rt_s,
            }

        if stage_id == "stage1_training":
            hit_rate = self.stage1_hit_rate
            rt_mean = self.rt_mean_s - 0.10
        elif stage_id == "stage2_training":
            hit_rate = self.stage2_hit_rate
            rt_mean = self.rt_mean_s - 0.05
        elif stage_id == "stage3_training":
            hit_rate = self.stage3_hit_rate
            rt_mean = self.rt_mean_s
        elif stage_id == "transfer_test" or pair_kind == "transfer_probe":
            hit_rate = self.transfer_hit_rate
            rt_mean = self.rt_mean_s + 0.08
        else:
            hit_rate = self.stage2_hit_rate
            rt_mean = self.rt_mean_s

        if block_idx >= 2 and stage_id in {"stage2_training", "stage3_training", "transfer_test"}:
            hit_rate = min(1.0, hit_rate + 0.01)

        return {
            "task_factors": task_factors,
            "stage_id": stage_id,
            "condition_id": condition_id,
            "hit_rate": max(0.0, min(1.0, hit_rate)),
            "timeout_rate": max(0.0, min(1.0, self.timeout_rate)),
            "rt_mean_s": max(self.rt_min_s, rt_mean),
        }

    def act(self, obs: Observation) -> Action:
        valid_keys = [str(key) for key in list(obs.valid_keys or [])]
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "no_valid_keys"})

        rng = self._rng
        if rng is None:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "rng_missing"})

        profile = self._profile(obs)
        task_factors = profile["task_factors"]
        correct_key = task_factors.get("correct_key") or getattr(obs, "correct_key", None)
        correct_key = str(correct_key) if correct_key is not None else None

        if profile["hit_rate"] >= 1.0 and profile["timeout_rate"] <= 0.0:
            rt = max(self.rt_min_s, self._sample_normal(self.continue_rt_s, self.rt_sd_s))
            chosen_key = self._pick_valid_key(valid_keys, correct_key or self.key)
            return Action(
                key=chosen_key,
                rt_s=rt,
                meta={"source": "task_sampler", "outcome": "continue", "correct_key": correct_key, "stage": profile["stage_id"]},
            )

        if self._sample_random() < profile["timeout_rate"]:
            return Action(
                key=None,
                rt_s=None,
                meta={"source": "task_sampler", "outcome": "timeout", "correct_key": correct_key, "stage": profile["stage_id"]},
            )

        rt = max(self.rt_min_s, self._sample_normal(profile["rt_mean_s"], self.rt_sd_s))

        if self._sample_random() > profile["hit_rate"]:
            wrong_keys = [key for key in valid_keys if key != correct_key]
            chosen_key = wrong_keys[0] if wrong_keys else self._pick_valid_key(valid_keys, correct_key)
            return Action(
                key=chosen_key,
                rt_s=rt,
                meta={"source": "task_sampler", "outcome": "miss", "correct_key": correct_key, "stage": profile["stage_id"]},
            )

        chosen_key = self._pick_valid_key(valid_keys, correct_key)
        return Action(
            key=chosen_key,
            rt_s=rt,
            meta={"source": "task_sampler", "outcome": "hit", "correct_key": correct_key, "stage": profile["stage_id"]},
        )
