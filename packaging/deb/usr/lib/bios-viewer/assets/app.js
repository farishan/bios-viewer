
/* BIOS Viewer UI (monokit design system). */
(function () {
  "use strict";

  const send = (action, payload) => {
    const msg = JSON.stringify({ action: action, payload: payload || {} });
    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nativeApp) {
      window.webkit.messageHandlers.nativeApp.postMessage(msg);
    } else {
      console.warn("native bridge unavailable:", msg);
    }
  };

  window.nativeAppReceive = function (reply) {
    if (!reply || !reply.ok) { console.error("bridge error:", reply); return; }
    const r = reply.result || {};
    if (r.identity) renderIdentity(r.identity);
    if (r.settings) renderSettings(r.settings);
    if (r.security) renderSecurity(r.security);
    if (r.boot) renderBoot(r.boot);
    if (r.ec) renderEc(r.ec);
    if (r.firmware) renderFirmware(r.firmware);
    if (r.version) {
      const lbl = document.getElementById("versionLabel");
      if (lbl) lbl.textContent = "v" + r.version;
    }
  };

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function panel(name) { return document.querySelector('.panel[data-p="' + name + '"]'); }

  function kvCard(title, obj) {
    const card = el("div", "card");
    card.appendChild(el("h3", null, title));
    const list = el("div", "list");
    Object.keys(obj).forEach((k) => {
      const row = el("div");
      row.appendChild(el("span", null, k));
      const v = el("span", "muted", String(obj[k]));
      row.appendChild(v);
      list.appendChild(row);
    });
    card.appendChild(list);
    return card;
  }

  function renderIdentity(data) {
    const p = panel("identity"); p.innerHTML = "";
    p.appendChild(kvCard("Identity", data));
  }

  function renderSettings(data) {
    const p = panel("settings"); p.innerHTML = "";
    const card = el("div", "card");
    card.appendChild(el("h3", null, "BIOS Settings (" + (data.settings || []).length + ")"));
    const info = el("div", "list");
    const pr = (data.special || {}).pending_reboot;
    const ss = (data.special || {}).save_settings;
    const r1 = el("div"); r1.appendChild(el("span", null, "pending_reboot")); r1.appendChild(el("span", "muted", pr != null ? pr : "n/a")); info.appendChild(r1);
    const r2 = el("div"); r2.appendChild(el("span", null, "save_settings")); r2.appendChild(el("span", "muted", ss != null ? ss : "n/a")); info.appendChild(r2);
    card.appendChild(info);

    const filterWrap = el("div", "row");
    const input = el("input", "in");
    input.type = "text"; input.placeholder = "Filter settings...";
    input.style.maxWidth = "360px";
    filterWrap.appendChild(input);
    card.appendChild(filterWrap);

    const wrap = el("div", "scroll");
    const table = el("table");
    const thead = el("thead");
    const hr = el("tr");
    ["Name", "Display", "Type", "Current", "Possible values"].forEach((h) => hr.appendChild(el("th", null, h)));
    thead.appendChild(hr); table.appendChild(thead);
    const tbody = el("tbody"); table.appendChild(tbody);
    wrap.appendChild(table); card.appendChild(wrap);
    p.appendChild(card);

    function draw(filter) {
      tbody.innerHTML = "";
      (data.settings || []).forEach((s) => {
        const hay = (s.name + " " + (s.display_name || "")).toLowerCase();
        if (filter && !hay.includes(filter.toLowerCase())) return;
        const tr = el("tr");
        tr.appendChild(el("td", null, s.name));
        tr.appendChild(el("td", null, s.display_name || s.name));
        tr.appendChild(el("td", null, s.type));
        const cur = s.value_readable ? s.current_value : "auth required";
        const td = el("td", null, cur);
        if (!s.value_readable) td.classList.add("muted");
        tr.appendChild(td);
        tr.appendChild(el("td", null, (s.possible_values || []).join(", ")));
        tbody.appendChild(tr);
      });
    }
    draw("");
    input.addEventListener("input", () => draw(input.value));
  }

  function renderSecurity(data) {
    const p = panel("security"); p.innerHTML = "";
    if (data.error) {
      const card = el("div", "card");
      card.appendChild(el("h3", null, "Security (HSI)"));
      card.appendChild(el("p", "muted", "Error: " + data.error));
      p.appendChild(card); return;
    }
    const card = el("div", "card");
    card.appendChild(el("h3", null, "Host Security (HSI)"));
    const wrap = el("div", "scroll");
    const table = el("table");
    const thead = el("thead"); const hr = el("tr");
    ["Name", "Result", "Summary"].forEach((h) => hr.appendChild(el("th", null, h)));
    thead.appendChild(hr); table.appendChild(thead);
    const tbody = el("tbody");
    (data.attributes || []).forEach((a) => {
      const tr = el("tr");
      tr.appendChild(el("td", null, a.name));
      const res = a.hsi_result || "";
      const good = (res === "valid" || res === "enabled" || res === "not-tainted" || res === "locked");
      const td = el("td"); const b = el("span", "badge" + (good ? " solid" : ""), res); td.appendChild(b); tr.appendChild(td);
      tr.appendChild(el("td", null, a.summary || ""));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody); wrap.appendChild(table); card.appendChild(wrap); p.appendChild(card);

    if (data.events && data.events.length) {
      const card2 = el("div", "card");
      card2.appendChild(el("h3", null, "Security Events"));
      const wrap2 = el("div", "scroll");
      const table2 = el("table");
      const thead2 = el("thead"); const hr2 = el("tr");
      ["When", "Name", "Result"].forEach((h) => hr2.appendChild(el("th", null, h)));
      thead2.appendChild(hr2); table2.appendChild(thead2);
      const tbody2 = el("tbody");
      data.events.forEach((e) => {
        const tr = el("tr");
        tr.appendChild(el("td", null, e.created ? new Date(e.created * 1000).toISOString().slice(0,19).replace("T"," ") : ""));
        tr.appendChild(el("td", null, e.name || ""));
        tr.appendChild(el("td", null, e.result || ""));
        tbody2.appendChild(tr);
      });
      table2.appendChild(tbody2); wrap2.appendChild(table2); card2.appendChild(wrap2); p.appendChild(card2);
    }
  }

  function renderBoot(data) {
    const p = panel("boot"); p.innerHTML = "";
    const card = el("div", "card");
    card.appendChild(el("h3", null, "Boot Configuration"));
    const list = el("div", "list");
    [["BootCurrent", data.boot_current], ["SecureBoot", data.secure_boot], ["Timeout", data.timeout]].forEach(([k, v]) => {
      const row = el("div"); row.appendChild(el("span", null, k)); row.appendChild(el("span", "muted", v || "n/a")); list.appendChild(row);
    });
    card.appendChild(list);
    const wrap = el("div", "scroll");
    const table = el("table");
    const thead = el("thead"); const hr = el("tr");
    ["ID", "Label", "Active"].forEach((h) => hr.appendChild(el("th", null, h)));
    thead.appendChild(hr); table.appendChild(thead);
    const tbody = el("tbody");
    (data.entries || []).forEach((e) => {
      const tr = el("tr");
      tr.appendChild(el("td", null, e.id));
      tr.appendChild(el("td", null, e.label));
      tr.appendChild(el("td", null, e.active ? "yes" : ""));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody); wrap.appendChild(table); card.appendChild(wrap); p.appendChild(card);
  }

  function renderEc(data) {
    const p = panel("ec"); p.innerHTML = "";
    if (!data.available) {
      const card = el("div", "card");
      card.appendChild(el("h3", null, "Embedded Controller"));
      card.appendChild(el("p", "muted", "thinkpad_acpi not available"));
      p.appendChild(card); return;
    }
    Object.keys(data.entries || {}).forEach((name) => {
      const card = el("div", "card");
      card.appendChild(el("h3", null, name));
      const list = el("div", "list");
      Object.keys(data.entries[name]).forEach((k) => {
        const row = el("div"); row.appendChild(el("span", null, k)); row.appendChild(el("span", "muted", data.entries[name][k])); list.appendChild(row);
      });
      card.appendChild(list); p.appendChild(card);
    });
  }

  function renderFirmware(data) {
    const p = panel("firmware"); p.innerHTML = "";
    const card = el("div", "card");
    card.appendChild(el("h3", null, "Firmware Devices"));
    const wrap = el("div", "scroll");
    const table = el("table");
    const thead = el("thead"); const hr = el("tr");
    ["Name", "Version", "Vendor"].forEach((h) => hr.appendChild(el("th", null, h)));
    thead.appendChild(hr); table.appendChild(thead);
    const tbody = el("tbody");
    (data.devices || []).forEach((d) => {
      const tr = el("tr");
      tr.appendChild(el("td", null, d.name || ""));
      tr.appendChild(el("td", null, d.version || ""));
      tr.appendChild(el("td", null, d.vendor || ""));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody); wrap.appendChild(table); card.appendChild(wrap); p.appendChild(card);

    if (data.history && data.history.length) {
      const card2 = el("div", "card");
      card2.appendChild(el("h3", null, "Update History"));
      const wrap2 = el("div", "scroll");
      const table2 = el("table");
      const thead2 = el("thead"); const hr2 = el("tr");
      ["Device", "Old", "New", "Result"].forEach((h) => hr2.appendChild(el("th", null, h)));
      thead2.appendChild(hr2); table2.appendChild(thead2);
      const tbody2 = el("tbody");
      data.history.forEach((h) => {
        const tr = el("tr");
        tr.appendChild(el("td", null, h.device || ""));
        tr.appendChild(el("td", null, h.old_version || ""));
        tr.appendChild(el("td", null, h.new_version || ""));
        tr.appendChild(el("td", null, h.result || ""));
        tbody2.appendChild(tr);
      });
      table2.appendChild(tbody2); wrap2.appendChild(table2); card2.appendChild(wrap2); p.appendChild(card2);
    }
  }

  function loadAll(readValues) {
    send("get_version", {});
    send("get_identity", {});
    send("get_settings", { read_values: readValues });
    send("get_security", {});
    send("get_boot", {});
    send("get_ec", {});
    send("get_firmware", {});
  }

  const refreshBtn = document.getElementById("refreshBtn");
  if (refreshBtn) refreshBtn.addEventListener("click", () => loadAll(document.getElementById("readValues").checked));
  const rv = document.getElementById("readValues");
  if (rv) rv.addEventListener("change", (e) => loadAll(e.target.checked));

  const themeBtn = document.getElementById("theme");
  if (themeBtn) themeBtn.addEventListener("click", () => {
    const r = document.documentElement;
    const dark = r.dataset.theme === "dark" || (!r.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
    r.dataset.theme = dark ? "light" : "dark";
  });

  loadAll(false);
})();
