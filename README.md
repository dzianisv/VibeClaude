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
vibeclaude --install

# Install in specific project directory
vibeclaude --install --project-dir /path/to/project
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

1. Copies itself to your project's `.claude/hooks/` directory
2. Registers as a Stop hook in `.claude/settings.json`
3. When Claude-Code finishes a task:
   - Shows desktop notification with the last assistant message
   - Plays a pleasant 4-note arpeggio (C-E-G-C)

## License

MIT License