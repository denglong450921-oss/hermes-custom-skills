# Python Source Encoding Pitfall

When editing this skill's Python scripts (e.g., via `skill_manage(action='write_file')`),
emoji characters in source strings can cause encoding failures.

## The issue

Writing `\ud83c\udfaf` (UTF-16 surrogate pairs) into Python source produces:
```
'utf-8' codec can't encode characters in position …: surrogates not allowed
```

Python 3 rejects lone surrogate code points (U+D800–U+DFFF) in UTF-8 source files.

## Fix

| Don't | Do |
|-------|----|
| `"\ud83c\udfaf"` (surrogate pair) | `"\U0001f3af"` (8-digit escape) or `"🎯"` (actual char) |

**Prefer the actual emoji character** in source strings. If an escape sequence is
required, use `\U` (capital U, 8 hex digits), not `\u` (16-bit) for characters
above U+FFFF.

## Detection

Runtime error at a specific byte position → search the source for `\\ud` to find
the offending surrogate pair.
