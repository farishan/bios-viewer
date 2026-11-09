# Platform support

## Target

- Ubuntu 22.04 LTS and newer
- X11 session (`XDG_SESSION_TYPE=x11`)
- Python 3.10+
- GTK 3.24+ (`libgtk-3-0`, `gir1.2-gtk-3.0`)
- WebKit2GTK 4.0 (`libwebkit2gtk-4.0-37`, `gir1.2-webkit2-4.0`)

## Wayland

On GNOME/Wayland, X11 window hints (desktop type, keep-below) are ignored
by Mutter. The starter still runs, but desktop-widget features will not
work. For Wayland-only desktop widgets use a GNOME Shell extension (GJS) or
a layer-shell client. See `topics/ubuntu-desktop-widget` research.