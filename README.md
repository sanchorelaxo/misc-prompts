# best-prompts

Prompt library organized by content theme.

## Directory layout

- `ai/` - AI agent and assistant prompts
- `comms/` - communication and negotiation prompts
- `content/` - content creation and analysis prompts
- `dev/` - software engineering and architecture prompts
- `fin/` - finance and modeling prompts
- `prompt/` - prompt-engineering methods and templates
- `reasoning/` - reasoning frameworks and thought structures
- `misc/` - single-file categories that do not yet have 2+ files

## Naming convention

- Files inside category folders do **not** repeat the category prefix.
- Single-file categories may keep a category prefix while they remain in `misc/`.

## Utility scripts

- `content/ytscribe_transcript.py`
  - CLI utility used by `content/YouTube_Video_Analyst_Playbook.txt`
  - Example: `python content/ytscribe_transcript.py --url <youtube-url> --out-dir content`
