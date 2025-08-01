#!/usr/bin/env python3
"""
main.py
=======

Claude-Code *Stop* hook + installer (no external APIs).

Default behaviour  ──────────────────────────────────────────────
    • Pops a desktop notification with the last assistant reply
    • Generates & plays a short C-major arpeggio (pydub + simpleaudio)

Install mode  ───────────────────────────────────────────────────
    python notify_and_play_jingle.py --install [--project-dir PATH]

    ▸ copies itself to  <PROJECT>/.claude/hooks/
    ▸ injects the hook command into  <PROJECT>/.claude/settings.json
      (idempotent – no duplicate entries)

Dependencies (one-time)  ────────────────────────────────────────
    pip install plyer pydub simpleaudio
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from typing import Any, Dict, List

# ── constants ───────────────────────────────────────────────────
CMD_PLACEHOLDER = "vibe-claude"
# ────────────────────────────────────────────────────────────────


# ╭──────────────────────── installer ╮
def install_hook(project_dir: pathlib.Path) -> None:
    """Register vibe-claude as a hook in Claude settings."""
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    # read / create settings.json
    settings_path = claude_dir / "settings.json"
    try:
        config: Dict[str, Any] = (
            json.loads(settings_path.read_text("utf-8")) if settings_path.exists() else {}
        )
    except json.JSONDecodeError:
        print("[install] Malformed settings.json – starting fresh")
        config = {}

    stop_hooks: List[Dict[str, Any]] = config.setdefault("hooks", {}).setdefault("Stop", [])

    # already present?
    if any(
        cmd.get("command") == CMD_PLACEHOLDER
        for entry in stop_hooks
        for cmd in entry.get("hooks", [])
    ):
        print("[install] Hook already listed – nothing to do.")
    else:
        stop_hooks.append({"hooks": [{"type": "command", "command": CMD_PLACEHOLDER}]})
        settings_path.write_text(json.dumps(config, indent=2), "utf-8")
        print(f"[install] Hook entry added to {settings_path}")

    print("[install] Done – Claude-Code will now run vibe-claude hook on Stop.")
# ╰────────────────────────────────────╯


# ╭───────────────────── runtime hook ╮
def last_assistant_line(path: pathlib.Path) -> str:
    for raw in reversed(path.read_text("utf-8").splitlines()):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if obj.get("role") == "assistant":
            return (obj.get("text") or "").strip()
    return ""


def notify(msg: str) -> None:
    try:
        import subprocess
        import platform
        
        if platform.system() == "Darwin":  # macOS
            subprocess.run([
                "osascript", "-e", 
                f'display notification "{msg or "Task complete."}" with title "Claude ✔ Finished"'
            ], check=False)
        else:
            # Fallback for other systems
            try:
                from plyer import notification  # type: ignore
                notification.notify(title="Claude ✔ Finished", message=msg or "Task complete.")
            except ImportError:
                pass
    except Exception:
        pass  # silently ignore notification failures


def play_jingle() -> None:
    """Play a pleasant sound notification."""
    try:
        import subprocess
        import platform
        
        if platform.system() == "Darwin":  # macOS
            # Use built-in macOS sound
            subprocess.Popen([
                "afplay", "/System/Library/Sounds/Glass.aiff"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Fallback: try to generate audio with Python libs
            try:
                from pydub import AudioSegment               # type: ignore
                from pydub.generators import Sine            # type: ignore
                from pydub.playback import _play_with_simpleaudio as play  # type: ignore  # noqa: WPS450
                
                freqs = [523.25, 659.25, 783.99, 1046.5]        # C5 E5 G5 C6
                seg = AudioSegment.empty()
                for f in freqs:
                    seg += Sine(f).to_audio_segment(duration=250)
                play(seg)
            except ImportError:
                pass  # silently ignore if audio libs unavailable
    except Exception:
        pass  # silently ignore audio failures


def run_hook(payload: Dict[str, Any]) -> None:
    transcript = payload.get("transcript_path")
    text = ""
    if transcript:
        try:
            text = last_assistant_line(pathlib.Path(transcript))
        except Exception:
            pass

    notify(text)
    play_jingle()

    if text:
        print(text, flush=True)
# ╰────────────────────────────────────╯


def main() -> None:
    parser = argparse.ArgumentParser(description="Claude-Code Stop hook + installer (no API keys)")
    parser.add_argument("--install", action="store_true", help="install hook into a project")
    parser.add_argument(
        "--project-dir",
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help="project root (defaults to CWD)",
    )
    args = parser.parse_args()

    if args.install:
        install_hook(args.project_dir.resolve())
    else:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(f"[hook] Expected JSON on stdin – {exc}", file=sys.stderr)
            sys.exit(1)
        run_hook(payload)


if __name__ == "__main__":
    main()

