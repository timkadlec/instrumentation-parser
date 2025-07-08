"""
Instrumentation Parser
----------------------
Parses and processes orchestral instrumentation strings and maps them to structured data models.
"""

import re
from sqlalchemy import func
from models import Instrument, ProjectInstrumentation, DoublingInstrumentation, db


def normalize_abbr(abbr):
    """Normalize instrument abbreviation by removing dots, spaces, and hyphens."""
    return abbr.lower().replace('.', '').replace(' ', '').replace('-', '')


def find_instrument_by_abbr(abbr, strict=True):
    """Find Instrument object by normalized abbreviation."""
    normalized = normalize_abbr(abbr)
    instruments = Instrument.query.all()
    for inst in instruments:
        inst_normalized = normalize_abbr(inst.abbreviation or inst.name)
        if inst_normalized == normalized:
            return inst

    if strict:
        raise ValueError(f"Instrument abbreviation not found: '{abbr}'")
    return None


def clean_line(input_line):
    """Remove invisible characters and extra spaces from input line."""
    cleaned = re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', input_line)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def split_instrumentation_line(input_line):
    """Split a string representing orchestral instrumentation into logical parts."""
    input_line = clean_line(input_line)

    parts = []
    current = ''
    parentheses_level = 0

    for char in input_line:
        if char == ',' and parentheses_level == 0:
            parts.append(current.strip())
            current = ''
        else:
            if char == '(':
                parentheses_level += 1
            elif char == ')':
                parentheses_level -= 1
            current += char

    if current:
        parts.append(current.strip())

    return parts


def assign_doublings(players, items, separate, find_instrument_func):
    """Assign doubling instruments to players based on parsed items."""
    numbered = [item for item in items if re.match(r"^\d+", item)]
    non_numbered = [item for item in items if item not in numbered]

    for item in numbered:
        match = re.match(r"(\d+)([a-zA-Z .]+)", item)
        if not match:
            continue

        count = int(match.group(1))
        abbr = match.group(2).strip()
        instrument = find_instrument_func(abbr, strict=False)
        targets = sorted(players, key=lambda p: p.position)[-count:]

        if instrument:
            for p in targets:
                existing = DoublingInstrumentation.query.filter_by(
                    instrumentation_id=p.id,
                    doubling_instrument_id=instrument.id
                ).first()

                if not existing:
                    db.session.add(DoublingInstrumentation(
                        instrumentation_id=p.id,
                        doubling_instrument_id=instrument.id,
                        separate=separate
                    ))

    target_player = sorted(players, key=lambda p: p.position)[-1] if players else None

    for abbr in non_numbered:
        instrument = find_instrument_func(abbr.strip(), strict=False)
        if instrument and target_player:
            existing = DoublingInstrumentation.query.filter_by(
                instrumentation_id=target_player.id,
                doubling_instrument_id=instrument.id
            ).first()
            if not existing:
                db.session.add(DoublingInstrumentation(
                    instrumentation_id=target_player.id,
                    doubling_instrument_id=instrument.id,
                    separate=separate
                ))
        elif target_player:
            target_player.comment = ((target_player.comment or '') + f" {abbr}").strip()
            db.session.add(target_player)


def remove_existing_instrumentation(project_id, instrument_id, separate):
    existing = ProjectInstrumentation.query.filter_by(
        project_id=project_id,
        instrument_id=instrument_id,
        separate=separate
    ).all()
    for player in existing:
        db.session.delete(player)


def remove_existing_group_instrumentation(project_id, section_id, group_id):
    group_instruments = Instrument.query.filter(
        Instrument.instrument_section_id == section_id,
        Instrument.instrument_group_id == group_id,
        Instrument.is_primary == False
    ).all()
    group_ids = [i.id for i in group_instruments]
    existing = ProjectInstrumentation.query.filter(
        ProjectInstrumentation.project_id == project_id,
        ProjectInstrumentation.instrument_id.in_(group_ids),
        ProjectInstrumentation.separate == True
    ).all()
    for player in existing:
        db.session.delete(player)


def process_instrumentation_block(project_id, section_id, instrument, block, separate=False):
    """Parse and apply an instrumentation block string to the database."""
    separate_parts = []

    match = re.match(r"(\d+)?\((.*?)\)(.*)", block)
    if match:
        base_part = match.group(0)
        count = int(match.group(1)) if match.group(1) else 1
        inside_items = re.split(r'[+,]\s*', match.group(2))
        remaining = match.group(3).lstrip('+')
        if remaining:
            separate_parts = remaining.split('+')
    else:
        parts = block.split('+')
        base_part = parts[0].strip()
        separate_parts = parts[1:]
        count = int(base_part.strip()) if base_part.strip().isdigit() else 0
        inside_items = []

    remove_existing_instrumentation(project_id, instrument.id, separate=False)
    remove_existing_group_instrumentation(project_id, section_id, instrument.instrument_group_id)

    players = []
    for i in range(count):
        player = ProjectInstrumentation(
            project_id=project_id,
            instrument_id=instrument.id,
            separate=separate,
            position=i + 1,
            concertmaster=(i == 0)
        )
        db.session.add(player)
        players.append(player)

    db.session.flush()

    if inside_items:
        if section_id == 1 and players:
            concertmaster = players[0]
            concertmaster.comment = ((concertmaster.comment or '') + " " + ", ".join(inside_items)).strip()
            db.session.add(concertmaster)
        else:
            assign_doublings(players, inside_items, separate=separate, find_instrument_func=find_instrument_by_abbr)

    max_position = len(players)

    for separate_block in separate_parts:
        sep_match = re.match(r"(\d+)?([a-zA-Z .]+)(\((.*?)\))?", separate_block.strip())
        if not sep_match:
            continue

        num = int(sep_match.group(1)) if sep_match.group(1) else 1
        abbr = sep_match.group(2).strip()
        doubling_inside = re.split(r',\s*', sep_match.group(4)) if sep_match.group(4) else []

        separate_instrument = find_instrument_by_abbr(abbr, strict=False)
        if separate_instrument:
            separate_players = []
            for i in range(num):
                p = ProjectInstrumentation(
                    project_id=project_id,
                    instrument_id=separate_instrument.id,
                    separate=True,
                    position=max_position + i + 1
                )
                db.session.add(p)
                separate_players.append(p)

            db.session.flush()

            if doubling_inside:
                assign_doublings(separate_players, doubling_inside, separate=True,
                                 find_instrument_func=find_instrument_by_abbr)

            max_position += num
