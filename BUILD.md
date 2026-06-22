# Building Maclicky for macOS

Two ways to package Maclicky for distribution:

| Method | Output | Size | Install | Best for |
|---|---|---|---|---|
| **App Bundle** | `dist/Maclicky.app` | ~400-600 MB | Drag to Applications | Quick testing |
| **DMG installer** | `dist/Maclicky.dmg` | ~200-400 MB | Double-click, drag to Apps | Polished distribution |

---

## Quick build

```bash
chmod +x build.sh
./build.sh
```

After 2-5 minutes:
```
dist/Maclicky.app       ← drag to /Applications
dist/Maclicky.dmg       ← share this with friends
dist/Maclicky-macOS.zip ← compressed archive
```

Your friend:
1. Opens `Maclicky.dmg`
2. Drags `Maclicky.app` to their Applications folder
3. (Optional) creates `~/.env` in the app bundle or `~/Maclicky/.env` with API keys — see `.env.example`
4. Double-clicks `Maclicky.app`
5. Menu bar icon appears, Maclicky is running

**No Python needed on their machine.** Everything is bundled.

---

## What gets bundled

| Component | Bundled? | Notes |
|---|---|---|
| Python runtime | ✅ | Embedded — no install needed |
| PyQt6 | ✅ | UI framework |
| faster-whisper + ctranslate2 | ✅ | Local STT (free fallback) |
| edge-tts | ✅ | Free TTS (always available) |
| anthropic / openai / google SDKs | ✅ | LLM clients |
| Your `.env` | ❌ | **Must be added post-install** (security) |
| Ollama server | ❌ | Friend installs separately if they want local AI |

---

## First-run checklist for your friend

When they launch `Maclicky.app` the first time:

1. **macOS Gatekeeper warning** ("can't be opened because it's from an unidentified developer")
   - Right-click the app → "Open" → click "Open" in the dialog
   - Or go to **System Settings → Privacy & Security** → click "Open Anyway"
   - This is normal for unsigned apps. To fix permanently, code-sign with an Apple Developer certificate (~$99/year).

2. **Microphone permission** (macOS prompts automatically)
   - Click "OK" — needed for voice input
   - If denied, re-enable in **System Settings → Privacy & Security → Microphone**

3. **Accessibility permission** (for global hotkey)
   - macOS may prompt to allow keyboard monitoring
   - Grant access in **System Settings → Privacy & Security → Accessibility**

4. **Menu bar icon** appears in the top-right
   - Click it → see the menu
   - If no icon appears, check Activity Monitor for the Maclicky process

5. **Test it**:
   - Hold `Cmd + Opt + Space`, say "what's on my screen"
   - If silent → check `.env` has at least one API key, OR install Ollama locally

---

## Troubleshooting the build

**`pyinstaller: command not found`**
```bash
pip install pyinstaller
```

**`Failed to collect faster_whisper`**
```bash
pip install --upgrade faster-whisper ctranslate2
```
Then re-run `./build.sh`.

**App crashes on launch**
- Check Console.app for crash logs
- Make sure you built with the same Python version in your `.venv`

**Build is 600 MB — too large**
- Most of that is `torch` (pulled in by `faster-whisper`)
- For the smallest build, edit `requirements.txt`: remove `faster-whisper`, keep only `edge-tts` + `anthropic` + `openai` → drops to ~150 MB
- Friend loses local STT, must use Deepgram/OpenAI Whisper via API instead

**Build is slow (5+ min)**
- Normal first time — PyInstaller analyses every import
- Subsequent builds are faster if you don't `rm -rf build`

---

## Code-signing the app (optional)

To avoid the macOS Gatekeeper warning, you need an **Apple Developer certificate**:

1. Enroll in the [Apple Developer Program](https://developer.apple.com/programs/) ($99/year)
2. After `./build.sh`, sign the app:
   ```bash
   codesign --deep --force --sign "Developer ID Application: Your Name (TEAM_ID)" dist/Maclicky.app
   ```
3. Optionally notarize for full Gatekeeper bypass:
   ```bash
   xcrun notarytool submit dist/Maclicky.dmg --apple-id you@email.com --team-id TEAM_ID --password @keychain:AC_PASSWORD --wait
   xcrun stapler staple dist/Maclicky.dmg
   ```

For testing with friends this is overkill — just tell them to right-click → Open.

---

## Directory layout after build

```
Maclicky/
├── build/              ← PyInstaller scratch (safe to delete)
└── dist/
    ├── Maclicky.app    ← macOS application bundle
    ├── Maclicky.dmg    ← disk image installer — share with friends
    └── Maclicky-macOS.zip ← ZIP archive for distribution
```
