# Instrumentation Parser

A robust orchestral instrumentation parser for structured processing of instrumentation strings like:

```
12,10,8,6,4 - 2(pic+altfl),2,2,2 - 4,3,3,1 - timp+perc 2hp,pno(cel)
```

This parser is designed for use in orchestra project planning systems. It processes human-readable instrumentation lines and maps them to structured SQLAlchemy models, handling:

- Normal player assignments (e.g., `2 Fl`)
- Instrument doublings (e.g., `1(pic)`)
- Multiple doublings per player
- Separate instruments (e.g., `1 ehn`, `2 tbn` after `+`)
- Optional string section annotations

---

## Use Case

The parser is meant for use in orchestral management systems where one needs to transform shorthand instrumentation input into a database-backed structure with players, instruments, and doublings.

Originally developed as part of a larger orchestral planning system (Flask + SQLAlchemy).

---

## Main Features

- **Abbreviation normalization** (`pic`, `altfl`, `ehn`, etc.)
- **Smart player distribution**
- **Handles doublings and complex nesting**
- **Invisible character cleanup**
- **Maps to SQLAlchemy ORM models**

---

## Example Input

```python
line = "2(pic+altfl),2,2,2"
```

Will result in:

- 2 Flute players
- Player 2 doubles on Piccolo and Alto Flute

---

## Technologies

- Python 3
- SQLAlchemy ORM
- Flask (context-bound session handling)
- Regex parsing (`re`)

---

## Structure

| Function                         | Description                                                   |
|----------------------------------|---------------------------------------------------------------|
| `split_instrumentation_line()`   | Splits complex instrumentation line into top-level chunks     |
| `process_instrumentation_block()`| Parses and maps a single block to DB entries                  |
| `assign_doublings()`             | Handles instrument doublings (bracketed or trailing `+`)      |
| `remove_existing_*()`            | Cleans up database before fresh instrumentation insertion     |

---

## Integration

The parser assumes presence of SQLAlchemy models:

- `Instrument`
- `ProjectInstrumentation`
- `DoublingInstrumentation`

You'll need to adapt your database session (`db.session`) and instrument lookup model if integrating elsewhere.

---

## TODOs & Improvements

- [ ] CLI or web interface
- [ ] Tests and validation of ambiguous inputs
- [ ] Visual instrumentation renderer
- [ ] Error reporting module

---

## License

MIT License. See `LICENSE` file.

---

## Author

Created by **Tim Kadlec**, orchestral programmer, flute player & educator.

---

## Contributions

Issues and pull requests welcome. Let’s make orchestral tech elegant.
