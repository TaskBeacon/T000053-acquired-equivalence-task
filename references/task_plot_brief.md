# Task Plot Brief

- Task: Acquired Equivalence Task
- Figure title: Acquired Equivalence Task
- Subtitle: Construct: relational learning / equivalence-class formation / transfer inference
- Source priority: `README.md`, `config/config.yaml`, `src/run_trial.py`, `references/task_logic_audit.md`.

## Timeline Rows

1. Stage 1 training
2. Stage 2 training
3. Stage 3 training
4. Transfer test

## Trial Flow

Training trial:

1. Trial fixation, 400 ms.
2. Choice display, 3000 ms: one face cue and two fish choices.
3. Participant presses `Z` for the left fish or `M` for the right fish.
4. Training feedback, 800 ms: Correct / Incorrect / Too slow.
5. ITI, 400 ms.

Transfer test trial:

1. Trial fixation, 400 ms.
2. Choice display, 3000 ms: one face cue and two fish choices.
3. Participant presses `Z` for the left fish or `M` for the right fish.
4. No feedback.
5. ITI, 400 ms.

## Conditions

- Stage 1 trains initial face-fish mappings and requires 8 consecutive correct responses.
- Stage 2 expands equivalence with additional faces and requires 8 consecutive correct responses.
- Stage 3 adds the second fish set and requires 12 consecutive correct responses.
- Transfer test presents retained and novel equivalence-consistent probes without feedback.
- Training stages can repeat up to 8 attempts.
