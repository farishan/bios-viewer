/* BIOS Viewer UI. */
(function () {
  "use strict";

  const tabs = document.querySelectorAll(".tab");
  const panes = document.querySelectorAll(".tabpane");
  tabs.forEach((t) => t.addEventListener("click", () => {
    tabs.forEach((x) => x.classList.remove("active"));
    panes.forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    document.getElementById(t.dataset.tab).classList.add("active");
  }));

  const out = {};
  function send(action, payload) {
    const msg = JSON.stringify({ action: action, payload: payload || {} });
    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nativeApp) {
      window.webkit.messageHandlers.nativeApp.postMessage(msg);
    } else {
      console.warn("native bridge unavailable:", msg);
    }
  }

  window.nativeAppReceive = function (reply) {
    if (!reply || !reply.ok) {
      console.error("bridge error:", reply);
      return;
    }
    const r = reply.result || {};
    if (r.identity) renderIdentity(r.identity);
    if (r.settings) renderSettings(r.settings);
    if (r.security) renderSecurity(r.security);
    if (r.boot) renderBoot(r.boot);
    if (r.ec) renderEc(r.ec);
    if (r.firmware) renderFirmware(r.firmware);
    if (r.pong) { /* noop */ }
  };

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function kv(container, obj) {
    const wrap = el("div", "card");
    const title = el("h2", null, "Identity");
    wrap.appendChild(title);
    const grid = el("div", "kv");
    Object.keys(obj).forEach((k) => {
      grid.appendChild(el("div", "k", k));
      grid.appendChild(el("div", "v", String(obj[k])));
    });
    wrap.appendChild(grid);
    container.appendChild(wrap);
  }

  function renderIdentity(data) {
    const c = document.getElementById("identity");
    c.innerHTML = "";
    kv(c, data);
  }

  let settingsData = null;
  function renderSettings(data) {
    settingsData = data;
    const c = document.getElementById("settings");
    c.innerHTML = "";
    const card = el("div", "card");
    card.appendChild(el("h2", null, "BIOS Settings (" + (data.settings || []).length + ")"));
    const special = data.special || {};
    const info = el("div", "kv");
    info.appendChild(el("div", "k", "pending_reboot"));
    info.appendChild(el("div", "v", special.pending_reboot != null ? special.pending_reboot : "n/a"));
    info.appendChild(el("div", "k", "save_settings"));
    info.appendChild(el("div", "v", special.save_settings != null ? special.save_settings : "n/a"));
    card.appendChild(info);

    const filterWrap = el("div", "filter");
    const input = el("input");
    input.type = "text";
    input.placeholder = "Filter settings...";
    filterWrap.appendChild(input);
    card.appendChild(filterWrap);

    const table = el("table");
    const thead = el("thead");
    const hr = el("tr");
    ["Name", "Display", "Type", "Current", "Possible values"].forEach((h) => {
      const th = el("th", null, h);
      hr.appendChild(th);
    });
    thead.appendChild(hr);
    table.appendChild(thead);
    const tbody = el("tbody");
    table.appendChild(tbody);
    card.appendChild(table);
    c.appendChild(card);

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
        const curTd = el("td", "val", cur);
        if (!s.value_readable) curTd.classList.add("muted");
        tr.appendChild(curTd);
        tr.appendChild(el("td", null, (s.possible_values || []).join(", ")));
        tbody.appendChild(tr);
      });
    }
    draw("");
    input.addEventListener("input", () => draw(input.value));
  }

  function renderSecurity(data) {
    const c = document.getElementById("security");
    c.innerHTML = "";
    if (data.error) {
      const card = el("div", "card");
      card.appendChild(el("h2", null, "Security (HSI)"));
      card.appendChild(el("p", null, "Error: " + data.error));
      c.appendChild(card);
      return;
    }
    const card = el("div", "card");
    card.appendChild(el("h2", null, "Host Security (HSI)"));
    const table = el("table");
    const thead = el("thead");
    const hr = el("tr");
    ["Name", "Result", "Summary"].forEach((h) => hr.appendChild(el("th", null, h)));
    thead.appendChild(hr);
    table.appendChild(thead);
    const tbody = el("tbody");
    (data.attributes || []).forEach((a) => {
      const tr = el("tr");
      tr.appendChild(el("td", null, a.name));
      const res = a.hsi_result || "";
      const badgeCls = (res === "valid" || res === "enabled" || res === "not-tainted" || res === "locked") ? "ok" : "bad";
      const td = el("td");
      const b = el("span", "badge " + badgeCls, res);
      td.appendChild(b);
      tr.appendChild(td);
      tr.appendChild(el("td", null, a.summary || ""));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    card.appendChild(table);
    c.appendChild(card);

    if (data.events && data.events.length) {
      const card2 = el("div", "card");
      card2.appendChild(el("h2", null, "Security Events"));
      const table2 = el("table");
      const thead2 = el("thead");
      const hr2 = el("tr");
      ["When", "Name", "Result"].forEach((h) => hr2.appendChild(el("th", null, h)));
      thead2.appendChild(hr2);
      table2.appendChild(thead2);
      const tbody2 = el("tbody");
      data.events.forEach((e) => {
        const tr = el("tr");
        tr.appendChild(el("td", null, e.created ? new Date(e.created * 1000).toISOString().slice(0,19).replace("T"," ") : ""));
        tr.appendChild(el("td", null, e.name || ""));
        tr.appendChild(el("td", null, e.result || ""));
        tbody2.appendChild(tr);
      });
      table2.appendChild(tbody2);
      card2.appendChild(table2);
      c.appendChild(card2);
    }
  }

  function renderBoot(data) {
    const c = document.getElementById("boot");
    c.innerHTML = "";
    const card = el("div", "card");
    card.appendChild(el("h2", null, "Boot Configuration"));
    const info = el("div", "kv");
    info.appendChild(el("div", "k", "BootCurrent"));
    info.appendChild(el("div", "v", data.boot_current || "n/a"));
    info.appendChild(el("div", "k", "SecureBoot"));
    info.appendChild(el("div", "v", data.secure_boot || "n/a"));
    info.appendChild(el("div", "k", "Timeout"));
    info.appendChild(el("div", "v", data.timeout || "n/a"));
    card.appendChild(info);

    const table = el("table");
    const thead = el("thead");
    const hr = el("tr");
    ["ID", "Label", "Active"].forEach((h) => hr.appendChild(el("th", null, h)));
    thead.appendChild(hr);
    table.appendChild(thead);
    const tbody = el("tbody");
    (data.entries || []).forEach((e) => {
      const tr = el("tr");
      tr.appendChild(el("td", "val", e.id));
      tr.appendChild(el("td", null, e.label));
      tr.appendChild(el("td", null, e.active ? "yes" : ""));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    card.appendChild(table);
    c.appendChild(card);
  }

  function renderEc(data) {
    const c = document.getElementById("ec");
    c.innerHTML = "";
    if (!data.available) {
      const card = el("div", "card");
      card.appendChild(el("h2", null, "Embedded Controller"));
      card.appendChild(el("p", null, "thinkpad_acpi not available"));
      c.appendChild(card);
      return;
    }
    Object.keys(data.entries || {}).forEach((name) => {
      const card = el("div", "card");
      card.appendChild(el("h2", null, name));
      const info = el("div", "kv");
      Object.keys(data.entries[name]).forEach((k) => {
        info.appendChild(el("div", "k", k));
        info.appendChild(el("div", "v", data.entries[name][k]));
      });
      card.appendChild(info);
      c.appendChild(card);
    });
  }

  function renderFirmware(data) {
    const c = document.getElementById("firmware");
    c.innerHTML = "";
    const card = el("div", "card");
    card.appendChild(el("h2", null, "Firmware Devices"));
    const table = el("table");
    const thead = el("thead");
    const hr = el("tr");
    ["Name", "Version", "Vendor"].forEach((h) => hr.appendChild(el("th", null, h)));
    thead.appendChild(hr);
    table.appendChild(thead);
    const tbody = el("tbody");
    (data.devices || []).forEach((d) => {
      const tr = el("tr");
      tr.appendChild(el("td", null, d.name || ""));
      tr.appendChild(el("td", "val", d.version || ""));
      tr.appendChild(el("td", null, d.vendor || ""));
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    card.appendChild(table);
    c.appendChild(card);

    if (data.history && data.history.length) {
      const card2 = el("div", "card");
      card2.appendChild(el("h2", null, "Update History"));
      const table2 = el("table");
      const thead2 = el("thead");
      const hr2 = el("tr");
      ["Device", "Old", "New", "Result"].forEach((h) => hr2.appendChild(el("th", null, h)));
      thead2.appendChild(hr2);
      table2.appendChild(thead2);
      const tbody2 = el("tbody");
      data.history.forEach((h) => {
        const tr = el("tr");
        tr.appendChild(el("td", null, h.device || ""));
        tr.appendChild(el("td", "val", h.old_version || ""));
        tr.appendChild(el("td", "val", h.new_version || ""));
        tr.appendChild(el("td", null, h.result || ""));
        tbody2.appendChild(tr);
      });
      table2.appendChild(tbody2);
      card2.appendChild(table2);
      c.appendChild(card2);
    }
  }

  function loadAll(readValues) {
    send("get_identity", {});
    send("get_settings", { read_values: readValues });
    send("get_security", {});
    send("get_boot", {});
    send("get_ec", {});
    send("get_firmware", {});
  }

  document.getElementById("refreshBtn").addEventListener("click", () => {
    const rv = document.getElementById("readValues").checked;
    loadAll(rv);
  });
  document.getElementById("readValues").addEventListener("change", (e) => {
    loadAll(e.target.checked);
  });

  // Initial load (metadata only, no auth prompt).
  loadAll(false);
})();
