"""Minimal reader for the phpMyAdmin dump of the legacy site (DATABASE.sql).

Only understands what that dump contains: `INSERT INTO `table` (cols) VALUES (...), (...);`
with MySQL-escaped single-quoted strings, integers and NULL.
"""

import re
from pathlib import Path

_INSERT = re.compile(r"INSERT INTO `(\w+)` \(([^)]*)\) VALUES\s*", re.S)
_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "0": "\0", "Z": "\x1a"}


def _parse_values(sql: str, pos: int):
    """Parse `(v, v, ...), (...);` starting at pos. Returns (rows, end_pos)."""
    rows, row, i = [], None, pos
    while i < len(sql):
        c = sql[i]
        if c == "(" and row is None:
            row, i = [], i + 1
        elif c == ")" and row is not None:
            rows.append(row)
            row, i = None, i + 1
        elif c == ";" and row is None:
            return rows, i + 1
        elif c in ", \r\n\t":
            i += 1
        elif c == "'":
            buf, i = [], i + 1
            while True:
                ch = sql[i]
                if ch == "\\":
                    nxt = sql[i + 1]
                    buf.append(_ESCAPES.get(nxt, nxt))
                    i += 2
                elif ch == "'" and sql[i + 1] == "'":
                    buf.append("'")
                    i += 2
                elif ch == "'":
                    i += 1
                    break
                else:
                    buf.append(ch)
                    i += 1
            row.append("".join(buf))
        else:
            m = re.compile(r"NULL|-?\d+(?:\.\d+)?").match(sql, i)
            if not m:
                raise ValueError(f"Unexpected token at {i}: {sql[i:i+40]!r}")
            tok = m.group(0)
            row.append(None if tok == "NULL" else (float(tok) if "." in tok else int(tok)))
            i = m.end()
    raise ValueError("Unterminated INSERT")


def read_tables(path: Path) -> dict[str, list[dict]]:
    """Return {table: [row dicts]} for every INSERT in the dump."""
    sql = path.read_text(encoding="utf-8")
    tables: dict[str, list[dict]] = {}
    for m in _INSERT.finditer(sql):
        cols = [c.strip(" `") for c in m.group(2).split(",")]
        rows, _ = _parse_values(sql, m.end())
        tables.setdefault(m.group(1), []).extend(dict(zip(cols, r)) for r in rows)
    return tables
