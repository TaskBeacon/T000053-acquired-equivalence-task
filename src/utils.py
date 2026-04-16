from __future__ import annotations

import random
from collections import defaultdict
from typing import Any

DEFAULT_LEFT_KEY = "z"
DEFAULT_RIGHT_KEY = "m"
DEFAULT_CONTINUE_KEY = "space"
DEFAULT_RESPONSE_WINDOW_S = 3.0
DEFAULT_FIXATION_DURATION_S = 0.4
DEFAULT_FEEDBACK_DURATION_S = 0.8
DEFAULT_ITI_DURATION_S = 0.4
DEFAULT_BLOCK_REPEAT_LIMIT = 8

DEFAULT_FACE_ASSETS = {
    "A1": "face_A1",
    "A2": "face_A2",
    "B1": "face_B1",
    "B2": "face_B2",
}

DEFAULT_FISH_ASSETS = {
    "X1": "fish_X1",
    "X2": "fish_X2",
    "Y1": "fish_Y1",
    "Y2": "fish_Y2",
}

DEFAULT_STAGE_REQUIREMENTS = {
    "stage1_training": 8,
    "stage2_training": 8,
    "stage3_training": 12,
}

PAIR_ORDER = (
    "A1_X1",
    "B1_Y1",
    "A2_X1",
    "B2_Y1",
    "A1_X2",
    "B1_Y2",
    "A2_X2",
    "B2_Y2",
)


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _to_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if value is None:
        return {}
    try:
        return dict(value)
    except Exception:
        return {}


def _trial_rng(seed: int, block_idx: int, trial_idx: int, attempt_idx: int = 0, salt: int = 0) -> random.Random:
    mixed = (
        (int(seed) + 1) * 1_000_003
        + (int(block_idx) + 1) * 10_009
        + (int(trial_idx) + 1) * 1_009
        + (int(attempt_idx) + 1) * 97
        + int(salt) * 31
    )
    return random.Random(mixed % (2**32))


def _asset_name(mapping: dict[str, Any], key: str, default: str) -> str:
    value = mapping.get(key, default)
    if value is None:
        return str(default)
    return str(value)


def _face_asset_map(settings: Any) -> dict[str, str]:
    raw = _to_dict(getattr(settings, "face_assets", None))
    return {
        "A1": _asset_name(raw, "A1", DEFAULT_FACE_ASSETS["A1"]),
        "A2": _asset_name(raw, "A2", DEFAULT_FACE_ASSETS["A2"]),
        "B1": _asset_name(raw, "B1", DEFAULT_FACE_ASSETS["B1"]),
        "B2": _asset_name(raw, "B2", DEFAULT_FACE_ASSETS["B2"]),
    }


def _fish_asset_map(settings: Any) -> dict[str, str]:
    raw = _to_dict(getattr(settings, "fish_assets", None))
    return {
        "X1": _asset_name(raw, "X1", DEFAULT_FISH_ASSETS["X1"]),
        "X2": _asset_name(raw, "X2", DEFAULT_FISH_ASSETS["X2"]),
        "Y1": _asset_name(raw, "Y1", DEFAULT_FISH_ASSETS["Y1"]),
        "Y2": _asset_name(raw, "Y2", DEFAULT_FISH_ASSETS["Y2"]),
    }


def _stage_requirement_map(settings: Any) -> dict[str, int]:
    raw = _to_dict(getattr(settings, "stage_required_consecutive_correct", None))
    return {
        "stage1_training": max(1, _coerce_int(raw.get("stage1_training", DEFAULT_STAGE_REQUIREMENTS["stage1_training"]), DEFAULT_STAGE_REQUIREMENTS["stage1_training"])),
        "stage2_training": max(1, _coerce_int(raw.get("stage2_training", DEFAULT_STAGE_REQUIREMENTS["stage2_training"]), DEFAULT_STAGE_REQUIREMENTS["stage2_training"])),
        "stage3_training": max(1, _coerce_int(raw.get("stage3_training", DEFAULT_STAGE_REQUIREMENTS["stage3_training"]), DEFAULT_STAGE_REQUIREMENTS["stage3_training"])),
    }


def _pair_template(
    *,
    pair_id: str,
    face_id: str,
    correct_fish_id: str,
    foil_fish_id: str,
    pair_kind: str,
) -> dict[str, Any]:
    return {
        "pair_id": str(pair_id),
        "face_id": str(face_id),
        "correct_fish_id": str(correct_fish_id),
        "foil_fish_id": str(foil_fish_id),
        "pair_kind": str(pair_kind),
    }


def _stage_pair_templates(settings: Any) -> dict[str, list[dict[str, Any]]]:
    faces = _face_asset_map(settings)
    fish = _fish_asset_map(settings)

    stage1 = [
        _pair_template(pair_id="A1_X1", face_id=faces["A1"], correct_fish_id=fish["X1"], foil_fish_id=fish["Y1"], pair_kind="training"),
        _pair_template(pair_id="B1_Y1", face_id=faces["B1"], correct_fish_id=fish["Y1"], foil_fish_id=fish["X1"], pair_kind="training"),
    ]
    stage2 = stage1 + [
        _pair_template(pair_id="A2_X1", face_id=faces["A2"], correct_fish_id=fish["X1"], foil_fish_id=fish["Y1"], pair_kind="training"),
        _pair_template(pair_id="B2_Y1", face_id=faces["B2"], correct_fish_id=fish["Y1"], foil_fish_id=fish["X1"], pair_kind="training"),
    ]
    stage3 = stage2 + [
        _pair_template(pair_id="A1_X2", face_id=faces["A1"], correct_fish_id=fish["X2"], foil_fish_id=fish["Y2"], pair_kind="training"),
        _pair_template(pair_id="B1_Y2", face_id=faces["B1"], correct_fish_id=fish["Y2"], foil_fish_id=fish["X2"], pair_kind="training"),
    ]
    transfer = stage3 + [
        _pair_template(pair_id="A2_X2", face_id=faces["A2"], correct_fish_id=fish["X2"], foil_fish_id=fish["Y2"], pair_kind="transfer_probe"),
        _pair_template(pair_id="B2_Y2", face_id=faces["B2"], correct_fish_id=fish["Y2"], foil_fish_id=fish["X2"], pair_kind="transfer_probe"),
    ]

    return {
        "stage1_training": stage1,
        "stage2_training": stage2,
        "stage3_training": stage3,
        "transfer_test": transfer,
    }


def _expand_display_trials(
    pair_templates: list[dict[str, Any]],
    *,
    stage_id: str,
    condition_id: str,
    block_kind: str,
    block_idx: int,
    block_id: str,
    block_label: str,
    seed: int,
    attempt_idx: int = 0,
) -> list[dict[str, Any]]:
    left_key = DEFAULT_LEFT_KEY
    right_key = DEFAULT_RIGHT_KEY

    def _left_stim_id(fish_id: str) -> str:
        return f"{fish_id}_left"

    def _right_stim_id(fish_id: str) -> str:
        return f"{fish_id}_right"

    trials: list[dict[str, Any]] = []
    for template in pair_templates:
        for order_index, correct_left in enumerate((True, False), start=1):
            if correct_left:
                left_fish_id = _left_stim_id(template["correct_fish_id"])
                right_fish_id = _right_stim_id(template["foil_fish_id"])
                correct_key = left_key
                correct_side = "left"
            else:
                left_fish_id = _left_stim_id(template["foil_fish_id"])
                right_fish_id = _right_stim_id(template["correct_fish_id"])
                correct_key = right_key
                correct_side = "right"

            trials.append(
                {
                    "stage_id": stage_id,
                    "condition_id": condition_id,
                    "block_kind": block_kind,
                    "block_idx": int(block_idx),
                    "block_id": block_id,
                    "block_label": block_label,
                    "block_attempt": int(attempt_idx + 1),
                    "pair_id": str(template["pair_id"]),
                    "pair_kind": str(template["pair_kind"]),
                    "face_id": str(template["face_id"]),
                    "correct_fish_id": str(template["correct_fish_id"]),
                    "foil_fish_id": str(template["foil_fish_id"]),
                    "left_fish_id": str(left_fish_id),
                    "right_fish_id": str(right_fish_id),
                    "correct_key": correct_key,
                    "correct_side": correct_side,
                    "order_index": order_index,
                    "seed": int(seed),
                    "stimulus_summary": f'{template["pair_id"]}:{correct_side}',
                }
            )

    rng = _trial_rng(seed, block_idx, 0, attempt_idx=attempt_idx, salt=91)
    rng.shuffle(trials)
    for trial_index, trial in enumerate(trials, start=1):
        trial["trial_index_in_block"] = trial_index

    return trials


def build_session_plan(settings: Any) -> list[dict[str, Any]]:
    """Build the full acquired-equivalence session plan."""

    overall_seed = _coerce_int(getattr(settings, "overall_seed", 53053), 53053)
    repeat_limit = max(1, _coerce_int(getattr(settings, "block_repeat_limit", DEFAULT_BLOCK_REPEAT_LIMIT), DEFAULT_BLOCK_REPEAT_LIMIT))
    stage_requirements = _stage_requirement_map(settings)
    stage_pairs = _stage_pair_templates(settings)

    plan: list[dict[str, Any]] = []
    stage_specs = [
        ("stage1_training", "Stage 1 Training", stage_pairs["stage1_training"], True),
        ("stage2_training", "Stage 2 Training", stage_pairs["stage2_training"], True),
        ("stage3_training", "Stage 3 Training", stage_pairs["stage3_training"], True),
        ("transfer_test", "Final Transfer Test", stage_pairs["transfer_test"], False),
    ]

    for block_idx, (stage_id, block_label, pair_templates, feedback_enabled) in enumerate(stage_specs):
        condition_id = stage_id
        trials = _expand_display_trials(
            pair_templates,
            stage_id=stage_id,
            condition_id=condition_id,
            block_kind="training" if feedback_enabled else "test",
            block_idx=block_idx,
            block_id=f"{stage_id}_block",
            block_label=block_label,
            seed=overall_seed,
            attempt_idx=0,
        )
        plan.append(
            {
                "stage_id": stage_id,
                "block_kind": "training" if feedback_enabled else "test",
                "block_idx": block_idx,
                "block_id": f"{stage_id}_block",
                "block_label": block_label,
                "trials": trials,
                "pair_ids": [trial["pair_id"] for trial in trials],
                "trial_count": len(trials),
                "required_consecutive_correct": stage_requirements.get(stage_id),
                "repeat_limit": repeat_limit,
                "feedback_enabled": feedback_enabled,
            }
        )

    return plan


def summarize_trials(trials: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize accuracy and latency across a trial list."""

    total = len(trials)
    correct = 0
    timeouts = 0
    correct_rts: list[float] = []

    for trial in trials:
        if bool(trial.get("response_correct")):
            correct += 1
            rt = trial.get("response_rt")
            if isinstance(rt, (int, float)) and rt > 0:
                correct_rts.append(float(rt))
        if bool(trial.get("timed_out")):
            timeouts += 1

    mean_correct_rt_ms = round((sum(correct_rts) / len(correct_rts)) * 1000.0, 1) if correct_rts else None
    return {
        "total_trials": total,
        "correct_trials": correct,
        "accuracy": (correct / total) if total else 0.0,
        "mean_correct_rt_ms": mean_correct_rt_ms,
        "timeout_count": timeouts,
    }


def summarize_stage_attempt(trials: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize one attempt of a training stage."""

    overall = summarize_trials(trials)
    pair_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"correct": 0, "total": 0})
    for trial in trials:
        pair_id = str(trial.get("pair_id", "")).strip().upper()
        if not pair_id:
            continue
        pair_counts[pair_id]["total"] += 1
        if bool(trial.get("response_correct")):
            pair_counts[pair_id]["correct"] += 1

    pair_accuracy: dict[str, float] = {}
    for pair_id, counts in pair_counts.items():
        total = counts["total"]
        pair_accuracy[pair_id] = (counts["correct"] / total) if total else 0.0

    perfect = overall["correct_trials"] == overall["total_trials"] and overall["total_trials"] > 0
    return {
        **overall,
        "pair_accuracy": pair_accuracy,
        "perfect": perfect,
    }


def format_pair_accuracy_lines(summary: dict[str, Any]) -> str:
    """Render pair accuracy into a compact multi-line summary."""

    pair_accuracy = dict(summary.get("pair_accuracy", {}) or {})
    if not pair_accuracy:
        return "No pair data."

    lines: list[str] = []
    for pair_id in PAIR_ORDER:
        if pair_id in pair_accuracy:
            lines.append(f"{pair_id}: {pair_accuracy[pair_id] * 100:.0f}%")

    for pair_id, acc in pair_accuracy.items():
        if pair_id not in PAIR_ORDER:
            lines.append(f"{pair_id}: {acc * 100:.0f}%")

    return "   ".join(lines)
