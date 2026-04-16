# Task Plot Audit

- generated_at: 2026-04-17T03:08:53.5231563+08:00
- mode: existing
- task_path: E:\Taskbeacon\T000053-acquired-equivalence-task

## 1. Inputs and provenance

- E:\Taskbeacon\T000053-acquired-equivalence-task\README.md
- E:\Taskbeacon\T000053-acquired-equivalence-task\config\config.yaml
- E:\Taskbeacon\T000053-acquired-equivalence-task\src\run_trial.py
- E:\Taskbeacon\T000053-acquired-equivalence-task\references\plot_assets\choice_stage1.png
- E:\Taskbeacon\T000053-acquired-equivalence-task\references\plot_assets\choice_stage2.png
- E:\Taskbeacon\T000053-acquired-equivalence-task\references\plot_assets\choice_stage3.png
- E:\Taskbeacon\T000053-acquired-equivalence-task\references\plot_assets\choice_transfer.png

## 2. Evidence extracted from README

- Stage 1, Stage 2, Stage 3, and a final transfer test are described as the main flow.
- Training stages use feedback after each choice.
- The transfer test skips feedback.
- Response mapping is `Z` for left and `M` for right.

## 3. Evidence extracted from config/source

- `stage1_training`: fixation 400 ms, choice 3 s response window, feedback 800 ms, ITI 400 ms.
- `stage2_training`: same flow, with the stage 2 composite choice screenshot.
- `stage3_training`: same flow, with the stage 3 composite choice screenshot.
- `transfer_test`: fixation 400 ms, choice 3 s response window, ITI 400 ms; no feedback screen.
- The choice display is representative and uses stage-specific face/fish combinations with randomized left/right order at runtime.

## 4. Mapping to task_plot_spec

- root_key: task_plot_spec
- spec_version: 0.2
- one timeline per stage
- four timelines total
- four screens for each training timeline
- three screens for the transfer timeline

## 5. Style decision and rationale

- A four-timeline collection was used so the stage progression stays visible instead of collapsing into a single representative row.
- `auto_width` was disabled so the renderer uses the full 16-inch canvas and keeps labels readable across four timelines.

## 6. Rendering parameters and constraints

- output_file: task_flow.png
- dpi: 300
- max_conditions: 4
- screens_per_timeline: 4
- screen_overlap_ratio: 0.1
- screen_slope: 0.08
- screen_slope_deg: 25.0
- screen_aspect_ratio: 1.4545454545454546
- auto_width: false
- validator_warnings: none

## 7. Output files and checksums

- E:\Taskbeacon\T000053-acquired-equivalence-task\references\task_plot_spec.yaml: sha256=46C1FB827FB7D997C65B08C78DD22836D3BFEC7C1FF5A0C3A9FB15AD75BFDFFB
- E:\Taskbeacon\T000053-acquired-equivalence-task\references\task_plot_spec.json: sha256=DE96B27DBEA838F4CD0DD5A455E1FA0CEB62FA62FB9529CBC1D86F24985F2AED
- E:\Taskbeacon\T000053-acquired-equivalence-task\references\task_plot_source_excerpt.md: sha256=F4E1194D50E1247F3B659ECB94E3F129D1C646ED7BD54667F0DF6956992470CB
- E:\Taskbeacon\T000053-acquired-equivalence-task\task_flow.png: sha256=627D4D1A14794AB83110C3DA19EA2600204577C401AF4CF0E9424BE77F8FC376

## 8. Inferred/uncertain items

- The plotted choice screenshots are representative composites assembled from runtime face/fish assets for visual clarity.
- The transfer timeline uses a representative transfer probe layout; runtime order remains randomized across probes.
- `display_condition_note` wording was shortened to satisfy the renderer's note-length guardrails.
