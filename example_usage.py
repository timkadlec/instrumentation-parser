"""
Demo: Parsing orchestral instrumentation string into structured parts and simulating player assignments.
Usage:
    python example_usage.py --input "2(Pic+AltFl), 2, 2, 2+eh"
"""

import argparse
import re
from parser_utils import clean_line, normalize_abbr, split_instrumentation_line

# === Dummy Player class for simulation ===
class DummyPlayer:
    def __init__(self, position):
        self.position = position
        self.doublings = []
        self.comment = ""

    def __repr__(self):
        return f"Player {self.position} | Doublings: {self.doublings} | Comment: {self.comment}"


def assign_doublings(players, items):
    """Simulate doubling assignments (simplified, no DB or models)."""
    numbered = [item for item in items if item.strip().isdigit() or item.strip()[0].isdigit()]
    non_numbered = [item for item in items if item not in numbered]

    for item in numbered:
        match = re.match(r"(\d+)([a-zA-Z .]+)", item)
        if not match:
            continue
        count = int(match.group(1))
        abbr = normalize_abbr(match.group(2).strip())
        targets = players[-count:]
        for p in targets:
            p.doublings.append(abbr)

    if players:
        last = players[-1]
        for item in non_numbered:
            abbr = normalize_abbr(item.strip())
            last.doublings.append(abbr)


def process_section(block, section_name):
    """Process a single section block."""
    print(f"\n--- {section_name} Section ---")
    match = re.match(r"(\d+)?\((.*?)\)", block)
    if match:
        count = int(match.group(1)) if match.group(1) else 1
        doubling_items = [x.strip() for x in match.group(2).split('+')]
    else:
        parts = block.split('+')
        count = int(parts[0]) if parts[0].isdigit() else 0
        doubling_items = parts[1:] if len(parts) > 1 else []

    players = [DummyPlayer(i + 1) for i in range(count)]
    assign_doublings(players, doubling_items)

    for p in players:
        print(p)


def main():
    parser = argparse.ArgumentParser(description="Instrumentation Parser Demo")
    parser.add_argument("--input", "-i", type=str, required=True,
                        help="Instrumentation string, e.g. '2(Pic+AltFl), 2, 2, 2+eh'")
    args = parser.parse_args()

    cleaned = clean_line(args.input)
    print("Cleaned Input:", cleaned)

    parts = split_instrumentation_line(cleaned)
    print("Split Parts:", parts)

    section_names = [
        "Flutes", "Oboes", "Clarinets", "Bassoons", "Horns",
        "Trumpets", "Trombones", "Tuba", "Timpani", "Percussion", "Harp", "Piano", "Strings"
    ]

    for i, block in enumerate(parts):
        section = section_names[i] if i < len(section_names) else f"Section {i+1}"
        process_section(block, section)

    print("\n--- Normalization Examples ---")
    for abbr in ["pic", "altfl", "eh", "B-fl"]:
        print(f"Normalized '{abbr}':", normalize_abbr(abbr))


if __name__ == "__main__":
    main()
