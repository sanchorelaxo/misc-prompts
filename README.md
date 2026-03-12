# best-prompts

Prompt library organized by content theme.

## Directory layout

- `ai/` - AI agent and assistant prompts
- `comms/` - communication and negotiation prompts
  - `marketing/` - marketing and advertisement prompts
- `content/` - content creation and analysis prompts
- `dev/` - software engineering and architecture prompts
- `fin/` - finance and modeling prompts
- `photography/` - photography and visual content prompts
- `prompt/` - prompt-engineering methods and templates
- `reasoning/` - reasoning frameworks and thought structures
- `misc/` - single-file categories that do not yet have 2+ files

## Utility scripts

- `content/ytscribe_transcript.py`
  - CLI utility used by `content/YouTube_Video_Analyst_Playbook.txt`
  - Example: `python content/ytscribe_transcript.py --url <youtube-url> --out-dir content`
