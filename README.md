# VibeClaude

Claude-Code Stop hook with desktop notifications and audio feedback.

## Features

- Desktop notifications when Claude-Code tasks complete
- Pleasant C-major arpeggio audio feedback
- Easy installation as a Claude-Code hook
- No external API dependencies

## Installation

### From Git

```bash
pip install git+https://github.com/dzianisv/VibeClaude.git
```

### From Source

```bash
git clone https://github.com/dzianisv/VibeClaude.git
cd VibeClaude
pip install .
```

## Usage

### Install as Claude-Code Hook

```bash
# Install in current project
vibe-claude --install

# Install in specific project directory
vibe-claude --install --project-dir /path/to/project
```

### Manual Installation

```bash
python main.py --install
python main.py --install --project-dir /path/to/project
```

## Dependencies

- `plyer` - Cross-platform desktop notifications
- `pydub` - Audio generation and processing
- `simpleaudio` - Audio playback

## How It Works

1. Registers `vibe-claude` as a Stop hook in `.claude/settings.json`
2. Uses the installed binary from PATH (no file copying needed)
3. When Claude-Code finishes a task:
   - Shows desktop notification with the last assistant message
   - Plays a pleasant 4-note arpeggio (C-E-G-C)

## License

MIT License