#!/usr/bin/env python3
"""
Generate C header/source files from resolved.json and types.json.
Generates:
1. Compile-time macros for Storage/Item IDs and sizes/types.
2. A runtime function srm_get_offset(storage_id, item_id) using nested switch.
Supports alignment per data type.
"""
import argparse
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from jinja2 import Template
except ImportError:
    print("[srm-layout-generate] error: jinja2 not installed. Run: pip install jinja2", file=sys.stderr)
    sys.exit(1)

from src.scripts.srm_log import Logger

PROG_NAME = "srm-layout-generate"

def to_c_identifier(name: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    if s and s[0].isdigit():
        s = '_' + s
    return s.upper()

def load_json(path: Path, logger: Logger, desc: str) -> dict:
    if not path.is_file():
        logger.error(f"{desc} file not found: {path}")
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"invalid JSON in {path}: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"cannot read {path}: {e}")
        sys.exit(1)

def compute_item_length(item: dict, type_map: dict, logger: Logger) -> Optional[int]:
    name = item.get("name")
    data_type = item.get("data_type")
    if not data_type:
        logger.error(f"item '{name}': missing 'data_type'")
        return None

    if data_type not in type_map:
        logger.error(f"item '{name}': unknown data_type '{data_type}'")
        return None

    type_def = type_map[data_type]

    if "length" in type_def:
        length = type_def["length"]
        if isinstance(length, int):
            return length
        logger.error(f"type '{data_type}': 'length' must be integer")
        return None

    if "length_strip" in type_def:
        expr = type_def["length_strip"]
        if not expr.startswith("${") or not expr.endswith("}"):
            logger.error(f"type '{data_type}': unsupported length_strip expression '{expr}'")
            return None
        field_name = expr[2:-1]
        if field_name not in item:
            logger.error(f"item '{name}': missing field '{field_name}' for length_strip")
            return None
        value = item[field_name]
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        logger.error(f"item '{name}': field '{field_name}' must be string")
        return None

    logger.error(f"type '{data_type}': missing 'length' or 'length_strip'")
    return None

def build_item_info(items: List[dict], type_to_code: dict, type_map: dict, logger: Logger) -> List[dict]:
    info_list = []
    for idx, item in enumerate(items):
        name = item.get("name")
        if not name:
            continue
        data_type = item.get("data_type")
        length = compute_item_length(item, type_map, logger)
        if length is None:
            logger.error(f"skip item '{name}' due to length error")
            continue

        type_num = type_to_code.get(data_type, 0)
        info = {
            "id": idx,
            "name": name,
            "c_name": to_c_identifier(name),
            "data_type": data_type,
            "type_num": type_num,
            "length": length,
            "storages": item.get("storages", []),
        }
        info_list.append(info)
    return info_list

def build_layout_entries(storages: dict, items: List[dict], type_map: dict) -> List[dict]:
    """
    构建每个 (Storage, Item) 组合的偏移条目，考虑对齐。
    """
    storage_names = sorted(storages.keys())
    storage_id_map = {name: idx for idx, name in enumerate(storage_names)}
    entries = []

    for s_name in storage_names:
        s_id = storage_id_map[s_name]
        offset = 0
        for item in items:
            if s_name not in item["storages"]:
                continue
            # 获取对齐要求
            data_type = item["data_type"]
            alignment = type_map.get(data_type, {}).get("alignment", 1)
            if alignment > 1:
                offset = ((offset + alignment - 1) // alignment) * alignment
            entries.append({
                "storage_id": s_id,
                "storage_name": s_name,
                "storage_c_name": to_c_identifier(s_name),
                "item_id": item["id"],
                "item_name": item["name"],
                "item_c_name": item["c_name"],
                "offset": offset,
                "length": item["length"],
                "type_num": item["type_num"],
            })
            offset += item["length"]
    return entries

def main():
    parser = argparse.ArgumentParser(description="Generate C code from resolved SRM data")
    parser.add_argument("--resolved", default="srm_resolved.json", help="resolved JSON file")
    parser.add_argument("--types", default="srm_types.json", help="type definition file")
    parser.add_argument("--output", "-o", default="srm_layout", help="output base name (without extension)")
    parser.add_argument("--template", default="srm_layout_generate.jinja2", help="Jinja2 template file")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logger = Logger(PROG_NAME)

    types_data = load_json(Path(args.types), logger, "Types")
    if "types" not in types_data:
        logger.error("srm_types.json missing 'types' array")
        sys.exit(1)

    type_map = {}
    type_to_code = {}
    for idx, entry in enumerate(types_data["types"], start=1):
        t_name = entry.get("name")
        if t_name:
            type_map[t_name] = entry
            type_to_code[t_name] = idx

    resolved = load_json(Path(args.resolved), logger, "Resolved")
    if "storages" not in resolved or "items" not in resolved:
        logger.error("resolved file must contain 'storages' and 'items' keys")
        sys.exit(1)

    storages = resolved["storages"]
    items_data = resolved["items"]

    if args.verbose:
        logger.info(f"loaded {len(storages)} storages, {len(items_data)} items")

    # 1. 构建 Item 详细信息（分配 ID 并计算长度）
    item_info_list = build_item_info(items_data, type_to_code, type_map, logger)
    if not item_info_list:
        logger.error("no valid items found")
        sys.exit(1)

    # 2. 构建存储区列表（分配 ID）
    storage_names = sorted(storages.keys())
    storage_list = []
    for idx, name in enumerate(storage_names):
        storage_list.append({
            "id": idx,
            "name": name,
            "c_name": to_c_identifier(name),
            "size": storages[name].get("size", 0)
        })

    # 3. 构建布局条目（每个 Storage+Item 组合，考虑对齐）
    layout_entries = build_layout_entries(storages, item_info_list, type_map)

    # 4. 类型枚举
    type_enums = []
    for t_name, code in type_to_code.items():
        type_enums.append({
            "c_name": to_c_identifier(t_name),
            "code": code
        })

    context = {
        "storages": storage_list,
        "items": item_info_list,
        "layout_entries": layout_entries,
        "type_enums": type_enums,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 5. 渲染模板
    template_path = Path(args.template)
    if not template_path.is_file():
        logger.error(f"template file not found: {template_path}")
        sys.exit(1)
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    template = Template(template_content)

    output_base = Path(args.output)
    for ext, out_path in [(".h", output_base.with_suffix(".h")), (".c", output_base.with_suffix(".c"))]:
        ctx = context.copy()
        ctx["output_file"] = ext[1:]
        rendered = template.render(ctx)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rendered)
        logger.ok(f"generated {out_path}")

if __name__ == "__main__":
    main()