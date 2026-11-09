# Architecture — BIOS Viewer

## Layers

1. **Config** (`config.py`) — dataclass built from environment variables.
   No global mutable state.
2. **Platform** (`platform.py`) — read-only detection of X11/Wayland.
3. **Bridge** (`bridge.py`) — validated JSON dispatch between the webview
   and Python. Only registered actions are callable; no arbitrary eval.
4. **Webview** (`webview.py`) — WebKit2 4.0 view + user content manager.
5. **Window** (`window.py`) — GTK application window hosting the webview.
6. **App** (`app.py`) — `Gtk.Application` lifecycle and wiring.

## Data flow

```
User clicks button in HTML
  -> app.js calls window.webkit.messageHandlers.nativeApp.postMessage(JSON)
  -> WebKit emits script-message-received
  -> MainWindow._on_web_message(raw)
  -> Bridge.dispatch(raw) validates + routes to handler
  -> handler returns result
  -> run_javascript pushes JSON reply into window.nativeAppReceive(reply)
```

## Threading

All GTK/WebKit calls happen on the main thread. Long-running work should be
offloaded to a worker thread/asyncio and marshalled back with `GLib.idle_add`.

## Security

- The bridge never evaluates arbitrary code from the UI.
- `allow_universal_access_from_file_urls` is disabled.
- File access from file URLs is allowed only for the bundled assets.