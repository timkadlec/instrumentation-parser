"""
Demo: Parsing orchestral instrumentation string into structured parts and simulating player assignments.
"""

from parser_utils import clean_line, normalize_abbr, split_instrumentation_line
import re

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

    # Unnumbered go to last player
    if players:
        last = players[-1]
        for item in non_numbered:
            abbr = normalize_abbr(item.strip())
            last.doublings.append(abbr)


# === INPUT STRING ===
raw_input = "2(Pic+AltFl), 2, 2, 2+eh"

# === STEP 1: CLEANING ===
cleaned = clean_line(raw_input)
print("Cleaned Input:", cleaned)

# === STEP 2: SPLITTING ===
parts = split_instrumentation_line(cleaned)
print("Split Parts:", parts)

# === STEP 3: Simulate flute section ===
# We will assume the first part is the flute section
flute_block = parts[0]  # e.g. '2(Pic+AltFl)'

match = re.match(r"(\d+)?\((.*?)\)", flute_block)
if match:
    flute_count = int(match.group(1)) if match.group(1) else 1
    doubling_items = [x.strip() for x in match.group(2).split('+')]
else:
    flute_count = int(flute_block.strip()) if flute_block.strip().isdigit() else 0
    doubling_items = []

# Create dummy players
flute_players = [DummyPlayer(i + 1) for i in range(flute_count)]

# Assign doublings
assign_doublings(flute_players, doubling_items)

# === OUTPUT ===
print("\nFlute Section:")
for p in flute_players:
    print(p)

# === Normalize Examples (Optional Debug) ===
print("\nNormalization Examples:")
for abbr in ["pic", "altfl", "eh", "B-fl"]:
    print(f"Normalized '{abbr}':", normalize_abbr(abbr))
