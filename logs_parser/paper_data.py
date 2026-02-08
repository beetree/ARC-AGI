import argparse
import csv
import os
import re
import sys
import json

try:
    from .utils import load_answers
    from .parsing import parse_log_file
except ImportError:
    from utils import load_answers
    from parsing import parse_log_file


def scan_logs(
    directory: str,
) -> tuple[
    list[tuple[str, int]],
    list[str],
    dict[str, str],
    dict[tuple[str, int], dict[str, str]],
    dict[tuple[str, int], str],
]:
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        return [], [], {}

    pattern = re.compile(r'([a-f0-9]{8})_(\d+)_step_([a-zA-Z0-9]+)\.json$')
    pairs = set()
    method_keys = set()
    method_labels: dict[str, str] = {}
    statuses: dict[tuple[str, int], dict[str, str]] = {}
    overall_status: dict[tuple[str, int], str] = {}

    answers = load_answers(os.getcwd())

    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if not match:
            continue

        task_id = match.group(1)
        test_id_str = match.group(2)
        step_name = match.group(3)
        test_id = int(test_id_str)
        task_key = (task_id, test_id)
        pairs.add(task_key)

        filepath = os.path.join(directory, filename)
        result = parse_log_file(filepath, task_id, test_id_str, step_name, answers)
        if not result:
            continue

        calls = []
        res_type = result.get("type")
        data = result.get("data", {})
        if res_type == "generic":
            calls = data.get("calls", [])
        elif res_type == "nested":
            for sub_calls in data.get("steps", {}).values():
                calls.extend(sub_calls)
        elif res_type == "finish":
            calls = data.get("calls", [])
            finish_status = data.get("finish_status")
            if finish_status in ("PASS", "SOLVED"):
                overall_status[task_key] = "PASS"
            elif finish_status:
                overall_status.setdefault(task_key, "FAIL")

        for call in calls:
            status = call.get("status")
            if status not in ("PASS", "FAIL"):
                continue

            method = call.get("run_id") or call.get("name")
            if not method:
                continue

            method_key = normalize_method_key(method)
            method_label = classify_method_label(method_key)

            method_keys.add(method_key)
            method_labels[method_key] = method_label
            method_statuses = statuses.setdefault(task_key, {})
            existing = method_statuses.get(method_key)
            if existing == "PASS":
                continue
            if status == "PASS" or existing is None:
                method_statuses[method_key] = status

    sorted_pairs = sorted(pairs, key=lambda x: (x[0], x[1]))
    label_order = [
        "Claude-Text",
        "Gemini-Text",
        "GPT-Text",
        "GPT-Deep",
        "Gemini-Image",
        "GPT-Image",
        "Gemini-Code-Tools",
        "GPT-Code",
        "GPT-Code-Tools",
    ]
    label_index = {label: idx for idx, label in enumerate(label_order)}
    sorted_method_keys = sorted(
        method_keys,
        key=lambda k: (label_index.get(method_labels.get(k, ""), len(label_order)), method_labels.get(k, ""), k),
    )
    return sorted_pairs, sorted_method_keys, method_labels, statuses, overall_status


def normalize_method_key(raw_name: str) -> str:
    parts = raw_name.split("_")
    cleaned_parts = []
    skip_next = False

    for idx, part in enumerate(parts):
        if skip_next:
            skip_next = False
            continue
        if part == "step" and idx + 1 < len(parts):
            skip_next = True
            continue
        cleaned_parts.append(part)

    if cleaned_parts and re.fullmatch(r"\d{9,}(\.\d+)?", cleaned_parts[-1]):
        cleaned_parts = cleaned_parts[:-1]

    return "_".join(cleaned_parts)


def classify_method_label(method_key: str) -> str:
    lowered = method_key.lower()

    if "claude" in lowered or "opus" in lowered or "sonnet" in lowered or "haiku" in lowered:
        vendor = "Claude"
    elif "gemini" in lowered:
        vendor = "Gemini"
    elif "gpt" in lowered:
        vendor = "GPT"
    else:
        vendor = "GPT"

    if vendor == "Claude":
        kind = "Text"
    elif "image" in lowered:
        kind = "Image"
    elif "deep" in lowered or "thinking" in lowered:
        kind = "Deep"
    elif "codegen" in lowered or "tool" in lowered or "tools" in lowered:
        kind = "Code-Tools"
    elif "code" in lowered:
        if vendor == "Gemini":
            kind = "Code-Tools"
        else:
            kind = "Code"
    else:
        kind = "Text"

    if vendor == "Gemini" and kind == "Deep":
        kind = "Text"

    return f"{vendor}-{kind}"


def category_for_label(label: str) -> str:
    if label.endswith("Text"):
        return "Text"
    if label.endswith("Deep"):
        return "Deep"
    if label.endswith("Image"):
        return "Image"
    if "Code" in label:
        return "Code"
    return ""


def type_for_label(label: str) -> str:
    if label.endswith("Image"):
        return "Image"
    if "Code" in label:
        return "Code"
    if label.endswith("Deep"):
        return "Text"
    if label.endswith("Text"):
        return "Text"
    return ""


def compute_many_candidates_matrix(
    pairs: list[tuple[str, int]],
    statuses: dict[tuple[str, int], dict[str, str]],
    method_labels: dict[str, str],
    threshold: int = 29,
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, list[str]]], int]:
    types = ["Text", "Image", "Code"]
    counts = {row: {col: 0 for col in types} for row in types}
    lists = {row: {col: [] for col in types} for row in types}
    total_pairs = 0

    for pair in pairs:
        if len(statuses.get(pair, {})) < threshold:
            continue
        total_pairs += 1
        pass_by_type = {t: False for t in types}
        for method_key, status in statuses.get(pair, {}).items():
            if status != "PASS":
                continue
            label = method_labels.get(method_key, "")
            t = type_for_label(label)
            if t in pass_by_type:
                pass_by_type[t] = True

        pair_label = f"{pair[0]}:{pair[1]}"
        for row in types:
            if not pass_by_type[row]:
                continue
            for col in types:
                if not pass_by_type[col]:
                    counts[row][col] += 1
                    lists[row][col].append(pair_label)

    return counts, lists, total_pairs


def compute_only_category_counts(
    pairs: list[tuple[str, int]],
    statuses: dict[tuple[str, int], dict[str, str]],
    method_labels: dict[str, str],
    threshold: int = 29,
) -> tuple[dict[str, int], dict[str, list[str]]]:
    counts = {"Text": 0, "Image": 0, "Code": 0}
    lists = {"Text": [], "Image": [], "Code": []}

    for pair in pairs:
        if len(statuses.get(pair, {})) < threshold:
            continue

        present = {"Text": False, "Image": False, "Code": False}
        for method_key, status in statuses.get(pair, {}).items():
            if status != "PASS":
                continue
            label = method_labels.get(method_key, "")
            t = type_for_label(label)
            if t in present:
                present[t] = True

        pair_label = f"{pair[0]}:{pair[1]}"
        if present["Text"] and not present["Image"] and not present["Code"]:
            counts["Text"] += 1
            lists["Text"].append(pair_label)
        if present["Image"] and not present["Text"] and not present["Code"]:
            counts["Image"] += 1
            lists["Image"].append(pair_label)
        if present["Code"] and not present["Text"] and not present["Image"]:
            counts["Code"] += 1
            lists["Code"].append(pair_label)

    return counts, lists


def classify_model_modality_bucket(method_key: str) -> str | None:
    lowered = method_key.lower()

    if "claude-opus-4.5" in lowered:
        return "Claude Opus 4.5 (text)"

    if "gemini-3" in lowered:
        if "image" in lowered:
            return "Gemini 3 Preview (image)"
        if "codegen" in lowered or "tool" in lowered or "tools" in lowered:
            return "Gemini 3 Preview (code, tools)"
        return "Gemini 3 Preview (text)"

    if "gpt-5.2" in lowered:
        if "deep" in lowered or "deep_thinking" in lowered:
            return "GPT-5.2 (deep think)"
        if "image" in lowered:
            return "GPT-5.2 (image)"
        if "codegen" in lowered or "tool" in lowered or "tools" in lowered:
            return "GPT-5.2 (code, tools)"
        return "GPT-5.2 (text)"

    return None


def compute_only_model_modality_counts(
    pairs: list[tuple[str, int]],
    statuses: dict[tuple[str, int], dict[str, str]],
    threshold: int = 29,
) -> tuple[dict[str, int], dict[str, list[str]]]:
    buckets = [
        "Claude Opus 4.5 (text)",
        "Gemini 3 Preview (text)",
        "GPT-5.2 (text)",
        "GPT-5.2 (deep think)",
        "Gemini 3 Preview (image)",
        "GPT-5.2 (image)",
        "Gemini 3 Preview (code, tools)",
        "GPT-5.2 (code, tools)",
    ]
    counts = {b: 0 for b in buckets}
    lists = {b: [] for b in buckets}

    for pair in pairs:
        if len(statuses.get(pair, {})) < threshold:
            continue

        present = {b: False for b in buckets}
        for method_key, status in statuses.get(pair, {}).items():
            if status != "PASS":
                continue
            bucket = classify_model_modality_bucket(method_key)
            if bucket in present:
                present[bucket] = True

        active = [b for b, ok in present.items() if ok]
        if len(active) != 1:
            continue

        pair_label = f"{pair[0]}:{pair[1]}"
        bucket = active[0]
        counts[bucket] += 1
        lists[bucket].append(pair_label)

    return counts, lists


def write_many_candidates_matrix(
    output_dir: str,
    counts: dict[str, dict[str, int]],
    total_pairs: int,
    threshold: int,
    only_counts: dict[str, int],
    matrix_lists: dict[str, dict[str, list[str]]],
    only_lists: dict[str, list[str]],
    only_model_modality_counts: dict[str, int],
    only_model_modality_lists: dict[str, list[str]],
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "many_candidates_matrix.md")
    types = ["Text", "Image", "Code"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Many Candidates Matrix\n\n")
        f.write("## Methodology\n\n")
        f.write(
            "We first **reduce the sample** to only Task:Test pairs that have **\"many\" candidates**, "
            f"defined here as having **>= {threshold} filled candidate columns** in the methodology matrix "
            f"(i.e., >= {threshold} distinct method columns with a PASS or FAIL entry).\n\n"
        )
        f.write(
            "We then classify every method column into one of three types: **Text**, **Image**, or **Code**. "
            "**Deep** is folded into **Text**. A Task:Test is considered to have a PASS for a type "
            "if **any method in that type** has status **PASS**.\n\n"
        )
        f.write(
            "The 3×3 matrix counts, for each row type R and column type C, how many Task:Test pairs "
            "have **at least one PASS in R** and **zero PASS in C**. "
            "A Task:Test can contribute to multiple cells if it satisfies multiple row/column conditions. "
            "The diagonal is marked NA by definition.\n\n"
        )
        f.write(f"- Threshold (many candidates): >= {threshold} filled columns\n")
        f.write(f"- Task:Test count after filtering: {total_pairs}\n\n")
        f.write("| | Text | Image | Code |\n")
        f.write("| --- | --- | --- | --- |\n")
        for row in types:
            row_vals = []
            for col in types:
                if row == col:
                    row_vals.append("NA")
                else:
                    row_vals.append(str(counts[row][col]))
            f.write(f"| {row} | " + " | ".join(row_vals) + " |\n")

        f.write("\n### Task:Test Lists by Cell\n\n")
        for row in types:
            for col in types:
                if row == col:
                    continue
                cell_list = matrix_lists[row][col]
                label = f"{row} PASS, {col} NO PASS"
                f.write(f"**{label}** ({len(cell_list)}):\n\n")
                if cell_list:
                    f.write(", ".join(cell_list) + "\n\n")
                else:
                    f.write("(none)\n\n")

        f.write("\n## Only-One-Category Presence\n\n")
        f.write(
            f"Counts of Task:Test problems (with >= {threshold} filled columns) that have **at least one PASS** "
            "in the given category and **zero PASS** in the other two.\n\n"
        )
        f.write("| Category | Count |\n")
        f.write("| --- | --- |\n")
        f.write(f"| Text only | {only_counts.get('Text', 0)} |\n")
        f.write(f"| Image only | {only_counts.get('Image', 0)} |\n")
        f.write(f"| Code only | {only_counts.get('Code', 0)} |\n")

        f.write("\n### Task:Test Lists (Only-One-Category)\n\n")
        f.write(f"**Text only** ({len(only_lists.get('Text', []))}):\n\n")
        f.write(", ".join(only_lists.get('Text', [])) + "\n\n" if only_lists.get('Text') else "(none)\n\n")
        f.write(f"**Image only** ({len(only_lists.get('Image', []))}):\n\n")
        f.write(", ".join(only_lists.get('Image', [])) + "\n\n" if only_lists.get('Image') else "(none)\n\n")
        f.write(f"**Code only** ({len(only_lists.get('Code', []))}):\n\n")
        f.write(", ".join(only_lists.get('Code', [])) + "\n\n" if only_lists.get('Code') else "(none)\n\n")

        f.write("\n## Only-One-Category PASS (Model/Modality)\n\n")
        f.write(
            f"Counts of Task:Test problems (with >= {threshold} filled columns) that have **at least one PASS** "
            "in the given bucket and **zero PASS** in the other listed buckets.\n\n"
        )
        bucket_order = [
            "Claude Opus 4.5 (text)",
            "Gemini 3 Preview (text)",
            "GPT-5.2 (text)",
            "GPT-5.2 (deep think)",
            "Gemini 3 Preview (image)",
            "GPT-5.2 (image)",
            "Gemini 3 Preview (code, tools)",
            "GPT-5.2 (code, tools)",
        ]
        f.write("| Bucket | Count |\n")
        f.write("| --- | --- |\n")
        for bucket in bucket_order:
            f.write(f"| {bucket} only | {only_model_modality_counts.get(bucket, 0)} |\n")

        f.write("\n### Task:Test Lists (Only-One-Bucket)\n\n")
        for bucket in bucket_order:
            items = only_model_modality_lists.get(bucket, [])
            f.write(f"**{bucket} only** ({len(items)}):\n\n")
            if items:
                f.write(", ".join(items) + "\n\n")
            else:
                f.write("(none)\n\n")

    return output_path


def sorted_pairs_by_filled(
    pairs: list[tuple[str, int]],
    statuses: dict[tuple[str, int], dict[str, str]],
) -> list[tuple[str, int]]:
    def filled_count(pair: tuple[str, int]) -> int:
        return len(statuses.get(pair, {}))

    def pass_count(pair: tuple[str, int]) -> int:
        return sum(1 for status in statuses.get(pair, {}).values() if status == "PASS")

    return sorted(pairs, key=lambda p: (filled_count(p), pass_count(p), p[0], p[1]))


def write_methodology_matrix_csv(
    output_dir: str,
    pairs: list[tuple[str, int]],
    method_keys: list[str],
    method_labels: dict[str, str],
    statuses: dict[tuple[str, int], dict[str, str]],
    overall_status: dict[tuple[str, int], str],
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "methodology_matrix.csv")

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        headers = ["Task", "Test", "Overall"] + [method_labels.get(k, k) for k in method_keys]
        writer.writerow(headers)
        category_row = ["", "", ""] + [category_for_label(method_labels.get(k, k)) for k in method_keys]
        writer.writerow(category_row)

        sorted_pairs = sorted_pairs_by_filled(pairs, statuses)
        for task_id, test_id in sorted_pairs:
            row = [task_id, str(test_id), overall_status.get((task_id, test_id), "")]
            method_statuses = statuses.get((task_id, test_id), {})
            for method_key in method_keys:
                row.append(method_statuses.get(method_key, ""))
            writer.writerow(row)

    return output_path


def write_methodology_matrix_md(
    output_dir: str,
    pairs: list[tuple[str, int]],
    method_keys: list[str],
    method_labels: dict[str, str],
    statuses: dict[tuple[str, int], dict[str, str]],
    overall_status: dict[tuple[str, int], str],
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "methodology_matrix.md")

    def escape_cell(text: str) -> str:
        return text.replace("|", "\\|")

    headers = ["Task", "Test", "Overall"] + [method_labels.get(k, k) for k in method_keys]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Methodology Matrix\n\n")
        f.write("| " + " | ".join([escape_cell(h) for h in headers]) + " |\n")
        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        category_row = ["", "", ""] + [category_for_label(method_labels.get(k, k)) for k in method_keys]
        f.write("| " + " | ".join(category_row) + " |\n")

        sorted_pairs = sorted_pairs_by_filled(pairs, statuses)
        for task_id, test_id in sorted_pairs:
            row = [task_id, str(test_id), overall_status.get((task_id, test_id), "")]
            method_statuses = statuses.get((task_id, test_id), {})
            for method_key in method_keys:
                row.append(method_statuses.get(method_key, ""))
            f.write("| " + " | ".join(row) + " |\n")

    return output_path


def write_methodology_matrix_image(output_dir: str, csv_path: str) -> str:
    rows = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        raise ValueError("CSV appears to be empty.")

    cols = max(len(r) for r in rows)
    for row in rows:
        if len(row) < cols:
            row.extend([""] * (cols - len(row)))

    category_row = rows[1] if len(rows) > 1 else []
    data_rows = rows[2:] if len(rows) > 2 else []

    display_start_col = 2  # Overall + method columns
    display_cols = max(cols - display_start_col, 0)

    col_categories = []
    for idx in range(display_start_col, cols):
        if idx == display_start_col:
            col_categories.append("Overall")
        else:
            label = category_row[idx] if idx < len(category_row) else ""
            if label == "Deep":
                label = "Text"
            if label not in ("Text", "Image", "Code"):
                label = label or "Other"
            col_categories.append(label)

    groups: list[tuple[str, int, int]] = []
    if display_cols > 0:
        current = col_categories[0]
        start = 0
        for i in range(1, display_cols):
            if col_categories[i] != current:
                groups.append((current, start, i - 1))
                current = col_categories[i]
                start = i
        groups.append((current, start, display_cols - 1))

    row_labels = []
    for row in data_rows:
        task = row[0] if len(row) > 0 else ""
        test = row[1] if len(row) > 1 else ""
        if task or test:
            row_labels.append(f"{task}:{test}")
        else:
            row_labels.append("")

    cell_size = 14
    overall_width = cell_size * 4
    gap_size = 6
    label_pad_x = 4
    label_pad_y = 2
    grid_color = (220, 220, 220)
    pass_color = (70, 180, 70)
    fail_color = (200, 70, 70)
    empty_color = (255, 255, 255)

    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore

        font = ImageFont.load_default()

        def text_size(text: str) -> tuple[int, int]:
            if not text:
                return (0, 0)
            bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=font)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])

        max_row_label_width = 0
        max_row_label_height = 0
        for label in row_labels:
            w, h = text_size(label)
            if w > max_row_label_width:
                max_row_label_width = w
            if h > max_row_label_height:
                max_row_label_height = h

        max_col_label_width = 0
        max_col_label_height = 0
        for label, _, _ in groups:
            w, h = text_size(label)
            if w > max_col_label_width:
                max_col_label_width = w
            if h > max_col_label_height:
                max_col_label_height = h

        row_label_width = max_row_label_width + label_pad_x * 2
        header_height = max(cell_size, max_col_label_height + label_pad_y * 2)
        row_height = max(cell_size, max_row_label_height + label_pad_y * 2)

        col_widths = [overall_width if idx == 0 else cell_size for idx in range(display_cols)]
        gap_starts = {start for _, start, _ in groups[1:]}
        col_x = [0] * display_cols
        cursor = 0
        for col_idx in range(display_cols):
            if col_idx in gap_starts:
                cursor += gap_size
            col_x[col_idx] = cursor
            cursor += col_widths[col_idx]

        def col_left(col_idx: int) -> int:
            return row_label_width + col_x[col_idx]

        width = row_label_width + cursor + 1
        height = header_height + len(data_rows) * row_height + 1
        image = Image.new("RGB", (width, height), empty_color)
        draw = ImageDraw.Draw(image)

        header_bg = (245, 245, 245)
        for label, start, end in groups:
            x0 = col_left(start)
            x1 = col_left(end) + col_widths[end]
            y0 = 0
            y1 = header_height
            draw.rectangle([x0, y0, x1, y1], fill=header_bg, outline=grid_color)
            if label:
                tw, th = text_size(label)
                tx = x0 + (x1 - x0 - tw) // 2
                ty = y0 + (header_height - th) // 2
                draw.text((tx, ty), label, fill=(0, 0, 0), font=font)

        for r_idx, row in enumerate(data_rows):
            row_y0 = header_height + r_idx * row_height

            label = row_labels[r_idx] if r_idx < len(row_labels) else ""
            if label:
                tw, th = text_size(label)
                tx = label_pad_x
                ty = row_y0 + (row_height - th) // 2
                draw.text((tx, ty), label, fill=(0, 0, 0), font=font)

            for c_idx in range(display_cols):
                value_idx = display_start_col + c_idx
                value = row[value_idx] if value_idx < len(row) else ""
                if value == "PASS":
                    fill = pass_color
                elif value == "FAIL":
                    fill = fail_color
                else:
                    fill = empty_color
                x0 = col_left(c_idx)
                y0 = row_y0 + (row_height - cell_size) // 2
                x1 = x0 + col_widths[c_idx]
                y1 = y0 + cell_size
                draw.rectangle([x0, y0, x1, y1], fill=fill, outline=grid_color)

        draw.line([(row_label_width, 0), (row_label_width, height)], fill=grid_color)
        draw.line([(row_label_width, header_height), (width, header_height)], fill=grid_color)

        output_path = os.path.join(output_dir, "methodology_matrix.png")
        image.save(output_path)
        return output_path
    except Exception:
        col_widths = [overall_width if idx == 0 else cell_size for idx in range(display_cols)]
        gap_starts = {start for _, start, _ in groups[1:]}
        col_x = [0] * display_cols
        cursor = 0
        for col_idx in range(display_cols):
            if col_idx in gap_starts:
                cursor += gap_size
            col_x[col_idx] = cursor
            cursor += col_widths[col_idx]

        width = cursor
        height = len(data_rows) * cell_size
        output_path = os.path.join(output_dir, "methodology_matrix.ppm")
        with open(output_path, "w", encoding="ascii") as f:
            f.write(f"P3\n{width} {height}\n255\n")
            for y in range(height):
                row_idx = y // cell_size
                y_border = (y % cell_size) == 0
                line_parts = []
                for x in range(width):
                    col_idx = None
                    for idx in range(display_cols):
                        x0 = col_x[idx]
                        x1 = x0 + col_widths[idx]
                        if x0 <= x < x1:
                            col_idx = idx
                            break
                    if col_idx is None:
                        color = empty_color
                        line_parts.append(f"{color[0]} {color[1]} {color[2]}")
                        continue
                    x_border = ((x - col_x[col_idx]) % col_widths[col_idx]) == 0
                    if x_border or y_border:
                        color = grid_color
                    else:
                        value_idx = display_start_col + col_idx
                        value = data_rows[row_idx][value_idx] if row_idx < len(data_rows) else ""
                        if value == "PASS":
                            color = pass_color
                        elif value == "FAIL":
                            color = fail_color
                        else:
                            color = empty_color
                    line_parts.append(f"{color[0]} {color[1]} {color[2]}")
                f.write(" ".join(line_parts) + "\n")
        return output_path


def write_judge_performance_dataset(logs_dir: str, output_dir: str) -> tuple[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "judge_performance.csv")
    summary_path = os.path.join(output_dir, "judge_performance_summary.md")

    pattern = re.compile(r'.*([a-f0-9]{8})_(\d+)_step_finish\.json$')
    rows = []

    totals = {
        "total": 0,
        "council_top2": 0,
        "judge0_top2": 0,
        "judge1_top2": 0,
        "judge2_top2": 0,
    }

    for filename in os.listdir(logs_dir):
        match = pattern.match(filename)
        if not match:
            continue

        task_id = match.group(1)
        test_id = int(match.group(2))
        filepath = os.path.join(logs_dir, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        correct = data.get("correct_solution")
        if correct is None:
            continue

        selection_details = data.get("selection_details", {}) or {}
        sel_process = selection_details.get("selection_process", {}) or {}
        scoreboard = sel_process.get("scoreboard", []) or []

        council_top2_correct = False
        for item in scoreboard[:2]:
            if isinstance(item, dict) and item.get("grid") == correct:
                council_top2_correct = True
                break

        judges = selection_details.get("judges", {}) or {}
        council = judges.get("duo_pick_council", []) or []

        def judge_top2_correct(idx: int) -> bool:
            if idx >= len(council):
                return False
            picked = council[idx].get("picked_grids")
            if not picked:
                return False
            return any(grid == correct for grid in picked[:2])

        j0 = judge_top2_correct(0)
        j1 = judge_top2_correct(1)
        j2 = judge_top2_correct(2)

        totals["total"] += 1
        if council_top2_correct:
            totals["council_top2"] += 1
        if j0:
            totals["judge0_top2"] += 1
        if j1:
            totals["judge1_top2"] += 1
        if j2:
            totals["judge2_top2"] += 1

        rows.append(
            {
                "task": task_id,
                "test": test_id,
                "council_top2_correct": council_top2_correct,
                "judge0_top2_correct": j0,
                "judge1_top2_correct": j1,
                "judge2_top2_correct": j2,
            }
        )

    rows.sort(key=lambda r: (r["task"], r["test"]))

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Task",
                "Test",
                "CouncilTop2Correct",
                "Judge0Top2Correct",
                "Judge1Top2Correct",
                "Judge2Top2Correct",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    r["task"],
                    r["test"],
                    "TRUE" if r["council_top2_correct"] else "FALSE",
                    "TRUE" if r["judge0_top2_correct"] else "FALSE",
                    "TRUE" if r["judge1_top2_correct"] else "FALSE",
                    "TRUE" if r["judge2_top2_correct"] else "FALSE",
                ]
            )

    def rate(n: int, d: int) -> str:
        if d == 0:
            return "0.0%"
        return f"{(n / d) * 100:.1f}%"

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Judge Performance Summary\n\n")
        f.write(f"- Total tasks evaluated: {totals['total']}\n")
        f.write(f"- Council (3-judge) Top2 correct: {totals['council_top2']} ({rate(totals['council_top2'], totals['total'])})\n")
        f.write(f"- Judge 0 Top2 correct: {totals['judge0_top2']} ({rate(totals['judge0_top2'], totals['total'])})\n")
        f.write(f"- Judge 1 Top2 correct: {totals['judge1_top2']} ({rate(totals['judge1_top2'], totals['total'])})\n")
        f.write(f"- Judge 2 Top2 correct: {totals['judge2_top2']} ({rate(totals['judge2_top2'], totals['total'])})\n")

    return csv_path, summary_path


def classify_cost_category(raw_name: str) -> str:
    lowered = (raw_name or "").lower()
    if "image" in lowered:
        return "Image"
    if "deep" in lowered or "thinking" in lowered:
        return "Text"
    if "codegen" in lowered or "code" in lowered or "tool" in lowered or "tools" in lowered:
        return "Code"
    return "Text"


def compute_cost_breakdown(logs_dir: str) -> tuple[dict[tuple[str, int], dict[str, float]], list[tuple[str, int]]]:
    pattern = re.compile(r'.*([a-f0-9]{8})_(\d+)_step_([a-zA-Z0-9]+)\.json$')
    task_costs: dict[tuple[str, int], dict[str, float]] = {}
    task_keys = set()

    answers = load_answers(os.getcwd())

    for filename in os.listdir(logs_dir):
        match = pattern.match(filename)
        if not match:
            continue

        task_id = match.group(1)
        test_id_str = match.group(2)
        step_name = match.group(3)
        test_id = int(test_id_str)
        task_key = (task_id, test_id)
        task_keys.add(task_key)

        costs = task_costs.setdefault(
            task_key,
            {
                "candidate_total": 0.0,
                "candidate_text": 0.0,
                "candidate_image": 0.0,
                "candidate_code": 0.0,
                "judging_total": 0.0,
            },
        )

        filepath = os.path.join(logs_dir, filename)

        if step_name == "finish":
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue

            sel = data.get("selection_details", {}) or {}
            judges = sel.get("judges", {}) or {}
            judge_cost = 0.0

            if isinstance(judges, dict):
                for judge_data in judges.values():
                    if isinstance(judge_data, dict):
                        judge_cost += float(judge_data.get("total_cost", 0) or 0)
                    elif isinstance(judge_data, list):
                        for run in judge_data:
                            if isinstance(run, dict):
                                judge_cost += float(run.get("total_cost", 0) or 0)

            costs["judging_total"] += judge_cost
            continue

        if step_name in ("2", "4"):
            continue

        result = parse_log_file(filepath, task_id, test_id_str, step_name, answers)
        if not result:
            continue

        calls = []
        res_type = result.get("type")
        data = result.get("data", {})
        if res_type == "generic":
            calls = data.get("calls", [])
        elif res_type == "nested":
            for sub_calls in data.get("steps", {}).values():
                calls.extend(sub_calls)
        elif res_type == "finish":
            calls = []

        for call in calls:
            cost = call.get("cost")
            if not isinstance(cost, (int, float)):
                continue
            if cost <= 0:
                continue

            name = call.get("run_id") or call.get("name") or ""
            category = classify_cost_category(name)

            costs["candidate_total"] += float(cost)
            if category == "Text":
                costs["candidate_text"] += float(cost)
            elif category == "Image":
                costs["candidate_image"] += float(cost)
            elif category == "Code":
                costs["candidate_code"] += float(cost)

    return task_costs, sorted(task_keys, key=lambda x: (x[0], x[1]))


def write_cost_breakdown_md(output_dir: str, task_costs: dict[tuple[str, int], dict[str, float]], task_keys: list[tuple[str, int]]) -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cost_breakdown.md")

    total_tasks = len(task_keys)
    totals = {
        "candidate_total": 0.0,
        "candidate_text": 0.0,
        "candidate_image": 0.0,
        "candidate_code": 0.0,
        "judging_total": 0.0,
    }

    for key in task_keys:
        costs = task_costs.get(key, {})
        for k in totals:
            totals[k] += float(costs.get(k, 0.0) or 0.0)

    def avg(value: float) -> float:
        if total_tasks == 0:
            return 0.0
        return value / total_tasks

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Cost Breakdown\n\n")
        f.write(f"- Task:Test count: {total_tasks}\n\n")
        f.write("## Phase Breakdown (Average $/Task)\n\n")
        f.write("_Note: \"per task\" here means per Task:Test pair._\n\n")
        f.write("| Phase | Total ($) | Avg per Task ($) |\n")
        f.write("| --- | --- | --- |\n")
        candidate_total = totals["candidate_total"]
        judging_total = totals["judging_total"]
        total_all = candidate_total + judging_total
        f.write(f"| Candidate generation | {candidate_total:.4f} | {avg(candidate_total):.4f} |\n")
        f.write(f"| Judging | {judging_total:.4f} | {avg(judging_total):.4f} |\n")
        f.write(f"| **Total** | {total_all:.4f} | {avg(total_all):.4f} |\n")

        f.write("\n## Candidate Generation Breakdown (Average $/Task)\n\n")
        f.write("| Category | Total ($) | Avg per Task ($) |\n")
        f.write("| --- | --- | --- |\n")
        f.write(f"| Text | {totals['candidate_text']:.4f} | {avg(totals['candidate_text']):.4f} |\n")
        f.write(f"| Image | {totals['candidate_image']:.4f} | {avg(totals['candidate_image']):.4f} |\n")
        f.write(f"| Code | {totals['candidate_code']:.4f} | {avg(totals['candidate_code']):.4f} |\n")

        f.write("\nNotes:\n")
        f.write("- Candidate generation costs are summed across all non-finish steps (steps 1/3/5), excluding steps 2 and 4.\n")
        f.write("- Judging costs are summed from `selection_details.judges` in the finish logs (including council runs).\n")
        f.write("- Deep/Thinking variants are included in **Text**.\n")

    return output_path


def compute_gpt52_api_errors(logs_dir: str) -> tuple[int, int, int, dict[str, int]]:
    pattern = re.compile(r'.*([a-f0-9]{8})_(\d+)_step_([a-zA-Z0-9]+)\.json$')
    answers = load_answers(os.getcwd())

    total = 0
    failed = 0
    success = 0
    by_error: dict[str, int] = {}

    error_counts = {
        "max_token": 0,
        "timeout": 0,
        "server": 0,
        "error_403": 0,
        "rate_limit": 0,
        "network": 0,
        "connection": 0,
        "content_filter": 0,
        "other": 0,
    }

    for filename in os.listdir(logs_dir):
        match = pattern.match(filename)
        if not match:
            continue

        step_name = match.group(3)
        if step_name == "finish":
            continue

        filepath = os.path.join(logs_dir, filename)
        task_id = match.group(1)
        test_id_str = match.group(2)

        result = parse_log_file(filepath, task_id, test_id_str, step_name, answers)
        if not result:
            continue

        calls = []
        res_type = result.get("type")
        data = result.get("data", {})
        if res_type == "generic":
            calls = data.get("calls", [])
        elif res_type == "nested":
            for sub_calls in data.get("steps", {}).values():
                calls.extend(sub_calls)

        for call in calls:
            timing = call.get("timing_breakdown")
            if not isinstance(timing, list):
                continue
            for item in timing:
                if not isinstance(item, dict):
                    continue
                model = (item.get("model") or "").lower()
                if "gpt-5.2" not in model:
                    continue
                total += 1
                status = (item.get("status") or "").lower()
                if status == "success":
                    success += 1
                else:
                    failed += 1
                    err = item.get("error") or "Unknown"
                    by_error[err] = by_error.get(err, 0) + 1

                    msg = (err or "").lower()
                    is_max_token = "max_output_tokens" in msg
                    is_timeout = "timed out after 3600s" in msg or "timed out. falling back" in msg or "timeout after 3600s" in msg
                    is_server_error = "server_error" in msg
                    is_403 = "error code: 403" in msg
                    is_429 = "error code: 429" in msg or "rate_limit_exceeded" in msg or "resource_exhausted" in msg
                    is_network = "network/protocol error" in msg or "503 unavailable" in msg
                    is_connection = "connection error" in msg
                    is_content_filter = "content filtering policy" in msg or "output blocked" in msg

                    if is_max_token:
                        error_counts["max_token"] += 1
                    elif is_timeout:
                        error_counts["timeout"] += 1
                    elif is_server_error:
                        error_counts["server"] += 1
                    elif is_403:
                        error_counts["error_403"] += 1
                    elif is_429:
                        error_counts["rate_limit"] += 1
                    elif is_network:
                        error_counts["network"] += 1
                    elif is_connection:
                        error_counts["connection"] += 1
                    elif is_content_filter:
                        error_counts["content_filter"] += 1
                    else:
                        error_counts["other"] += 1

    return total, success, failed, by_error, error_counts


def write_gpt52_api_errors_md(
    output_dir: str,
    total: int,
    success: int,
    failed: int,
    by_error: dict[str, int],
    error_counts: dict[str, int],
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "gpt52_api_errors.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# GPT-5.2 API Errors\n\n")
        f.write("- Dataset: `timing_breakdown` entries in non-finish steps (1/3/5) with model matching `gpt-5.2`.\n")
        f.write("- Each timing_breakdown entry represents a single request attempt (including retries).\n\n")
        f.write("| Metric | Count |\n")
        f.write("| --- | --- |\n")
        f.write(f"| Total attempts | {total} |\n")
        f.write(f"| Success | {success} |\n")
        f.write(f"| Failed | {failed} |\n\n")

        f.write("## By Error Class (logs_parser classification)\n\n")
        f.write("| Class | Count |\n")
        f.write("| --- | --- |\n")
        f.write(f"| Max token | {error_counts.get('max_token', 0)} |\n")
        f.write(f"| Timeout | {error_counts.get('timeout', 0)} |\n")
        f.write(f"| Server error | {error_counts.get('server', 0)} |\n")
        f.write(f"| 403 | {error_counts.get('error_403', 0)} |\n")
        f.write(f"| Rate limit | {error_counts.get('rate_limit', 0)} |\n")
        f.write(f"| Network | {error_counts.get('network', 0)} |\n")
        f.write(f"| Connection | {error_counts.get('connection', 0)} |\n")
        f.write(f"| Content filter | {error_counts.get('content_filter', 0)} |\n")
        f.write(f"| Other | {error_counts.get('other', 0)} |\n\n")

        # Raw error table removed by request

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract paper data from logs.")
    parser.add_argument("directory", help="Path to the logs directory")
    args = parser.parse_args()

    pairs, method_keys, method_labels, statuses, overall_status = scan_logs(args.directory)
    output_dir = os.path.join(os.path.dirname(__file__), "paper_data")
    csv_path = write_methodology_matrix_csv(output_dir, pairs, method_keys, method_labels, statuses, overall_status)
    md_path = write_methodology_matrix_md(output_dir, pairs, method_keys, method_labels, statuses, overall_status)
    image_path = write_methodology_matrix_image(output_dir, csv_path)
    counts, matrix_lists, total_pairs = compute_many_candidates_matrix(
        pairs,
        statuses,
        method_labels,
        threshold=29,
    )
    only_counts, only_lists = compute_only_category_counts(
        pairs,
        statuses,
        method_labels,
        threshold=29,
    )
    only_model_modality_counts, only_model_modality_lists = compute_only_model_modality_counts(
        pairs,
        statuses,
        threshold=29,
    )
    summary_path = write_many_candidates_matrix(
        output_dir,
        counts,
        total_pairs,
        threshold=29,
        only_counts=only_counts,
        matrix_lists=matrix_lists,
        only_lists=only_lists,
        only_model_modality_counts=only_model_modality_counts,
        only_model_modality_lists=only_model_modality_lists,
    )
    task_costs, task_keys = compute_cost_breakdown(args.directory)
    cost_path = write_cost_breakdown_md(output_dir, task_costs, task_keys)
    gpt_total, gpt_success, gpt_failed, gpt_by_error, gpt_error_counts = compute_gpt52_api_errors(args.directory)
    gpt_path = write_gpt52_api_errors_md(
        output_dir,
        gpt_total,
        gpt_success,
        gpt_failed,
        gpt_by_error,
        gpt_error_counts,
    )
    print(f"Wrote methodology matrix with {len(method_keys)} methods to {csv_path}")
    print(f"Wrote methodology matrix with {len(method_keys)} methods to {md_path}")
    print(f"Wrote methodology matrix image to {image_path}")
    print(f"Wrote many-candidates matrix to {summary_path}")
    print(f"Wrote cost breakdown to {cost_path}")
    print(f"Wrote GPT-5.2 API error summary to {gpt_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
