# Acquired Equivalence Task

| Field | Value |
|---|---|
| Name | Acquired Equivalence Task |
| Version | v0.1.0-dev |
| URL / Repository | [TaskBeacon/T000053-acquired-equivalence-task](https://github.com/TaskBeacon/T000053-acquired-equivalence-task) |
| Short Description | Face-cue / fish-choice acquired-equivalence task with staged learning, repeat-until-criterion training, and a final transfer test |
| Created By | TaskBeacon build pipeline |
| Date Updated | 2026-04-17 |
| PsyFlow Version | 0.1.12 |
| PsychoPy Version | 2025.2.4 |
| Modality | Behavior |
| Language | English |

## 1. Task Overview

This task implements a classic acquired-equivalence paradigm in PsychoPy/PsyFlow. Participants learn which fish goes with each face across three training stages. New faces that share the same learned outcomes are introduced in later stages, and the final transfer test checks whether participants generalize the learned associations to the novel equivalence-consistent pairings.

The runtime keeps the execution auditable. Trial order is deterministic from the task seed, the left/right fish order is counterbalanced within each stage, and training feedback is limited to the learning stages. The task uses generated face and fish reference assets and does not require external licensed media.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Description |
|---|---|
| Load Config | Read the mode-specific config and task metadata. |
| Collect Subject Info | Collect subject ID in human mode or inject deterministic IDs in QA/sim. |
| Initialize Runtime | Create the PsychoPy window, keyboard, triggers, and stimulus bank. |
| Show Instructions | Present the acquired-equivalence instructions and response-key mapping. |
| Run Stage 1 | Train the first face-fish mappings until the streak criterion is met. |
| Run Stage 2 | Add the second face variants while retaining the earlier mappings. |
| Run Stage 3 | Add the second fish set while retaining the earlier face-fish mappings. |
| Run Transfer Test | Present the retained and novel transfer probes with no feedback. |
| Finish | Present the goodbye screen, send the end trigger, and quit PsychoPy. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Trial Fixation | Show a centered fixation cross for a short pre-choice interval. |
| Face and Fish Display | Show one face cue near the top and two fish choices lower left/right. |
| Choice Response | Collect `Z` for left or `M` for right within the response window. |
| Training Feedback | Show correctness feedback only during the training stages. |
| Trial ITI | Show the fixation cross again before the next trial. |

### Controller Logic

| Feature | Description |
|---|---|
| Condition Scheduling | `build_session_plan(...)` expands the stage templates into ordered trial lists for Stage 1, Stage 2, Stage 3, and the transfer test. |
| Determinism | Trial order is deterministic from the overall seed, block index, and attempt index. |
| Criterion Control | Training stages repeat until the required consecutive-correct streak is reached or the repeat limit is hit. |
| Trial Context | Every participant-visible phase in `src/run_trial.py` calls `set_trial_context(...)` before display or response capture. |
| Simulation | The scripted and sampler responders exercise the response path with high-accuracy training behavior and slightly lower transfer-probe accuracy. |

## 3. Configuration Summary

| Setting | Value |
|---|---|
| Subject Info | `subject_id` collected as a 3-digit integer in human mode. |
| Window | `1280 x 720`, black background, `pix` units, fullscreen off. |
| Stimuli | Config-defined instruction text, fixation, feedback, block-intro text, and generated face/fish PNG assets. |
| Timing | Fixation `0.4 s`, response window `3.0 s`, feedback `0.8 s`, ITI `0.4 s`. |
| Triggers | Experiment, block, choice, response, feedback, ITI, and goodbye triggers are mapped in `config/*.yaml`. |
| Adaptive Controller | Stage 1 requires `8` consecutive correct responses, Stage 2 requires `8`, and Stage 3 requires `12`; training blocks repeat up to `8` attempts. |

### a. Subject Info

`subject_id` is collected as a 3-digit integer in human mode.

### b. Window Settings

`1280 x 720`, black background, `pix` units, fullscreen off.

### c. Stimuli

Config-defined instruction text, fixation, feedback, block-intro text, and generated face/fish PNG assets.

### d. Timing

Fixation `0.4 s`, response window `3.0 s`, feedback `0.8 s`, ITI `0.4 s`.

## 4. Methods (for academic publication)

Participants complete an acquired-equivalence learning task with face cues and paired fish choices. The task is organized into three training stages and a final transfer test. Early stages establish the associative structure and introduce additional faces or fish while retaining earlier pairings; the final test probes whether learning generalizes to the novel transfer-consistent pairings.

The implementation is designed for reproducibility and auditability. Trial order, left/right response order, and stage repetition are deterministic given the task seed, and the participant-facing text remains config-driven for localization portability.
