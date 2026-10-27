"""Block 2: The Logic Crucible — Algorithmic Fluid Intelligence Problem Generator with Dynamic Difficulty Scaling."""

import random


def _render_matrix_cell_svg(shape: str, angle: int, dots: int, filled: bool) -> str:
    """Renders a crisp 88x88 SVG cell for 3x3 Matrix Reasoning."""
    fill_color = "currentColor" if filled else "none"
    fill_opacity = "0.22" if filled else "0"
    stroke_color = "currentColor"

    shape_svg = ""
    if shape == "triangle":
        shape_svg = f'<polygon points="44,14 74,68 14,68" fill="{fill_color}" fill-opacity="{fill_opacity}" stroke="{stroke_color}" stroke-width="3"/>'
    elif shape == "square":
        shape_svg = f'<rect x="18" y="18" width="52" height="52" rx="4" fill="{fill_color}" fill-opacity="{fill_opacity}" stroke="{stroke_color}" stroke-width="3"/>'
    elif shape == "diamond":
        shape_svg = f'<polygon points="44,12 76,44 44,76 12,44" fill="{fill_color}" fill-opacity="{fill_opacity}" stroke="{stroke_color}" stroke-width="3"/>'
    else:  # circle with orientation notch
        shape_svg = (
            f'<circle cx="44" cy="44" r="28" fill="{fill_color}" fill-opacity="{fill_opacity}" stroke="{stroke_color}" stroke-width="3"/>'
            f'<line x1="44" y1="44" x2="44" y2="16" stroke="{stroke_color}" stroke-width="3" stroke-linecap="round"/>'
        )

    # Orientation indicator bar on top edge of the shape before rotation
    notch_svg = f'<circle cx="44" cy="18" r="3.5" fill="{stroke_color}"/>'

    # Inner dots (1 to 3)
    dot_positions = {
        1: [(44, 46)],
        2: [(35, 46), (53, 46)],
        3: [(34, 50), (54, 50), (44, 36)],
        4: [(34, 38), (54, 38), (34, 54), (54, 54)],
    }
    dots_svg = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="3.8" fill="{stroke_color}"/>'
        for cx, cy in dot_positions.get(dots, [(44, 46)])
    )

    return (
        f'<svg viewBox="0 0 88 88" width="82" height="82" aria-hidden="true">'
        f'<g transform="rotate({angle} 44 44)">{shape_svg}{notch_svg}</g>'
        f'{dots_svg}'
        f'</svg>'
    )


def generate_matrix_puzzle(difficulty: int) -> dict:
    """Generates a 3x3 Raven's-style progressive matrix puzzle."""
    shapes = ["triangle", "square", "circle"]
    random.shuffle(shapes)
    rot_step = 90 if difficulty <= 2 else 45
    base_angle = random.choice([0, 45, 90])

    # Build 3x3 grid cells
    grid_svgs = []
    for r in range(3):
        row_cells = []
        for c in range(3):
            # Rule 1: Shape is determined by (r + c) % 3 at higher difficulty, or by column c at lower difficulty
            shape = shapes[c] if difficulty <= 2 else shapes[(r + c) % 3]
            # Rule 2: Rotation advances by rot_step across columns and rows
            angle = (base_angle + (r + c) * rot_step) % 360
            # Rule 3: Inner dot count progresses 1 -> 2 -> 3 across rows (or (r + c) % 3 + 1)
            dots = (r % 3) + 1 if difficulty == 1 else ((r + c) % 3) + 1
            # Rule 4: Shaded fill alternates on diagonal when difficulty >= 3
            filled = ((r + c) % 2 == 0) if difficulty >= 3 else (r == 1)

            if r == 2 and c == 2:
                correct_params = (shape, angle, dots, filled)
                row_cells.append(None)  # Missing 9th cell
            else:
                row_cells.append(_render_matrix_cell_svg(shape, angle, dots, filled))
        grid_svgs.append(row_cells)

    c_shape, c_angle, c_dots, c_filled = correct_params
    correct_svg = _render_matrix_cell_svg(c_shape, c_angle, c_dots, c_filled)

    # Create 3 distinct distractors that break 1 or 2 rule axes
    distractor_params = [
        (shapes[(shapes.index(c_shape) + 1) % 3], c_angle, c_dots, c_filled),
        (c_shape, (c_angle + 90) % 360, c_dots, not c_filled),
        (c_shape, c_angle, (c_dots % 3) + 1, c_filled),
    ]
    options_list = [correct_svg] + [_render_matrix_cell_svg(*dp) for dp in distractor_params]

    # Shuffle options while tracking correct index
    indexed = list(enumerate(options_list))
    random.shuffle(indexed)
    correct_idx = next(i for i, (orig_i, _) in enumerate(indexed) if orig_i == 0)
    final_options = [svg for _, svg in indexed]

    rule_desc = (
        f"Row/Column Progression: Shape shifts cyclically ({', '.join(shapes)}), "
        f"orientation rotates by +{rot_step}° per step (target {c_angle}°), "
        f"and inner dot count follows (row + col) mod 3 + 1 = {c_dots} dots."
    )

    return {
        "puzzle_type": "matrix",
        "puzzle_type_label": "Matrix Reasoning (3×3 Progressive)",
        "difficulty": difficulty,
        "tier": "Foundational" if difficulty <= 2 else ("Intermediate" if difficulty <= 3 else "Advanced"),
        "prompt": "Deduce the row and column transformation rules across the 3×3 matrix and select the missing bottom-right cell [?]:",
        "grid_svgs": grid_svgs,
        "options": final_options,
        "options_are_svg": True,
        "correct_index": correct_idx,
        "explanation": rule_desc,
    }


def generate_sequence_puzzle(difficulty: int) -> dict:
    """Generates an algorithmic sequence completion puzzle scaled by difficulty."""
    if difficulty == 1:
        start = random.randint(2, 9)
        step = random.randint(3, 6)
        seq = [start]
        for i in range(1, 6):
            seq.append(seq[-1] + step * i)
        ans = seq[-1] + step * 6
        rule = f"Second-order arithmetic difference: add +{step}×1, +{step}×2, +{step}×3, ... (+{step * 6} next)."
    elif difficulty == 2:
        a = random.randint(2, 5)
        b = random.randint(2, 4)
        seq = [a]
        for i in range(5):
            if i % 2 == 0:
                seq.append(seq[-1] * 2)
            else:
                seq.append(seq[-1] + b)
        ans = seq[-1] + b
        rule = f"Alternating operator recurrence: (×2), then (+{b}), repeating."
    elif difficulty == 3:
        a, b = random.randint(1, 4), random.randint(2, 6)
        offset = random.randint(1, 3)
        seq = [a, b]
        for _ in range(4):
            seq.append(seq[-1] + seq[-2] + offset)
        ans = seq[-1] + seq[-2] + offset
        rule = f"Modified Fibonacci recurrence: T(n) = T(n-1) + T(n-2) + {offset}."
    else:
        primes = [2, 3, 5, 7, 11, 13, 17]
        base = random.randint(1, 4)
        seq = [base + (i + 1) ** 2 + primes[i] for i in range(6)]
        ans = base + 7**2 + primes[6]
        rule = f"Composite polynomial-prime synthesis: T(n) = {base} + n² + Prime(n), so T(7) = {base} + 49 + 17 = {ans}."

    distractors = list({ans + random.choice([-4, -2, 2, 4, 6, -6]) for _ in range(6)} - {ans})[:3]
    while len(distractors) < 3:
        distractors.append(ans + len(distractors) + 3)

    options = [str(ans)] + [str(d) for d in distractors[:3]]
    indexed = list(enumerate(options))
    random.shuffle(indexed)
    correct_idx = next(i for i, (orig_i, _) in enumerate(indexed) if orig_i == 0)

    seq_display = "  →  ".join(str(x) for x in seq) + "  →  [ ? ]"
    return {
        "puzzle_type": "sequence",
        "puzzle_type_label": "Algorithmic Sequence Completion",
        "difficulty": difficulty,
        "tier": "Foundational" if difficulty <= 2 else ("Intermediate" if difficulty <= 3 else "Advanced"),
        "prompt": f"Identify the underlying generator function and compute the 7th term:\n{seq_display}",
        "sequence_display": seq_display,
        "options": [val for _, val in indexed],
        "options_are_svg": False,
        "correct_index": correct_idx,
        "explanation": rule,
    }


def generate_cryptogram_puzzle(difficulty: int) -> dict:
    """Generates a cipher/cryptogram deduction puzzle."""
    corpus = [
        ("ENTROPY ALWAYS INCREASES", "INCREASES", ["THERMODYNAMICS", "DECREASES", "EQUILIBRIUM"]),
        ("INVERT ALWAYS INVERT", "INVERT", ["DEDUCE", "DIVERT", "INSERT"]),
        ("EMPIRICAL FALSIFICATION", "EMPIRICAL", ["DOGMA", "SPHERICAL", "RHETORICAL"]),
        ("SECOND ORDER CONSEQUENCE", "SECOND", ["BEYOND", "RECORD", "FIRST"]),
        ("AXIOMATIC DECONSTRUCTION", "AXIOMATIC", ["AUTOMATIC", "PRAGMATIC", "SYSTEMATIC"]),
    ]
    phrase, target_word, distractors = random.choice(corpus)
    shift = random.choice([3, 4, 5, 7]) if difficulty <= 3 else random.choice([9, 11, 13])

    def encode(text: str) -> str:
        out = []
        for ch in text:
            if "A" <= ch <= "Z":
                out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
            else:
                out.append(ch)
        return "".join(out)

    encoded_phrase = encode(phrase)
    encoded_target = encode(target_word)
    first_word = phrase.split()[0]
    hint = f"Clue: Cipher is a uniform modular alphabet shift (+k mod 26). Letter '{encode(phrase[0])}' decodes to '{phrase[0]}', and '{encode(phrase[1])}' decodes to '{phrase[1]}'."

    options = [target_word] + distractors
    indexed = list(enumerate(options))
    random.shuffle(indexed)
    correct_idx = next(i for i, (orig_i, _) in enumerate(indexed) if orig_i == 0)

    return {
        "puzzle_type": "cryptogram",
        "puzzle_type_label": "Cryptographic Pattern Deduction",
        "difficulty": difficulty,
        "tier": "Foundational" if difficulty <= 2 else ("Intermediate" if difficulty <= 3 else "Advanced"),
        "prompt": f"Ciphertext: \"{encoded_phrase}\"\n{hint}\nDecode the encrypted token \"{encoded_target}\":",
        "sequence_display": f"CIPHER: {encoded_phrase}  |  TARGET: {encoded_target}",
        "options": [val for _, val in indexed],
        "options_are_svg": False,
        "correct_index": correct_idx,
        "explanation": f"Applying Caesar shift -{shift} (mod 26) decodes '{encoded_phrase}' → '{phrase}', so '{encoded_target}' = '{target_word}'.",
    }


def _render_polyomino_svg(coords: set[tuple[int, int]], grid_size: int = 4) -> str:
    """Renders a 4x4 polyomino grid SVG for spatial rotation reasoning."""
    cell = 18
    pad = 8
    total = grid_size * cell + pad * 2
    rects = []
    for r in range(grid_size):
        for c in range(grid_size):
            x = pad + c * cell
            y = pad + r * cell
            if (r, c) in coords:
                fill = "currentColor"
                opacity = "0.85"
            else:
                fill = "currentColor"
                opacity = "0.08"
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" rx="2" fill="{fill}" fill-opacity="{opacity}" stroke="currentColor" stroke-opacity="0.25" stroke-width="1"/>'
            )
    return f'<svg viewBox="0 0 {total} {total}" width="84" height="84" aria-hidden="true">{"".join(rects)}</svg>'


def _rotate_90_cw(coords: set[tuple[int, int]], n: int = 4) -> set[tuple[int, int]]:
    return {(c, n - 1 - r) for r, c in coords}


def _flip_horiz(coords: set[tuple[int, int]], n: int = 4) -> set[tuple[int, int]]:
    return {(r, n - 1 - c) for r, c in coords}


def generate_spatial_puzzle(difficulty: int) -> dict:
    """Generates a chiral 2D/voxel spatial rotation vs. mirror-reflection discrimination puzzle."""
    # Asymmetric chiral polyomino shapes on a 4x4 grid (never equal to their own mirror image)
    chiral_shapes = [
        {(0, 1), (1, 1), (2, 1), (2, 2), (1, 0)},  # F-pentomino
        {(0, 0), (1, 0), (2, 0), (2, 1), (3, 1)},  # N-pentomino
        {(0, 1), (0, 2), (1, 0), (1, 1), (2, 1), (2, 2)},  # Asymmetric hexomino
        {(0, 0), (0, 1), (1, 1), (2, 1), (2, 2), (3, 2)},  # Stepped Z-hexomino
    ]
    base_shape = random.choice(chiral_shapes)
    rot_steps = random.choice([1, 2, 3])  # 90°, 180°, or 270° CW
    target_angle = rot_steps * 90

    rotated = base_shape
    for _ in range(rot_steps):
        rotated = _rotate_90_cw(rotated)

    # Distractors are chiral mirror flips + rotations (impossible via rigid 2D rotation) or mutated cells
    mirrored_base = _flip_horiz(base_shape)
    d1 = mirrored_base
    d2 = _rotate_90_cw(mirrored_base)
    d3 = _rotate_90_cw(_rotate_90_cw(mirrored_base))

    ref_svg = _render_polyomino_svg(base_shape)
    options_svg = [
        _render_polyomino_svg(rotated),
        _render_polyomino_svg(d1),
        _render_polyomino_svg(d2),
        _render_polyomino_svg(d3),
    ]

    indexed = list(enumerate(options_svg))
    random.shuffle(indexed)
    correct_idx = next(i for i, (orig_i, _) in enumerate(indexed) if orig_i == 0)

    return {
        "puzzle_type": "spatial",
        "puzzle_type_label": "Spatial Mental Rotation (Chiral Discrimination)",
        "difficulty": difficulty,
        "tier": "Foundational" if difficulty <= 2 else ("Intermediate" if difficulty <= 3 else "Advanced"),
        "prompt": f"Mentally rotate the Reference Polyomino by {target_angle}° clockwise in-plane. Select the true rigid rotation (reject chiral mirror reflections):",
        "reference_svg": ref_svg,
        "options": [svg for _, svg in indexed],
        "options_are_svg": True,
        "correct_index": correct_idx,
        "explanation": f"Rotating each coordinate (r, c) → (c, 3-r) {rot_steps} time(s) ({target_angle}° CW) preserves chirality; the other 3 candidates are mirror-reflected enantiomorphs.",
    }


def generate_crucible_problem(difficulty: int = 1, preferred_type: str | None = None) -> dict:
    """Dispatches to one of the 4 required Logic Crucible problem generators."""
    difficulty = max(1, min(5, difficulty))
    kinds = ["matrix", "sequence", "cryptogram", "spatial"]
    chosen = preferred_type if preferred_type in kinds else random.choice(kinds)

    if chosen == "matrix":
        return generate_matrix_puzzle(difficulty)
    if chosen == "sequence":
        return generate_sequence_puzzle(difficulty)
    if chosen == "cryptogram":
        return generate_cryptogram_puzzle(difficulty)
    return generate_spatial_puzzle(difficulty)
