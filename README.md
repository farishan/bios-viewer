# BIOS Viewer

A **read-only BIOS/firmware settings viewer** for Linux machines that expose
the `firmware-attributes` sysfs class (notably Lenovo ThinkPad). Built on
the [ubuntu-native-app-starter](https://github.com/farishan/ubuntu-native-app-starter)
stack: **Python 3 + GTK 3 + WebKit2GTK 4.0**.

Verified on: ThinkPad T480, BIOS N24ET81W (1.56), Ubuntu 22.04.5 LTS,
X11, GNOME, Python 3.10, GTK 3.24.33, WebKit2GTK 4.0 (2.50.4).

## Why read-only?

BIOS changes can brick a machine or make it unbootable. This viewer **never
writes**. It aggregates runtime firmware info into one dashboard:

- **Identity** — DMI/SMBIOS machine & BIOS identity.
- **BIOS Settings** — all 77 ThinkLMI firmware-attributes (metadata
  world-readable; current values via polkit admin auth).
- **Security** — fwupd Host Security ID (HSI) levels + security events.
- **Boot** — UEFI boot entries + SecureBoot state.
- **Embedded Controller** — fan, thermals, bluetooth, hotkeys (thinkpad_acpi).
- **Firmware** — fwupd devices & update history.

## Quick start

```bash
git clone https://github.com/farishan/bios-viewer.git
cd bios-viewer
sudo apt install -y python3 python3-gi libgtk-3-0 libwebkit2gtk-4.0-37
PYTHONPATH=src python3 -m bios_viewer
```

For current BIOS values, check "Read current values (admin)" — triggers a
polkit authentication prompt.

## Installation

Three options (pick one):

### 1. pip (developer)
```bash
make install          # pip install --user .
bios-viewer
```

### 2. Manual local install (no pip, no sudo)
```bash
make install-local     # or: ./install.sh
bios-viewer           # ~/.local/bin must be on PATH
make uninstall-local   # to remove
```
Copies the package + assets into `~/.local/lib/bios-viewer` and creates a
wrapper + `.desktop` entry. No build step, no pip.

### 3. Debian package (system-wide, requires sudo)
```bash
make build-deb        # produces dist/bios-viewer_0.1.0_all.deb
sudo dpkg -i dist/bios-viewer_0.1.0_all.deb
sudo apt-get -f install   # pull in python3-gi, libwebkit2gtk-4.0-37, ...
```

## System dependencies

```bash
sudo apt install -y \
  python3 python3-gi python3-pytest \
  libgtk-3-dev libwebkit2gtk-4.0-dev
```

## Run / test

```bash
make run          # launch GUI
make test         # pytest (GUI-free)
make lint         # compileall
make smoke        # import smoke test
```

## Configuration

Environment variables (prefix `BIOS_VIEWER_`):

| Variable | Default | Description |
|---|---|---|
| `BIOS_VIEWER_TITLE` | `BIOS Viewer` | Window title |
| `BIOS_VIEWER_WIDTH` / `_HEIGHT` | `960` / `640` | Initial size |
| `BIOS_VIEWER_MIN_WIDTH` / `_HEIGHT` | `480` / `320` | Minimum size |
| `BIOS_VIEWER_MAXIMIZED` | `false` | Start maximized |
| `BIOS_VIEWER_DEVTOOLS` | `false` | Enable WebKit inspector |
| `BIOS_VIEWER_LOG_LEVEL` | `INFO` | Logging level |
| `BIOS_VIEWER_ASSETS` | bundled `assets/` | Path to web assets |

## Permissions

- Metadata (setting names, types, possible values) is world-readable.
- Current values require polkit admin auth (`org.freedesktop.fwupd.get-bios-settings`).
- Security/boot/EC/firmware data need no privilege.
- If no polkit agent is available, the viewer degrades to metadata-only.

## Security posture note

This machine reports **HSI:0! (low)**. TPM appears present to the kernel
(`/dev/tpm0`, tpm_version_major=2) but fwupd reports "Not found" — the
viewer reports this as-is without claiming the machine is TPM-less.

## License

GPL-3.0-or-later. See `LICENSE`.
