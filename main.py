from contextlib import nullcontext
from pathlib import Path
import random

import pandas as pd
from psychopy import core

from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
    set_trial_context,
)

from src.run_trial import run_trial
from src.utils import (
    DEFAULT_BLOCK_REPEAT_LIMIT,
    DEFAULT_CONTINUE_KEY,
    build_session_plan,
    format_pair_accuracy_lines,
    summarize_stage_attempt,
    summarize_trials,
)

MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _attempt_rng(seed: int, block_idx: int, attempt_idx: int) -> random.Random:
    mixed = (
        (int(seed) + 1) * 1_000_003
        + (int(block_idx) + 1) * 10_009
        + (int(attempt_idx) + 1) * 97
    )
    return random.Random(mixed % (2**32))


def _show_text(
    stim_bank: StimBank,
    win,
    kb,
    runtime,
    stim_name: str,
    *,
    phase: str,
    trial_id: str,
    block_id: str,
    condition_id: str,
    valid_keys: list[str],
    task_factors: dict | None = None,
    **fmt_kwargs,
) -> None:
    unit = StimUnit(stim_name, win, kb, runtime=runtime).add_stim(
        stim_bank.get_and_format(stim_name, **fmt_kwargs)
    )
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=None,
        valid_keys=list(valid_keys),
        block_id=block_id,
        condition_id=condition_id,
        task_factors=task_factors or {},
        stim_id=stim_name,
    )
    unit.wait_and_continue(keys=list(valid_keys))


def _format_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _format_ms(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1f} ms"


def _run_stage_block(
    *,
    win,
    kb,
    settings,
    stim_bank: StimBank,
    trigger_runtime,
    block_plan: dict,
    all_data: list[dict],
    continue_key: list[str],
) -> None:
    block_kind = str(block_plan["block_kind"])
    stage_id = str(block_plan["stage_id"])
    block_label = str(block_plan["block_label"])
    block_idx = int(block_plan["block_idx"])
    block_id = str(block_plan["block_id"])
    trials_template = list(block_plan["trials"])
    required_streak = int(block_plan.get("required_consecutive_correct") or 0)
    repeat_limit = int(block_plan.get("repeat_limit") or DEFAULT_BLOCK_REPEAT_LIMIT)

    if block_kind == "training":
        current_streak = 0
        attempt_idx = 0
        while True:
            attempt_idx += 1
            attempt_block_id = f"{block_id}_attempt_{attempt_idx}"
            trigger_runtime.send(settings.triggers.get("block_onset"))
            _show_text(
                stim_bank,
                win,
                kb,
                trigger_runtime,
                "training_block_intro_text",
                phase="block_intro",
                trial_id=f"{attempt_block_id}_intro",
                block_id=attempt_block_id,
                condition_id=stage_id,
                valid_keys=continue_key,
                task_factors={
                    "stage_id": stage_id,
                    "block_kind": block_kind,
                    "block_label": block_label,
                    "block_idx": block_idx,
                    "block_attempt": attempt_idx,
                    "trial_count": len(trials_template),
                    "required_consecutive_correct": required_streak,
                    "current_streak": current_streak,
                },
                block_label=block_label,
                trial_count=len(trials_template),
                required_consecutive_correct=required_streak,
                current_streak=current_streak,
            )

            attempt_trials = list(trials_template)
            rng = _attempt_rng(getattr(settings, "overall_seed", 53053), block_idx, attempt_idx)
            rng.shuffle(attempt_trials)

            attempt_conditions = [{**trial_spec, "block_attempt": attempt_idx} for trial_spec in attempt_trials]
            attempt_block = (
                BlockUnit(
                    block_id=attempt_block_id,
                    block_idx=block_idx,
                    settings=settings,
                    window=win,
                    keyboard=kb,
                    n_trials=len(attempt_conditions),
                )
                .add_condition(attempt_conditions)
                .run_trial(
                    lambda win_arg, kb_arg, settings_arg, condition_arg: run_trial(
                        win_arg,
                        kb_arg,
                        settings_arg,
                        condition=condition_arg,
                        stim_bank=stim_bank,
                        trigger_runtime=trigger_runtime,
                        block_id=attempt_block_id,
                        block_idx=block_idx,
                    )
                )
            )
            attempt_results = attempt_block.get_all_data()
            all_data.extend(attempt_results)

            summary = summarize_stage_attempt(attempt_results)
            trigger_runtime.send(settings.triggers.get("block_end"))

            if summary["perfect"]:
                current_streak += len(attempt_results)
            else:
                current_streak = 0

            criterion_met = current_streak >= required_streak
            repeat_block = (not criterion_met) and (attempt_idx < repeat_limit)
            if criterion_met:
                repeat_message = (
                    f"{current_streak} consecutive correct responses reached. Continue to the next stage."
                )
            elif repeat_block:
                repeat_message = (
                    f"Current streak is {current_streak}/{required_streak}. The stage will repeat with the same cue set."
                )
            else:
                repeat_message = "Repeat limit reached. Continue to the next stage."

            _show_text(
                stim_bank,
                win,
                kb,
                trigger_runtime,
                "block_summary_text",
                phase="block_summary",
                trial_id=f"{attempt_block_id}_summary",
                block_id=attempt_block_id,
                condition_id=stage_id,
                valid_keys=continue_key,
                task_factors={
                    "stage_id": stage_id,
                    "block_kind": block_kind,
                    "block_label": block_label,
                    "block_idx": block_idx,
                    "block_attempt": attempt_idx,
                    "current_streak": current_streak,
                    "required_consecutive_correct": required_streak,
                    "criterion_met": criterion_met,
                    "accuracy": summary["accuracy"],
                    "repeat_message": repeat_message,
                    "timeout_count": summary["timeout_count"],
                },
                block_label=block_label,
                current_streak=current_streak,
                required_consecutive_correct=required_streak,
                accuracy_pct=_format_pct(summary["accuracy"]),
                pair_accuracy_lines=format_pair_accuracy_lines(summary),
                repeat_message=repeat_message,
            )

            if not repeat_block:
                break
    else:
        trigger_runtime.send(settings.triggers.get("block_onset"))
        _show_text(
            stim_bank,
            win,
            kb,
            trigger_runtime,
            "test_block_intro_text",
            phase="block_intro",
            trial_id=f"{block_id}_intro",
            block_id=block_id,
            condition_id=stage_id,
            valid_keys=continue_key,
            task_factors={
                "stage_id": stage_id,
                "block_kind": block_kind,
                "block_label": block_label,
                "block_idx": block_idx,
                "trial_count": len(trials_template),
            },
            block_label=block_label,
            trial_count=len(trials_template),
        )

        attempt_trials = list(trials_template)
        rng = _attempt_rng(getattr(settings, "overall_seed", 53053), block_idx, 1)
        rng.shuffle(attempt_trials)

        test_conditions = [{**trial_spec, "block_attempt": 1} for trial_spec in attempt_trials]
        test_block = (
            BlockUnit(
                block_id=block_id,
                block_idx=block_idx,
                settings=settings,
                window=win,
                keyboard=kb,
                n_trials=len(test_conditions),
            )
            .add_condition(test_conditions)
            .run_trial(
                lambda win_arg, kb_arg, settings_arg, condition_arg: run_trial(
                    win_arg,
                    kb_arg,
                    settings_arg,
                    condition=condition_arg,
                    stim_bank=stim_bank,
                    trigger_runtime=trigger_runtime,
                    block_id=block_id,
                    block_idx=block_idx,
                )
            )
        )
        all_data.extend(test_block.get_all_data())

        trigger_runtime.send(settings.triggers.get("block_end"))


def run(options):
    """Run the acquired-equivalence task in human, QA, or sim mode."""

    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))

    output_dir: Path | None = None
    runtime_scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        if options.mode == "qa":
            subject_data = {"subject_id": "qa"}
        elif options.mode == "sim":
            participant_id = "sim"
            if runtime_ctx is not None and runtime_ctx.session is not None:
                participant_id = str(runtime_ctx.session.participant_id or "sim")
            subject_data = {"subject_id": participant_id}
        else:
            subform = SubInfo(cfg["subform_config"])
            subject_data = subform.collect()

        settings = TaskSettings.from_dict(cfg["task_config"])
        if options.mode in ("qa", "sim") and output_dir is not None:
            settings.save_path = str(output_dir)
        settings.add_subinfo(subject_data)

        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")
        elif options.mode == "sim" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "sim_trace.csv")
            settings.log_file = str(output_dir / "sim_psychopy.log")
            settings.json_file = str(output_dir / "sim_settings.json")

        settings.triggers = cfg["trigger_config"]
        trigger_runtime = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(cfg)

        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, cfg["stim_config"]).preload_all()
        settings.save_to_json()

        continue_key = [str(getattr(settings, "continue_key", DEFAULT_CONTINUE_KEY)).strip().lower()]

        trigger_runtime.send(settings.triggers.get("exp_onset"))
        _show_text(
            stim_bank,
            win,
            kb,
            trigger_runtime,
            "instruction_text",
            phase="instruction",
            trial_id="instruction",
            block_id="instruction",
            condition_id="instruction",
            valid_keys=continue_key,
            task_factors={
                "stage_id": "instruction",
                "task_name": str(getattr(settings, "task_name", "Acquired Equivalence Task")),
            },
        )

        session_plan = build_session_plan(settings)
        all_data: list[dict] = []

        for block_plan in session_plan:
            _run_stage_block(
                win=win,
                kb=kb,
                settings=settings,
                stim_bank=stim_bank,
                trigger_runtime=trigger_runtime,
                block_plan=block_plan,
                all_data=all_data,
                continue_key=continue_key,
            )

        total_summary = summarize_trials(all_data)
        trigger_runtime.send(settings.triggers.get("good_bye_onset"))
        _show_text(
            stim_bank,
            win,
            kb,
            trigger_runtime,
            "good_bye_text",
            phase="good_bye",
            trial_id="good_bye",
            block_id="good_bye",
            condition_id="good_bye",
            valid_keys=continue_key,
            task_factors={
                "stage_id": "good_bye",
                "overall_accuracy": total_summary["accuracy"],
                "mean_correct_rt_ms": total_summary["mean_correct_rt_ms"],
                "timeout_count": total_summary["timeout_count"],
            },
            overall_accuracy_pct=_format_pct(total_summary["accuracy"]),
            mean_correct_rt_ms=_format_ms(total_summary["mean_correct_rt_ms"]),
            timeout_count=int(total_summary["timeout_count"]),
        )

        trigger_runtime.send(settings.triggers.get("exp_end"))
        pd.DataFrame(all_data).to_csv(settings.res_file, index=False)

        trigger_runtime.close()
        core.quit()


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = parse_task_run_options(
        task_root=task_root,
        description="Run task in human/qa/sim mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )
    run(options)


if __name__ == "__main__":
    main()
