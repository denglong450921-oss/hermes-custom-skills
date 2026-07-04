---
name: process-obsidian-raw-sources
description: Process unprocessed Markdown files from an Obsidian LLM Wiki vault's 08_sources_raw folder into the vault structure. Use when the user asks to distill raw source Markdown, break down saved clippings/articles/transcripts into wiki notes, tasks, calendar items, projects, areas, memos, or outputs, and avoid reprocessing files already marked as processed.
---

# Process Obsidian Raw Sources

## Core Workflow

1. Locate the vault. Use the user-provided vault path, the current working directory if it contains `08_sources_raw/`, or this default if it exists:

   `/Users/f/Documents/dennon_obsidian_vault_important/den-llm-wiki/llm_wiki_knowledge`

2. Read the vault's `AGENTS.md` before changing notes.
3. Run the marker script to find unprocessed raw source files:

   ```bash
   python3 scripts/raw_source_marker.py --vault "/path/to/vault" list
   ```

4. For each selected unprocessed file, read the source and distill it into the vault:

   - `09_wiki/` for durable concepts, frameworks, summaries, and extracted knowledge.
   - `02_memos/` for small standalone ideas or sparks.
   - `05_projects/` for active work with a finishable outcome.
   - `06_areas/` for ongoing responsibilities or long-running themes.
   - `07_people/` for people, organizations, or relationship context.
   - `tasks.md` for actionable tasks using `- [ ] ... due:YYYY-MM-DD priority:medium`.
   - `upcoming.md` for dated events using the existing table format.
   - `10_outputs/` only for finished drafts or deliverables.

5. Preserve the raw source text. Only add or update processing marker fields in the raw file frontmatter.
6. Mark the source as processed after outputs are written:

   ```bash
   python3 scripts/raw_source_marker.py --vault "/path/to/vault" mark \
     --source "08_sources_raw/source.md" \
     --output "09_wiki/Distilled Note.md" \
     --output "tasks.md"
   ```

7. Run `npm run build` from the vault root when the dashboard exists.
8. Report which raw files were processed, which were skipped because they were already marked, and which output notes changed.

## Marker Rules

The marker is stored in source frontmatter:

```yaml
llm_wiki_processed: true
llm_wiki_processed_at: "2026-07-03T13:00:00+08:00"
llm_wiki_processor: "process-obsidian-raw-sources"
llm_wiki_outputs:
  - "09_wiki/Example.md"
```

Before processing a raw source, always check its marker with the bundled script. Skip files with `llm_wiki_processed: true` unless the user explicitly asks to reprocess them.

Useful commands:

```bash
python3 scripts/raw_source_marker.py --vault "/path/to/vault" status
python3 scripts/raw_source_marker.py --vault "/path/to/vault" list --all
python3 scripts/raw_source_marker.py --vault "/path/to/vault" next
python3 scripts/raw_source_marker.py --vault "/path/to/vault" unmark --source "08_sources_raw/source.md"
```

Use `--json` when a machine-readable status list is easier to inspect.

## Distillation Rules

- Write concise, linked notes. Do not paste whole raw articles into wiki notes.
- Prefer exact dates in `YYYY-MM-DD` format.
- Keep source attribution by linking back to the raw source note.
- Add `## Related` sections with Obsidian `[[wikilinks]]`.
- Update existing notes instead of creating duplicates when the concept already exists.
- Keep generated notes in the same language as the raw source unless the user asks otherwise.
- Use Title Case for English filenames and readable Chinese titles for Chinese notes.

## Duplicate Checks

Before creating a new note:

1. Search filenames in the target folder for the same title or concept.
2. Search existing wiki links for the concept if the note might already exist.
3. If an existing note is clearly the same concept, merge new distilled content into that note and include the source link.

## Failure Handling

- If a raw source is already marked processed, report the marker outputs and do not rewrite derived notes unless the user asks for reprocessing.
- If a source contains too many unrelated topics, create multiple focused notes and mark all outputs.
- If a source is unclear, create one `09_wiki/` seed note with `status: seed` and record open questions.
- If a dashboard build fails after notes are processed, keep the processing marker and report the build error separately.

## Bundled Script

Use `scripts/raw_source_marker.py` for status, next-file selection, and marker updates. The script intentionally does not summarize content; Codex performs the distillation and then uses the script to record that the raw source has been handled.
