# OpenClaw Control UI Voice Input (Userscript)

A Tampermonkey userscript that adds a voice-input button under the OpenClaw
Control UI chat input. v4 fixes v3's right-anchored overlap with model picker
/ send button. Horizontally centered on the input box.

## Install (one-time, ~3 minutes)

1. **Install Tampermonkey** (browser extension — Chrome, Edge, Firefox):
   - Chrome / Edge: <https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo>
   - Firefox: <https://addons.mozilla.org/firefox/addon/tampermonkey/>
   - Apple Safari: <https://apps.apple.com/app/tampermonkey/id1482490089>

2. **Install the userscript** (pick one):
   - **A. From local file**: open Tampermonkey dashboard → Utilities →
     "Import from file" → select `openclaw-mic.user.js` in this directory.
   - **B. By file:// URL**: paste
     `file:///home/zhiping/.openclaw/workspace/userscripts/openclaw-mic.user.js`
     into a new tab and Tampermonkey will offer to install it.
   - **C. (If you serve this file via your own web server)** point Tampermonkey
     at the served URL.

3. **Reload** the Control UI tab (`http://127.0.0.1:18789/`). The button should
   appear under the chat input, horizontally centered.

## Verify

After reload:
- A `🎙 语音输入` chip appears **horizontally centered on the chat input's
  width, 12 px below the input**.
- Click → browser asks for microphone permission. Allow.
- Speak → text appends to the input. Click again to stop.

Open DevTools console (F12) → you should see:
```
[openclaw-mic] ready v=4 lang=zh sr=webkitSpeechRecognition chat-input.host=chat-input
```

If `chat-input.host=not-found`, the input box uses a closed shadow root — the
script will fall back to clipboard + a "已复制到剪贴板" toast. Click in the
input area first, then click the mic button; click the toast area to paste.

## Update

Edit `openclaw-mic.user.js`, bump the `@version` line, save. Tampermonkey
detects the change automatically on the next page load (within ~24 h or on
manual "Update" from dashboard). **No Gateway restart needed** for any future
change.

## Uninstall

Tampermonkey dashboard → find "OpenClaw Control UI Voice Input (v4)" →
trash icon.

## Notes

- No audio leaves the browser. `SpeechRecognition` is browser-local.
- The button is visually centered on the input box's bounding rect, not on
  the viewport — when the input box is narrow or wide, the button follows it.
- The script only matches `http://127.0.0.1:18789/*` and
  `http://localhost:18789/*` — not remote Control UI instances.
