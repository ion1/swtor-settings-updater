# `swtor-settings-updater` Change Log

## Unreleased

* Pass the character metadata to the update callback as a data class object.
* Support multiple environments (both live and PTS).
* Use pathlib internally.
  * Replace the `SETTINGS_DIR` constant with a `default_settings_dir` function.
* Type check the code with mypy.
* Lint the code with flake8.

## [v0.0.2](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.2) – 2020-07-30

* [README](README.md) updates.
* character: Do not leave a `.new` file behind if encoding/writing fails.

## [v0.0.1](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.1) – 2020-07-22

Initial release.
