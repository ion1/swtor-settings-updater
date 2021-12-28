# `swtor-settings-updater` Change Log

## UNRELEASED

- [README](README.md): Avoid shadowing a variable in the example.
- `character`: Normalize the server ID to lower case.

## [v0.0.6](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.6) – 2021-12-28

- `character` `update_all`: Missed a case-insensitive "HE" prefix.

## [v0.0.5](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.5) – 2021-12-28

- Case-insensitive "HE" prefix for PlayerGUIState.ini files.

## [v0.0.4](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.4) – 2020-08-22

- `Character` no longer needs to be a class. Change the methods to functions.

## [v0.0.3](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.3) – 2020-08-22

- Pass the character metadata to the update callback as a data class object.
- Support multiple environments (both live and PTS).
- Use pathlib internally.
  - Replace the `SETTINGS_DIR` constant with a `default_settings_dir` function.
- Type check the code with mypy.
- Lint the code with flake8.

## [v0.0.2](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.2) – 2020-07-30

- [README](README.md) updates.
- character: Do not leave a `.new` file behind if encoding/writing fails.

## [v0.0.1](https://github.com/ion1/swtor-settings-updater/releases/tag/v0.0.1) – 2020-07-22

Initial release.
