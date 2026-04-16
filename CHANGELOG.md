# CHANGELOG

## [v0.1.0-dev] - 2026-04-17

### Added

- Built an acquired-equivalence task with face cues, paired fish choices, repeat-until-criterion training, and a final transfer test.
- Added generated face and fish reference assets for the cue/choice display.
- Added deterministic stage scheduling, QA/sim profiles, and a stage-aware simulation responder.
- Added reference artifacts, plot artifacts, and PsyFlow/TAPS metadata for publishing.

### Changed

- Replaced the inherited transitive-inference scaffold with acquired-equivalence stage logic and transfer probes.
- Switched the task documentation, manifest, and config bundle to the new task identity and asset map.

### Fixed

- Aligned the audit, runtime, and trigger labels for the new choice-display flow.
