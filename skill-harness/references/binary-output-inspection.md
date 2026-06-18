# Binary Output Inspection in Grader Checks

When a skill produces **binary files** (`.pptx`, `.docx`, `.xlsx`, `.mp3`, `.png`, `.pdf`, etc.), terminal-output-only grader checks are insufficient. The generator can print a believable `OUTPUT_FILE=...` line while the actual file is corrupt or missing content.

## Why Inspect Binary Outputs

| Limitation | Consequence |
|------------|-------------|
| Terminal output is self-reported | Model can fabricate success messages |
| `OUTPUT_FILE=` is easy to fake | Harness passes even if file doesn't exist |
| Text patterns are superficial | Can't verify actual content fidelity |
| Protected terms/homeomorphic constraints | Need byte-level verification |

**Rule**: Trust the file, not the log. The grader should open the binary output and verify its content.

## Office Document Pattern (.pptx, .docx, .xlsx)

All Office Open XML files are ZIP archives. Inspect their internal XML:

```python
import zipfile, re

def check_pptx_for_terms(pptx_path):
    """Verify protected terms remain untranslated in a .pptx file."""
    slide_texts = []
    with zipfile.ZipFile(pptx_path) as z:
        for name in z.namelist():
            if name.startswith("ppt/slides/slide"):
                slide_texts.append(z.read(name).decode("utf-8", errors="replace"))
    all_text = " ".join(slide_texts)
    return {"PAS": "PAS" in all_text, "Prism AI": "Prism AI" in all_text}
```

### Path Extraction from Terminal Output

Parse `OUTPUT_FILE=` to locate the binary output:

```python
import os, re

def _parse_output_pptx_path(content):
    match = re.search(r"OUTPUT_FILE=(\S+)", content)
    if match:
        path = match.group(1).strip()
        if os.path.exists(path):
            return path
        resolved = os.path.join(os.getcwd(), path)
        if os.path.exists(resolved):
            return resolved
    return None
```

### Fallback Chain Pattern

When binary file might not exist, fall back to terminal output:

```python
elif check["check"] == "protected_terms_preserved":
    pptx_output = _parse_output_pptx_path(content)
    if pptx_output and os.path.exists(pptx_output):
        term_results = check_pptx_for_terms(pptx_output)
        passed = sum(1 for v in term_results.values() if v) >= 2
        evidence = f"Terms: {[t for t,v in term_results.items() if v]}"
    else:
        term_hits = [t for t in PROTECTED_TERMS if t.lower() in content.lower()]
        passed = len(term_hits) >= 1
        evidence = f"Terms in terminal: {term_hits}" if term_hits else "No terms found"
```

## Concrete Example

The `ppt-translator` skill's grader (`~/.hermes/skills/ppt-translator/evals/grader.py`) implements the full pattern:
- Parses `OUTPUT_FILE=` from terminal log
- Opens the output `.pptx` (ZIP) to verify PAS/Prism AI/B2B term preservation
- Falls back to terminal log check when .pptx isn't available
- Counts slides for structural integrity

## When to Use

| Use binary inspection | Stick to terminal output |
|-----------------------|-------------------------|
| Skill produces office docs, images, audio | Skill produces text, JSON, CSV |
| Protected terms must survive processing | Only format/structure matters |
| Output integrity is primary concern | Task is information-retrieval only |
