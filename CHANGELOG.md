# Changelog

All notable changes to BIOS Viewer are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/), versioning: [SemVer](https://semver.org/).

## [0.2.0] - 2026-11-09

### Changed
- UI restyled with monokit design system (tokens, components, dark mode).
- Added versioning: --version/-V flag, get_version bridge action, footer version.

## [0.1.0] - 2026-11-09

### Added
- Initial release: read-only BIOS/firmware settings viewer for Linux (ThinkPad).
- Identity, BIOS Settings (77 ThinkLMI firmware-attributes), Security (HSI),
  Boot, Embedded Controller, Firmware tabs.
- Privileged current-value read via pkexec + fwupdmgr.
- Monokit design system for UI.
- pip, manual local (pip-free), and .deb installation methods.
- 11 GUI-free tests + CI.

### Notes
- Read-only by design; no BIOS writes.
