# Task Logic Audit

## 1. Paradigm Intent

- Task: Acquired Equivalence Task
- Primary construct: relational learning, equivalence-class formation, and transfer inference
- Manipulated factors:
  - training stage
  - stimulus class membership
  - trained versus transfer probe status
  - left/right option order
- Dependent measures:
  - choice accuracy
  - response time
  - training-block criterion attainment
  - transfer accuracy on novel class-consistent versus class-inconsistent probes
- Key citations:
  - W2036460152, Hall (1996)
  - W1535087671, Wimmer, Daw, & Shohamy (2012)
  - W2001562084, Zeithamová, Schlichting, & Preston (2012)
  - W2090075044, Zeithamová, Dominick, & Preston (2012)

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 4 nominal phases
  - Stage 1 training
  - Stage 2 training
  - Stage 3 training
  - Final transfer test
- Trials per block:
  - Stage 1: 4 trial types per attempt
  - Stage 2: 8 trial types per attempt
  - Stage 3: 12 trial types per attempt
  - Transfer test: 16 trial types total, no feedback
- Randomization/counterbalancing:
  - Within each block attempt, left/right fish position is randomized per trial
  - Trial order within a block is randomized deterministically from the task seed
  - Transfer probes preserve the same deterministic randomization policy
- Condition weight policy:
  - `task.condition_weights` is not used; each block is generated from explicit stage-specific trial lists
  - Runtime resolution is not delegated to `TaskSettings.resolve_condition_weights()`
  - Even generation is achieved by explicit repeat counts per trial type
- Condition generation method:
  - Custom generator
  - The task needs stage-aware trial lists with retained prior pairings, which cannot be represented cleanly by a flat condition-label system alone
  - The generated data shape is a list of block dictionaries, each with `block_kind`, `block_idx`, `block_id`, `block_label`, `trials`, `trial_count`, `criterion_threshold`, and `pair_ids`
- Runtime-generated trial values:
  - Left/right choice order is generated at runtime for every trial
  - Block repetition decisions are generated at runtime from block accuracy
  - The RNG is seeded from the task seed, block index, trial index, and attempt index to keep results reproducible

### Trial State Machine

1. State name: `instruction`
   - Onset trigger: experiment onset
   - Stimuli shown: task instructions, response-key mapping, and short explanation of the face-to-fish learning rule
   - Valid keys: continue key
   - Timeout behavior: waits indefinitely for continue
   - Next state: `block_intro` for Stage 1

2. State name: `block_intro`
   - Onset trigger: block onset
   - Stimuli shown: stage-specific intro text for the current learning phase or transfer phase
   - Valid keys: continue key
   - Timeout behavior: waits indefinitely for continue
   - Next state: first trial fixation of the current block

3. State name: `trial_fixation`
   - Onset trigger: trial onset
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: fixed duration
   - Next state: `choice_display`

4. State name: `choice_display`
   - Onset trigger: choice onset
   - Stimuli shown: one face cue centered near the top, two fish options on the lower left and lower right, and a short prompt
   - Valid keys: left_key, right_key
   - Timeout behavior: response window ends as incorrect / no-response when no choice is made
   - Next state: `feedback` on training trials, `iti` on transfer trials

5. State name: `feedback`
   - Onset trigger: feedback onset
   - Stimuli shown: correctness feedback text or icon
   - Valid keys: none
   - Timeout behavior: fixed duration
   - Next state: `iti`

6. State name: `iti`
   - Onset trigger: ITI onset
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: fixed duration
   - Next state: next trial or block summary

7. State name: `block_summary`
   - Onset trigger: block end
   - Stimuli shown: summary of accuracy by pair and whether the criterion was met
   - Valid keys: continue key
   - Timeout behavior: waits indefinitely for continue
   - Next state: either repeat the current training block or advance to the next block

8. State name: `good_bye`
   - Onset trigger: experiment end
   - Stimuli shown: goodbye screen with overall summary
   - Valid keys: continue key
   - Timeout behavior: waits indefinitely for continue
   - Next state: end of session

## 3. Condition Semantics

For each condition token in `task.conditions`:

- Condition ID: `stage1_training`
  - Participant-facing meaning: initial learning of the first face-fish associations
  - Concrete stimulus realization (visual/audio): one face cue with a left/right fish choice; correct fish is reinforced
  - Outcome rules: training feedback follows the choice; wrong or missing responses are marked incorrect

- Condition ID: `stage2_training`
  - Participant-facing meaning: equivalence expansion using new faces that share the first learned outcomes
  - Concrete stimulus realization (visual/audio): one of the four stage-1 faces or the two new faces appears as the cue, with the retained fish pairings from stage 1 plus the new stage-2 pairings
  - Outcome rules: training feedback follows the choice; stage continues until the criterion is met or the repeat limit is reached

- Condition ID: `stage3_training`
  - Participant-facing meaning: learning a new fish set while keeping the previously learned face-outcome relations active
  - Concrete stimulus realization (visual/audio): familiar faces cue choice between the new fish pair
  - Outcome rules: training feedback follows the choice; stage continues until the criterion is met or the repeat limit is reached

- Condition ID: `transfer_test`
  - Participant-facing meaning: no-feedback transfer probes for the novel equivalence-consistent pairings
  - Concrete stimulus realization (visual/audio): the transfer-stage faces and fish appear with no correctness feedback
  - Outcome rules: responses are logged for transfer accuracy; no learning feedback is shown

Also document where participant-facing condition text/stimuli are defined:

- Participant-facing text source (config stimuli / code formatting / generated assets): config stimuli for instructions and block-intro text; generated reference assets for face and fish icons; code only formats trial-specific labels and pairings
- Why this source is appropriate for auditability: it keeps instructional wording in config, keeps stimulus assets versioned under the task repo, and allows the runtime to remain mode-agnostic
- Localization strategy (how language variants are swapped via config without code edits): participant-facing text lives in the config files, so a language change only swaps the config bundle and the font settings

## 4. Response and Scoring Rules

- Response mapping: left key chooses the left fish; right key chooses the right fish
- Response key source (config field vs code constant): config-driven via `task.left_key`, `task.right_key`, and `task.response_keys`
- If code-defined, why config-driven mapping is not sufficient: not needed; the task can remain config-driven
- Missing-response policy: no response within the response window counts as incorrect and is logged as a timeout
- Correctness logic: the correct fish depends on the stage-specific face cue and the currently active trial pairing
- Reward/penalty updates: none; only correctness feedback is shown on training trials
- Running metrics:
  - block accuracy
  - pair-specific accuracy
  - timeout count
  - mean correct RT
  - transfer-probe accuracy

## 5. Stimulus Layout Plan

For every screen with multiple simultaneous options/stimuli:

- Screen name: instruction screen
  - Stimulus IDs shown together: instruction text, response-key text, brief task summary
  - Layout anchors (`pos`): centered title, body text below, key mapping near the bottom
  - Size/spacing (`height`, width, wrap): title large; body text wrapped to a narrow column
  - Readability/overlap checks: separate text blocks vertically with ample wrap width
  - Rationale: instructions need to be readable before the first trial

- Screen name: choice display
  - Stimulus IDs shown together: one face cue and two fish options
  - Layout anchors (`pos`): face centered at `y > 0`; fish options placed lower left and lower right; prompt centered below the face
  - Size/spacing (`height`, width, wrap): face slightly larger than the fish options; fish options sized evenly; prompt text small enough to avoid crowding
  - Readability/overlap checks: keep the fish options at least one option-width apart and clear the face cue from the response area
  - Rationale: the face is the cue, while the fish options are the response choices

- Screen name: feedback screen
  - Stimulus IDs shown together: feedback text plus fixation
  - Layout anchors (`pos`): feedback centered
  - Size/spacing (`height`, width, wrap): one line or short paragraph
  - Readability/overlap checks: single focal element keeps the stage easy to audit
  - Rationale: feedback should be unambiguous and brief

- Screen name: block summary screen
  - Stimulus IDs shown together: summary text and pair-accuracy lines
  - Layout anchors (`pos`): title at top, summary lines centered beneath
  - Size/spacing (`height`, width, wrap): compact multiline text, no overlap
  - Readability/overlap checks: separate summary line block from the repeat-message line
  - Rationale: participants need to see which stage is repeating or advancing

## 6. Trigger Plan

Map each phase/state to trigger code and semantics.

- `exp_onset`: start of the task
- `instruction_onset`: instruction screen onset
- `block_onset`: start of each stage or transfer block
- `trial_fixation_onset`: fixation onset before the face cue
- `choice_onset`: choice display onset
- `response_left` / `response_right`: recorded when the participant selects the left or right fish
- `feedback_onset`: training feedback onset
- `trial_iti_onset`: ITI onset
- `block_end`: end of a completed attempt block
- `good_bye_onset`: goodbye screen onset
- `exp_end`: task termination

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style (simple single flow / helper-heavy / why): simple single flow in `human|qa|sim` mode, with a thin helper for text screens and a block runner
- `utils.py` used? yes
- If yes, exact purpose (adaptive controller / sequence generation / asset pool / other): block-and-trial sequence generation, stage summaries, and criterion checks
- Custom controller used? yes, but only for the learning-stage repeat-until-criterion logic
- If yes, why PsyFlow-native path is insufficient: the task needs stage-specific trial lists that grow across phases and repeat based on accuracy criterion, which is easier to audit in a small helper than via static block conditions alone
- Legacy/backward-compatibility fallback logic required? no
- If yes, scope and removal plan: n/a

## 8. Inference Log

List any inferred decisions not directly specified by references:

- Decision: Use a four-phase schedule with Stage 1, Stage 2, Stage 3, and a final transfer test
  - Why inference was required: the selected papers establish the acquired-equivalence and inference framework, but the exact stage count and block-repeat schedule need one concrete protocol to operationalize
  - Citation-supported rationale: the classical acquired-equivalence protocol paper uses a multi-stage face/fish schedule with repeated learning blocks and a transfer test; the selected papers support the human generalization/inference framing

- Decision: Keep the participant-facing stimuli as stylized face and fish drawings rather than photographic images
  - Why inference was required: the selected papers describe the stimulus classes and their roles, but not a single required rendering package
  - Citation-supported rationale: the paradigm depends on the relational mapping, not on a proprietary visual asset set

- Decision: Use deterministic trial randomization and deterministic left/right order assignment
  - Why inference was required: the papers describe the trial structure and outcome logic, but not the exact randomization seed policy
  - Citation-supported rationale: deterministic generation is compatible with the published stage logic and improves auditability

## Contract Note

- Participant-facing labels/instructions/options should be config-defined whenever possible.
- `src/run_trial.py` should not hardcode participant-facing text that would require code edits for localization.
