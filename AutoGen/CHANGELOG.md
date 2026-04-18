# Changelog

## [Unreleased]
### Added
- Implemented changes to the `separability_matrix` function in `astropy/modeling/separable.py` to correctly compute separability for nested `CompoundModels`.
- Added unit tests in `test_separability.py` to validate the functionality of the `separability_matrix` for various models, including basic separable models, nested `CompoundModels`, and complex models.

### Fixed
- Resolved the issue with incorrect separability computation when using nested `CompoundModels`.

## [Previous Versions]
- Placeholder for previous version changes.
