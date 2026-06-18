# Python HTML Construction Pitfalls

When using execute_code (Python) to build HTML files programmatically, these escaping traps bite reliably.

## `\n` vs `\\n` — The literal-newline trap

```
# WRONG — produces literal \n text in the output file
cards = "\\n".join(card_list)
html = html.replace("\\\\n", "\n")   # mismatched escaping, does nothing

# RIGHT — real newline
cards = "\n".join(card_list)
html = html.replace( chr(92) + "n", "\n" )  # or use the correct escape level:
                                             # "\\n" in Python source = \n (2 chars)
                                             # "\n" in Python source = newline (1 char)
```

**Rule:** `"\\n".join(...)` joins with literal backslash-n. `"\n".join(...)` joins with actual newline.

## Triple-quote f-strings with braces

When using f-strings with `"""..."""`, any `{` or `}` in the CSS/HTML needs to be doubled:
```python
# WRONG — Python thinks { is an f-string expression
css = f""".container {{ max-width: 800px; }}"""

# RIGHT — double braces for literal { }
css = f""".container {{ max-width: 800px; }}"""
```
Or better: store CSS as a separate variable (not an f-string) and concatenate.

## Backslash in CSS escapes

CSS `content` properties with backslash escapes need careful handling:
```python
# Python string: \\f0c8 becomes \f0c8 in CSS, which CSS reads as char f0c8
content = "\\f0c8"  # correct for CSS Unicode escape
```

## Closing tag gotchas in Python strings

```
# WRONG — Python closes the string at </summary>
html = "<details><summary>Title</summary>content</details>"

# RIGHT — escape the slash or use a different quote style
html = '<details><summary>Title</summary>content</details>'
html = "<details><summary>Title<\/summary>content<\/details>"
```

## Variable interpolation in large HTML blocks

Building HTML via string concatenation or f-strings inside Python is fine for small dynamic sections. For large blocks, prefer:
1. Write the static template with `{placeholder}` markers
2. Use `.replace("{placeholder}", value)` to inject dynamic parts
3. This keeps the HTML readable and avoids f-string brace doubling
