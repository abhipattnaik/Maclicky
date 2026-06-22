# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Maclicky macOS App.

Build:
    pyinstaller maclicky.spec --clean --noconfirm
"""

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

hidden = [
    # Lazy LLM providers
    "ai.claude_provider",
    "ai.openai_provider",
    "ai.gemini_provider",
    "ai.ollama_provider",
    "ai.ollama_models_registry",
    "ai.github_copilot_provider",
    "ai.element_locator",
    "ai.universal_locator",
    "ai.web_search",
    "ai.ollama_bootstrap",

    # First-run setup wizard
    "ui.setup_wizard",

    # Lazy STT providers
    "audio.stt.deepgram_stt",
    "audio.stt.openai_stt",
    "audio.stt.faster_whisper_stt",

    # Lazy TTS providers
    "audio.tts.edge_tts_provider",
    "audio.tts.openai_tts_provider",
    "audio.tts.elevenlabs_provider",

    # Indirect deps
    "tiktoken_ext",
    "tiktoken_ext.openai_public",
]

datas, binaries, hiddenimports = [], [], []
for pkg in (
    "faster_whisper",
    "ctranslate2",
    "tokenizers",
    "edge_tts",
    "anthropic",
    "openai",
    "ollama",
    "elevenlabs",
    "tavily",
    "httpx",
    "httpcore",
    "certifi",
):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

hiddenimports += hidden
hiddenimports += collect_submodules("PyQt6")

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "scipy", "pandas", "tkinter",
        "notebook", "jupyter", "IPython",
        "torch.distributions", "torch.onnx",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Maclicky",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Maclicky",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Maclicky.app",
        icon="assets/icon.icns",
        bundle_identifier="com.abhipattnaik.maclicky",
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "NSAppleScriptEnabled": False,
            "NSMicrophoneUsageDescription": "Maclicky needs microphone access to listen to your voice commands.",
        }
    )
