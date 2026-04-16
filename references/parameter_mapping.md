# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `task_name` | `task.task_name` | `Acquired Equivalence Task` | `W2036460152` | Acquired-equivalence learning and transfer structure; task label is implementation metadata. | `direct` | Human-readable task title. |
| `save_path` | `task.save_path` | `./outputs/human` | `W2036460152` | Runtime output location is implementation metadata. | `direct` | QA/sim configs swap this path. |
| `total_blocks` | `task.total_blocks` | `4` | `W2036460152` | Three training stages plus one transfer test phase. | `adapted` | Nominal stage count, not repeat attempts. |
| `total_trials` | `task.total_trials` | `208` | `W2036460152` | Maximum of 32 + 64 + 96 + 16 trials if each training stage reaches its repeat limit. | `inferred` | Safe upper bound for the full schedule. |
| `trial_per_block` | `task.trial_per_block` | `16` | `W2036460152` | Final transfer block contains 16 display types; the last training stage also reaches 12. | `adapted` | Matches the largest within-attempt block. |
| `conditions` | `task.conditions` | `['stage1_training', 'stage2_training', 'stage3_training', 'transfer_test']` | `W2036460152` | Stage-based acquired-equivalence learning plus transfer probe. | `adapted` | Condition labels match the stage blocks. |
| `left_key` | `task.left_key` | `z` | `W2036460152` | Left/right choice mapping is implementation-specific, but fixed and config-driven. | `direct` | |
| `right_key` | `task.right_key` | `m` | `W2036460152` | Left/right choice mapping is implementation-specific, but fixed and config-driven. | `direct` | |
| `continue_key` | `task.continue_key` | `space` | `W2036460152` | Instruction and block-intro screens require a continue key. | `direct` | |
| `face_assets` | `task.face_assets` | `{'A1': 'face_A1', 'A2': 'face_A2', 'B1': 'face_B1', 'B2': 'face_B2'}` | `W2036460152` | Face-cue categories used to establish the equivalence classes. | `adapted` | Generated face icons are task-specific assets. |
| `fish_assets` | `task.fish_assets` | `{'X1': 'fish_X1', 'X2': 'fish_X2', 'Y1': 'fish_Y1', 'Y2': 'fish_Y2'}` | `W2036460152` | Fish-choice categories used for the learned associations and transfer probes. | `adapted` | Generated fish icons are task-specific assets. |
| `stage_required_consecutive_correct` | `task.stage_required_consecutive_correct` | `{'stage1_training': 8, 'stage2_training': 8, 'stage3_training': 12}` | `W2036460152` | Stage progression is repeated until the relevant streak criterion is met; exact counts are protocol-adapted. | `inferred` | Stage 1 needs 8 streaked correct responses across two 4-trial attempts. |
| `block_repeat_limit` | `task.block_repeat_limit` | `8` | `W2036460152` | The stage blocks can repeat if the criterion is not met. | `inferred` | Matches the repeat limit used in the source protocol. |
| `overall_seed` | `task.overall_seed` | `53053` | `W2036460152` | Deterministic seed used for reproducible trial ordering. | `inferred` | Derived from task id. |
| `seed_mode` | `task.seed_mode` | `same_across_sub` | `W2036460152` | Deterministic scheduling is used for auditability. | `adapted` | |
| `response_window_s` | `task.response_window_s` | `3.0` | `W1535087671` | Human generalization tasks use a short response window compatible with forced-choice learning. | `adapted` | |
| `fixation_duration_s` | `task.fixation_duration_s` | `0.4` | `W1535087671` | Short fixation interval used between trials. | `adapted` | |
| `feedback_duration_s` | `task.feedback_duration_s` | `0.8` | `W1535087671` | Brief training feedback interval. | `adapted` | Training only. |
| `iti_duration_s` | `task.iti_duration_s` | `0.4` | `W1535087671` | Short inter-trial interval keeps the learning loop compact. | `adapted` | |
| `language` | `task.language` | `English` | `W2036460152` | Participant-facing text is English in this repo. | `direct` | |
| `voice_name` | `task.voice_name` | `en-US-AriaNeural` | `W2036460152` | Voice setting is retained for compatibility with text-to-voice support. | `direct` | Disabled in this task. |
| `voice_enabled` | `task.voice_enabled` | `False` | `W2036460152` | No spoken instructions are required. | `direct` | |
| `input_mode` | `task.input_mode` | `keyboard` | `W2036460152` | The task uses keyboard responses. | `direct` | |
| `hide_cursor` | `task.hide_cursor` | `True` | `W2036460152` | Cursor hiding is standard for full-screen behavioral tasks. | `direct` | |
| `force_quit_enabled` | `task.force_quit_enabled` | `True` | `W2036460152` | Standard escape hatch for development and safety. | `direct` | |
| `force_quit_shortcut` | `task.force_quit_shortcut` | `ctrl+q` | `W2036460152` | Standard force-quit shortcut for the PsyFlow task suite. | `direct` | |
| `enable_logging` | `task.enable_logging` | `True` | `W2036460152` | Logging is required for auditability. | `direct` | |
| `choice_onset` | `triggers.map.choice_onset` | `21` | `W2090075044` | Choice onset marks the face-plus-fish decision screen. | `adapted` | Trigger semantics are implementation-defined. |
| `feedback_onset` | `triggers.map.feedback_onset` | `34` | `W2090075044` | Training feedback follows choice on the learning stages. | `adapted` | |
| `trial_fixation_onset` | `triggers.map.trial_fixation_onset` | `20` | `W2090075044` | Short pre-choice fixation is part of the trial loop. | `adapted` | |
| `trial_iti_onset` | `triggers.map.trial_iti_onset` | `35` | `W2090075044` | ITI separates consecutive trials. | `adapted` | |
| `block_onset` | `triggers.map.block_onset` | `10` | `W2036460152` | Stage blocks are repeated attempts until criterion. | `adapted` | |
| `block_end` | `triggers.map.block_end` | `11` | `W2036460152` | Marks completion of each block attempt. | `adapted` | |
| `good_bye_onset` | `triggers.map.good_bye_onset` | `40` | `W2036460152` | Closing screen for the completed task. | `direct` | |
