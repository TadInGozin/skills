"""
YAML parser for LLM Council config files.

Tries PyYAML first; falls back to a custom parser that handles the specific
patterns found in protocols/standard.yaml (nested maps, inline dicts/lists,
scalar types, block strings, comments).
"""

import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def load_yaml(path):
    """Load a YAML file and return a dict."""
    content = path.read_text(encoding="utf-8")
    return load_yaml_string(content)


def load_yaml_string(content):
    """Parse a YAML string and return a dict."""
    if HAS_YAML:
        return yaml.safe_load(content)
    return _parse_nested(content)


def extract_section(config, dotpath):
    """Extract a nested value by dot-separated path.

    >>> extract_section({"a": {"b": {"c": 1}}}, "a.b.c")
    1
    """
    current = config
    for key in dotpath.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


# ---------------------------------------------------------------------------
# Custom nested YAML parser
# ---------------------------------------------------------------------------

def _parse_nested(content):
    """Parse YAML content without PyYAML.

    Handles: nested maps, inline dicts {k: v}, inline lists [a, b],
    list items (- val), scalars (int, float, bool, str), block strings (|),
    comments (#).
    """
    lines = content.split("\n")
    root = {}
    # Stack of (indent_level, dict_ref)
    stack = [(-1, root)]
    i = 0

    while i < len(lines):
        raw = lines[i]
        # Strip inline comments (but not inside quoted strings)
        stripped = _strip_comment(raw)
        stripped_trimmed = stripped.strip()

        # Skip blank lines and comment-only lines
        if not stripped_trimmed or stripped_trimmed.startswith("#"):
            i += 1
            continue

        indent = _indent_level(raw)

        # Pop stack to find the correct parent
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]

        # Handle list item: - value or - key: value (list of dicts)
        if stripped_trimmed.startswith("- "):
            item_content = stripped_trimmed[2:].strip()
            if isinstance(parent, list):
                # Quoted strings are always scalars, even if they contain ':'
                if (item_content.startswith('"') and item_content.endswith('"')) or \
                   (item_content.startswith("'") and item_content.endswith("'")):
                    parent.append(_parse_scalar(item_content))
                    i += 1
                    continue
                if ":" in item_content:
                    # List item is a map entry: - key: value
                    item_dict = {}
                    k, _, v = item_content.partition(":")
                    k = k.strip()
                    v = v.strip()
                    if v:
                        item_dict[k] = _parse_scalar(v)
                    else:
                        item_dict[k] = {}
                    parent.append(item_dict)
                    # Push so subsequent indented lines add to this dict
                    # Use indent of the "- " content (indent + 2)
                    stack.append((indent, item_dict))
                else:
                    parent.append(_parse_scalar(item_content))
            i += 1
            continue

        # Handle key: value
        if ":" in stripped_trimmed:
            key, _, rest = stripped_trimmed.partition(":")
            key = key.strip()
            rest = rest.strip()

            if not rest:
                # Check next line to determine if list or nested map
                next_indent, next_line = _peek_next(lines, i + 1)
                if next_line is not None and next_line.strip().startswith("- "):
                    # Next is a list
                    new_list = []
                    parent[key] = new_list
                    stack.append((indent, new_list))
                else:
                    # Nested map
                    new_dict = {}
                    parent[key] = new_dict
                    stack.append((indent, new_dict))
            elif rest == "|" or rest == ">":
                # Block string — consume indented lines
                block_lines, i = _consume_block(lines, i + 1, indent)
                parent[key] = "\n".join(block_lines)
                continue
            elif rest.startswith("{"):
                # Inline dict
                parent[key] = _parse_inline_dict(rest)
            elif rest.startswith("["):
                # Inline list
                parent[key] = _parse_inline_list(rest)
            else:
                parent[key] = _parse_scalar(rest)

        i += 1

    return root


def _indent_level(line):
    """Count leading spaces."""
    return len(line) - len(line.lstrip(" "))


def _strip_comment(line):
    """Strip inline comments, preserving quoted strings."""
    in_quote = None
    for i, ch in enumerate(line):
        if ch in ('"', "'") and (i == 0 or line[i - 1] != "\\"):
            if in_quote == ch:
                in_quote = None
            elif in_quote is None:
                in_quote = ch
        elif ch == "#" and in_quote is None:
            # Check for space before # (YAML requires it for inline comments)
            if i == 0 or line[i - 1] == " ":
                return line[:i]
    return line


def _peek_next(lines, start):
    """Look ahead to the next non-empty, non-comment line."""
    for j in range(start, len(lines)):
        s = lines[j].strip()
        if s and not s.startswith("#"):
            return _indent_level(lines[j]), lines[j]
    return -1, None


def _consume_block(lines, start, parent_indent):
    """Consume a block string (| or >) starting from `start`."""
    block = []
    i = start
    while i < len(lines):
        if lines[i].strip() == "" or _indent_level(lines[i]) > parent_indent:
            block.append(lines[i].strip())
            i += 1
        else:
            break
    # Remove trailing empty lines
    while block and block[-1] == "":
        block.pop()
    return block, i


def _split_top_level(s, delimiter=","):
    """Split string on delimiter, respecting brackets and quotes."""
    parts = []
    current = []
    depth_bracket = 0
    depth_brace = 0
    in_quote = None

    for ch in s:
        if ch in ('"', "'") and in_quote is None:
            in_quote = ch
        elif ch == in_quote:
            in_quote = None
        elif in_quote is None:
            if ch == "[":
                depth_bracket += 1
            elif ch == "]":
                depth_bracket -= 1
            elif ch == "{":
                depth_brace += 1
            elif ch == "}":
                depth_brace -= 1
            elif ch == delimiter and depth_bracket == 0 and depth_brace == 0:
                parts.append("".join(current))
                current = []
                continue
        current.append(ch)

    if current:
        parts.append("".join(current))
    return parts


def _parse_inline_dict(s):
    """Parse `{ key: val, key2: val2 }` into a dict."""
    s = s.strip()
    if s.startswith("{"):
        s = s[1:]
    if s.endswith("}"):
        s = s[:-1]
    result = {}
    for pair in _split_top_level(s):
        pair = pair.strip()
        if ":" in pair:
            k, _, v = pair.partition(":")
            v = v.strip()
            if v.startswith("["):
                result[k.strip()] = _parse_inline_list(v)
            elif v.startswith("{"):
                result[k.strip()] = _parse_inline_dict(v)
            else:
                result[k.strip()] = _parse_scalar(v)
    return result


def _parse_inline_list(s):
    """Parse `[a, b, c]` into a list."""
    s = s.strip()
    if s.startswith("["):
        s = s[1:]
    if s.endswith("]"):
        s = s[:-1]
    return [_parse_scalar(item.strip()) for item in _split_top_level(s) if item.strip()]


def _unescape_double_quoted(s):
    """Process YAML double-quoted string escape sequences."""
    # Common YAML escapes: \\ -> \, \n -> newline, \t -> tab, \" -> "
    result = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == "\\":
                result.append("\\")
            elif nxt == "n":
                result.append("\n")
            elif nxt == "t":
                result.append("\t")
            elif nxt == '"':
                result.append('"')
            elif nxt == "/":
                result.append("/")
            else:
                # Unknown escape — keep as-is (e.g. \b for regex)
                result.append(s[i])
                result.append(nxt)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return "".join(result)


def _parse_scalar(s):
    """Parse a scalar value: int, float, bool, null, or string."""
    s = s.strip()

    # Quoted string
    if s.startswith('"') and s.endswith('"'):
        # Double-quoted: process YAML escape sequences
        return _unescape_double_quoted(s[1:-1])
    if s.startswith("'") and s.endswith("'"):
        # Single-quoted: no escapes (YAML spec)
        return s[1:-1]

    # Boolean
    lower = s.lower()
    if lower in ("true", "yes", "on"):
        return True
    if lower in ("false", "no", "off"):
        return False

    # Null
    if lower in ("null", "~", ""):
        return None

    # Integer
    try:
        return int(s)
    except ValueError:
        pass

    # Float
    try:
        return float(s)
    except ValueError:
        pass

    # Plain string (strip surrounding quotes if any stray ones)
    return s
