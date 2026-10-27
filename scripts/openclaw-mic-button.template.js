// openclaw-mic-button — voice-to-text button (position-fixed version)
// Browser-only; no Node APIs; CSP-safe via <script type="module" src="/...">.
(function () {
  'use strict';
  if (window.__openclawMicButtonLoaded) return;
  window.__openclawMicButtonLoaded = true;

  const TAG = '[openclaw-mic]';
  const BUTTON_CLASS = 'openclaw-mic-button';
  const TEXTAREA_SELECTORS = [
    '.agent-chat__composer-combobox > textarea',
    'textarea[placeholder*="message"i]',
    'textarea[aria-label*="message"i]'
  ];

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { console.info(TAG, 'SpeechRecognition unsupported'); return; }
  if (!window.isSecureContext) console.info(TAG, 'requires secure context (HTTPS or localhost)');

  let pendingFrame = null;
  const seen = new WeakSet();

  function scheduleScan() {
    if (pendingFrame) return;
    pendingFrame = requestAnimationFrame(() => { pendingFrame = null; scanAndInject(); });
  }

  function scanAndInject() {
    for (const sel of TEXTAREA_SELECTORS) {
      let list;
      try { list = document.querySelectorAll(sel); } catch (e) { continue; }
      list.forEach((ta) => { if (!seen.has(ta)) { seen.add(ta); injectButton(ta); } });
    }
  }

  function setNativeValue(el, value) {
    const proto = Object.getPrototypeOf(el);
    const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
    if (setter) setter.call(el, value); else el.value = value;
    el.dispatchEvent(new InputEvent('input', { bubbles: true, data: value }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function injectButton(textarea) {
    if (textarea.dataset.ocMic === '1') return;
    textarea.dataset.ocMic = '1';

    const parent = textarea.parentElement;
    if (!parent) return;

    // Make the combobox the positioning context (only if static — preserve any explicit value)
    const cs = window.getComputedStyle(parent);
    if (cs.position === 'static') parent.style.position = 'relative';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = BUTTON_CLASS;
    btn.setAttribute('aria-label', 'Voice input');
    btn.title = 'Voice input';
    btn.dataset.state = 'idle';

    btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">' +
      '<path fill="currentColor" d="M12 14q-1.25 0-2.125-.875T9 11V5q0-1.25.875-2.125T12 2q1.25 0 2.125.875T15 5v6q0 1.25-.875 2.125T12 14Zm-1 7v-3.075q-2.6-.35-4.3-2.325T5 11h2q0 2.075 1.463 3.537T12 16q2.075 0 3.538-1.463T17 11h2q0 2.625-1.7 4.6T13 17.925V21Z"/>' +
      '</svg>';

    // Position: absolute below the textarea, with parent acting as relative context
    Object.assign(btn.style, {
      position: 'absolute',
      bottom: '-56px',
      left: '0',
      right: '0',
      margin: '0 auto',
      width: '36px',
      height: '36px',
      borderRadius: '50%',
      border: '1px solid rgba(127,127,127,0.28)',
      background: 'rgba(30,30,30,0.82)',
      color: 'inherit',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '0',
      zIndex: '10',
      boxShadow: '0 2px 6px rgba(0,0,0,0.24)',
      transition: 'background 0.15s, color 0.15s, transform 0.1s'
    });
    btn.addEventListener('mouseenter', () => {
      if (btn.dataset.state !== 'recording') btn.style.background = 'rgba(60,60,60,0.9)';
    });
    btn.addEventListener('mouseleave', () => {
      if (btn.dataset.state === 'recording') btn.style.background = 'rgba(180,40,40,0.85)';
      else btn.style.background = 'rgba(30,30,30,0.82)';
    });
    btn.addEventListener('mousedown', () => { btn.style.transform = 'scale(0.94)'; });
    btn.addEventListener('mouseup', () => { btn.style.transform = 'scale(1)'; });

    let recognition = null; let silenceTimer = null; let finalText = '';
    const SILENCE_MS = 4000;

    function clearSilence() { if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null; } }
    function armSilence() {
      clearSilence();
      silenceTimer = setTimeout(() => { if (recognition) { try { recognition.stop(); } catch (_) {} } }, SILENCE_MS);
    }

    function stop() {
      clearSilence();
      if (recognition) { try { recognition.stop(); } catch (_) {} }
    }

    function start() {
      if (recognition) return;
      recognition = new SR();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = navigator.language || 'en-US';

      finalText = textarea.value ? textarea.value.replace(/\s+$/, '') + ' ' : '';
      armSilence();

      recognition.onresult = (ev) => {
        let interim = '';
        for (let i = ev.resultIndex; i < ev.results.length; i++) {
          const r = ev.results[i];
          if (r.isFinal) finalText += r[0].transcript + ' ';
          else interim += r[0].transcript;
        }
        setNativeValue(textarea, finalText + interim);
        armSilence();
      };

      recognition.onerror = (ev) => {
        const err = ev.error || '';
        if (err === 'no-speech') {
          try { recognition.stop(); } catch (_) {}
          setTimeout(() => { try { recognition.start(); } catch (_) {} }, 200);
        } else if (err === 'not-allowed' || err === 'service-not-allowed') {
          stop(); btn.dataset.state = 'denied';
        } else if (err === 'audio-capture') {
          stop(); btn.dataset.state = 'no-mic';
        } else {
          stop();
        }
      };

      recognition.onend = () => {
        clearSilence();
        recognition = null;
        if (btn.dataset.state !== 'denied' && btn.dataset.state !== 'no-mic') {
          btn.dataset.state = 'idle';
          btn.style.background = 'rgba(30,30,30,0.82)';
        }
      };

      try {
        recognition.start();
        btn.dataset.state = 'recording';
        btn.style.background = 'rgba(180,40,40,0.85)';
      } catch (_) {
        recognition = null;
        btn.dataset.state = 'idle';
      }
    }

    btn.addEventListener('click', (e) => {
      e.preventDefault(); e.stopPropagation();
      if (recognition) stop(); else start();
    });

    parent.appendChild(btn);
  }

  function init() {
    if (document.body) scanAndInject();
    else document.addEventListener('DOMContentLoaded', scanAndInject, { once: true });

    let debounce = null;
    const observer = new MutationObserver(() => {
      if (debounce) return;
      debounce = setTimeout(() => { debounce = null; scheduleScan(); }, 150);
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }

  init();
})();
