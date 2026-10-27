// ==UserScript==
// @name         OpenClaw Control UI Voice Input (v4)
// @namespace    openclaw-mic
// @version      1.0.0
// @description  Adds a voice-input button under the OpenClaw Control UI chat input,
//               horizontally centered on the input box. v4 fixes v3's right-anchored
//               overlap with model picker / send button. Auto-discovers input via
//               <chat-input> host + 5-step editable ladder + clipboard fallback.
// @author       gateway-owner
// @match        http://127.0.0.1:18789/*
// @match        http://localhost:18789/*
// @grant        none
// @run-at       document-idle
// @noframes
// ==/UserScript==

(() => {
  "use strict";

  // ---------- SpeechRecognition support --------------------------------------

  const SR =
    typeof window.SpeechRecognition === "function"
      ? window.SpeechRecognition
      : typeof window.webkitSpeechRecognition === "function"
      ? window.webkitSpeechRecognition
      : null;

  const LANG_OK = (navigator.language || "en").toLowerCase().startsWith("zh") ? "zh" : "en";

  // ---------- i18n ------------------------------------------------------------

  const LABEL = {
    zh: {
      idle: "🎙 语音输入",
      listening: "🔴 正在听…点此停止",
      unsupported: "当前浏览器不支持语音输入",
      denied: "已拒绝麦克风权限",
      error: "语音识别出错",
      copied: "已复制到剪贴板，请粘贴",
    },
    en: {
      idle: "🎙 Voice input",
      listening: "🔴 Listening… tap to stop",
      unsupported: "Speech recognition not supported in this browser",
      denied: "Microphone permission denied",
      error: "Speech recognition error",
      copied: "Copied to clipboard — paste into the input",
    },
  };
  const TXT = LABEL[LANG_OK];

  // ---------- DOM bootstrap --------------------------------------------------

  const ROOT_ID = "openclaw-mic-button-root";
  const TOAST_ID = "openclaw-mic-toast";

  function ensureRoot() {
    let root = document.getElementById(ROOT_ID);
    if (root) return root;
    root = document.createElement("div");
    root.id = ROOT_ID;
    root.setAttribute("data-openclaw-mic", "1");
    root.setAttribute("data-version", "v4-userscript");
    Object.assign(root.style, {
      position: "fixed",
      // Anchor (set dynamically in updateAnchor()):
      top: "auto",
      bottom: "calc(14px + env(safe-area-inset-bottom, 0px))",
      left: "50%",
      right: "auto",
      transform: "translateX(-50%)",
      zIndex: "2147483000",
      pointerEvents: "auto",
      display: "block", // ← never hide (v2 lesson)
    });
    (document.body || document.documentElement).appendChild(root);
    return root;
  }

  function ensureButton(root) {
    let btn = root.querySelector("#openclaw-mic-button");
    if (btn) return btn;
    btn = document.createElement("button");
    btn.type = "button";
    btn.id = "openclaw-mic-button";
    btn.setAttribute("aria-live", "polite");
    btn.textContent = SR ? TXT.idle : TXT.unsupported;
    Object.assign(btn.style, {
      appearance: "none",
      border: "1px solid rgba(127,127,127,0.5)",
      borderRadius: "999px",
      background: SR ? "rgba(28,28,32,0.86)" : "rgba(96,96,96,0.55)",
      color: "#f5f5f5",
      font: "12px/1.2 system-ui, -apple-system, 'Segoe UI', sans-serif",
      padding: "7px 12px",
      cursor: SR ? "pointer" : "not-allowed",
      boxShadow: "0 2px 10px rgba(0,0,0,0.25)",
      backdropFilter: "blur(6px)",
      WebkitBackdropFilter: "blur(6px)",
      transition: "transform 120ms ease, background 120ms ease",
      userSelect: "none",
      opacity: SR ? "1" : "0.55",
      minWidth: "108px",
      textAlign: "center",
    });
    btn.disabled = !SR;
    btn.addEventListener("mousedown", () => (btn.style.transform = "scale(0.95)"));
    btn.addEventListener("mouseleave", () => (btn.style.transform = "scale(1)"));
    btn.addEventListener("click", onClick);
    root.appendChild(btn);
    return btn;
  }

  function flashClick() {
    const btn = ensureButton(ensureRoot());
    btn.style.transform = "scale(1.08)";
    setTimeout(() => (btn.style.transform = "scale(1)"), 200);
  }

  // ---------- Speech recognition lifecycle -----------------------------------

  let recognition = null;
  let state = "idle";
  let lastTranscript = "";
  let lastTa = null;
  let lastValue = "";

  function setState(next) {
    state = next;
    const btn = ensureButton(ensureRoot());
    switch (next) {
      case "listening":
        btn.textContent = TXT.listening;
        btn.style.background = "rgba(196,29,29,0.85)";
        break;
      case "requesting":
        btn.textContent = "🎙 请求麦克风权限…";
        btn.style.background = "rgba(64,128,200,0.85)";
        break;
      case "denied":
        btn.textContent = TXT.denied;
        btn.style.background = "rgba(196,29,29,0.85)";
        btn.disabled = true;
        btn.style.opacity = "0.55";
        break;
      case "error":
        btn.textContent = TXT.error;
        btn.style.background = "rgba(196,29,29,0.85)";
        setTimeout(() => setState("idle"), 1800);
        break;
      default:
        btn.textContent = SR ? TXT.idle : TXT.unsupported;
        btn.style.background = SR ? "rgba(28,28,32,0.86)" : "rgba(96,96,96,0.55)";
        btn.style.opacity = SR ? "1" : "0.55";
        btn.disabled = !SR;
    }
  }

  function onClick() {
    if (!SR) return;
    flashClick();
    if (state === "listening" || state === "requesting") {
      stopListening();
    } else {
      startListening();
    }
  }

  function startListening() {
    setState("requesting");
    try {
      recognition = new SR();
    } catch (e) {
      console.warn("[openclaw-mic] cannot construct SpeechRecognition:", e);
      setState("error");
      return;
    }
    recognition.lang = navigator.language || "zh-CN";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      lastTranscript = "";
      setState("listening");
    };

    recognition.onresult = (ev) => {
      let interim = "";
      let final_ = "";
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        const r = ev.results[i];
        const txt = r[0] && r[0].transcript;
        if (!txt) continue;
        if (r.isFinal) final_ += txt;
        else interim += txt;
      }
      const combined = (final_ || interim).trim();
      if (!combined) return;

      const target = findEditable();
      if (target) {
        const delta = computeDelta(lastTranscript, combined);
        if (delta) {
          const ok = appendToEditable(target, delta);
          if (!ok) {
            copyToClipboard(delta, /* merge */ true);
            showToast(TXT.copied);
          }
        }
      } else {
        copyToClipboard(combined, /* merge */ true);
        showToast(TXT.copied);
      }
      lastTranscript = final_ ? final_.trim() : combined;
    };

    recognition.onerror = (ev) => {
      if (ev.error === "not-allowed" || ev.error === "service-not-allowed") {
        setState("denied");
        return;
      }
      if (ev.error === "no-speech") return;
      console.warn("[openclaw-mic] recognition error:", ev.error, ev.message || "");
    };

    recognition.onend = () => {
      setState("idle");
      recognition = null;
    };

    try {
      recognition.start();
    } catch (e) {
      console.warn("[openclaw-mic] start() rejected:", e);
    }
  }

  function stopListening() {
    if (recognition) {
      try { recognition.stop(); } catch (e) { /* ignore */ }
    }
    setState("idle");
  }

  function computeDelta(prev, next) {
    if (!prev) return next;
    if (next.startsWith(prev)) return next.slice(prev.length);
    let i = 0;
    while (i < prev.length && i < next.length && prev[i] === next[i]) i++;
    return next.slice(i);
  }

  // ---------- Editable surface discovery (5-step ladder) ---------------------

  function findChatInputHost() {
    const tagged = document.querySelector("chat-input");
    if (tagged) return tagged;
    const candidates = Array.from(document.querySelectorAll('[class*="chat-input" i], [class*="composer" i], [class*="message-input" i]'));
    for (const el of candidates) {
      const rect = el.getBoundingClientRect();
      if (rect.width > 80 && rect.height > 16) return el;
    }
    return null;
  }

  function findEditable() {
    // 1. <chat-input>.shadowRoot
    const chatInput = findChatInputHost();
    if (chatInput && chatInput.shadowRoot) {
      const ta = chatInput.shadowRoot.querySelector("textarea, [contenteditable]");
      if (ta) {
        console.info("[openclaw-mic] editable found via: chat-input.open-shadow");
        return ta;
      }
    }
    // 2. Any open shadow root
    const all = Array.from(document.querySelectorAll("*"));
    for (const el of all) {
      if (el.shadowRoot) {
        const ta = el.shadowRoot.querySelector("textarea, [contenteditable]");
        if (ta) {
          console.info("[openclaw-mic] editable found via: open-shadow." + (el.tagName || el.nodeName).toLowerCase());
          return ta;
        }
      }
    }
    // 3. Light DOM
    const taPlain = document.querySelector("textarea");
    if (taPlain) {
      console.info("[openclaw-mic] editable found via: document.textarea");
      return taPlain;
    }
    const ce = document.querySelector("[contenteditable]");
    if (ce) {
      console.info("[openclaw-mic] editable found via: document.contenteditable");
      return ce;
    }
    // 4. activeElement chain
    let ae = document.activeElement;
    let depth = 0;
    while (ae && depth++ < 8) {
      if (ae.tagName === "TEXTAREA" || ae.isContentEditable) {
        console.info("[openclaw-mic] editable found via: activeElement");
        return ae;
      }
      if (ae.shadowRoot) {
        const ta = ae.shadowRoot.querySelector("textarea, [contenteditable]");
        if (ta) {
          console.info("[openclaw-mic] editable found via: activeElement.shadowRoot");
          return ta;
        }
      }
      const parent = ae.parentElement;
      const host = ae.host;
      ae = parent || host || null;
      if (host === document) ae = null;
    }
    // 5. Same-origin iframes
    for (const f of Array.from(document.querySelectorAll("iframe"))) {
      let doc;
      try { doc = f.contentDocument; } catch (e) { continue; }
      if (!doc) continue;
      const t = doc.querySelector("textarea");
      if (t) {
        console.info("[openclaw-mic] editable found via: iframe.textarea");
        return t;
      }
      const c = doc.querySelector("[contenteditable]");
      if (c) {
        console.info("[openclaw-mic] editable found via: iframe.contenteditable");
        return c;
      }
    }
    console.info("[openclaw-mic] editable found via: NONE — using clipboard fallback");
    return null;
  }

  function appendToEditable(target, delta) {
    try {
      if (target.tagName === "TEXTAREA" || target.tagName === "INPUT") {
        const proto = target.tagName === "TEXTAREA" ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
        const current = target.value || "";
        const prevChar = current.length > 0 ? current[current.length - 1] : "";
        const needsSpace = prevChar && !/\s/.test(prevChar) && !/^\s/.test(delta);
        const piece = (needsSpace ? " " : "") + delta;
        const next = current + piece;
        if (setter) setter.call(target, next);
        else target.value = next;
        target.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
        target.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
        try { target.focus({ preventScroll: false }); } catch (e) { /* ignore */ }
        try { target.setSelectionRange(next.length, next.length); } catch (e) { /* ignore */ }
        return true;
      }
      if (target.isContentEditable) {
        const current = target.textContent || "";
        const prevChar = current.length > 0 ? current[current.length - 1] : "";
        const needsSpace = prevChar && !/\s/.test(prevChar) && !/^\s/.test(delta);
        const piece = (needsSpace ? " " : "") + delta;
        target.textContent = current + piece;
        target.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: piece }));
        return true;
      }
      return false;
    } catch (e) {
      console.warn("[openclaw-mic] appendToEditable threw:", e);
      return false;
    }
  }

  // ---------- Clipboard + toast fallback -------------------------------------

  async function copyToClipboard(text, merge) {
    try {
      let payload = text;
      if (merge) {
        try {
          const prev = await navigator.clipboard.readText();
          if (prev && !prev.endsWith(text)) {
            const lastChar = prev[prev.length - 1] || "";
            const sep = lastChar && !/\s/.test(lastChar) ? " " : "";
            payload = prev + sep + text;
          } else if (prev && prev.endsWith(text)) {
            payload = prev;
          }
        } catch (e) {
          // Clipboard read denied — write new chunk only.
        }
      }
      await navigator.clipboard.writeText(payload);
      console.info("[openclaw-mic] clipboard fallback wrote", payload.length, "chars");
    } catch (e) {
      console.warn("[openclaw-mic] clipboard fallback failed:", e);
    }
  }

  function showToast(msg) {
    let t = document.getElementById(TOAST_ID);
    if (!t) {
      t = document.createElement("div");
      t.id = TOAST_ID;
      Object.assign(t.style, {
        position: "fixed",
        bottom: "calc(60px + env(safe-area-inset-bottom, 0px))",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: "2147483600",
        background: "rgba(20,20,28,0.92)",
        color: "#f5f5f5",
        font: "13px/1.2 system-ui, -apple-system, 'Segoe UI', sans-serif",
        padding: "8px 14px",
        borderRadius: "10px",
        boxShadow: "0 4px 16px rgba(0,0,0,0.35)",
        backdropFilter: "blur(6px)",
        WebkitBackdropFilter: "blur(6px)",
        opacity: "0",
        transition: "opacity 200ms ease",
      });
      (document.body || document.documentElement).appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = "1";
    clearTimeout(showToast._hide);
    showToast._hide = setTimeout(() => (t.style.opacity = "0"), 2200);
  }

  // ---------- Anchor (v4: horizontally centered on chat-input) --------------

  function updateAnchor() {
    const root = ensureRoot();
    const host = findChatInputHost();
    if (host) {
      const r = host.getBoundingClientRect();
      if (r.width > 80 && r.height > 16 && r.bottom < window.innerHeight + 200) {
        // v4: horizontally centered ON the input box's center; positioned just below it.
        root.style.position = "fixed";
        root.style.top = "auto";
        root.style.bottom = `${window.innerHeight - r.bottom + 12}px`;
        root.style.left = `${r.left + r.width / 2}px`;
        root.style.right = "auto";
        root.style.transform = "translateX(-50%)";
        root.style.display = "block";
        return;
      }
    }
    // Fallback: viewport bottom-center
    root.style.position = "fixed";
    root.style.top = "auto";
    root.style.bottom = "calc(14px + env(safe-area-inset-bottom, 0px))";
    root.style.left = "50%";
    root.style.right = "auto";
    root.style.transform = "translateX(-50%)";
    root.style.display = "block";
  }

  let observer = null;
  let anchorTimer = 0;

  function scheduleUpdateAnchor() {
    if (anchorTimer) return;
    anchorTimer = window.setTimeout(() => {
      anchorTimer = 0;
      try { updateAnchor(); } catch (e) { /* ignore */ }
    }, 120);
  }

  function startObserver() {
    if (observer || typeof MutationObserver === "undefined") return;
    observer = new MutationObserver(scheduleUpdateAnchor);
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["style", "class", "hidden"],
    });
    window.addEventListener("resize", scheduleUpdateAnchor, { passive: true });
    window.addEventListener("scroll", scheduleUpdateAnchor, { passive: true });
  }

  // ---------- Boot ----------------------------------------------------------

  function init() {
    if (init._done) return;
    init._done = true;

    const host = findChatInputHost();
    console.info(
      "[openclaw-mic] ready",
      "v=4",
      "lang=" + LANG_OK,
      "sr=" + (SR ? (SR === window.SpeechRecognition ? "SpeechRecognition" : "webkitSpeechRecognition") : "null"),
      "chat-input.host=" + (host ? host.tagName.toLowerCase() : "not-found"),
    );

    const root = ensureRoot();
    ensureButton(root);
    updateAnchor();
    startObserver();
    scheduleUpdateAnchor();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }

  window.addEventListener("pagehide", () => {
    if (recognition) {
      try { recognition.abort(); } catch (e) { /* ignore */ }
    }
  });
})();