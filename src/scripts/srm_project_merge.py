#!/usr/bin/env python3
"""
Resolve srm_project.json into a flat structure:
- storages: all local storages from all modules (keyed by name)
- items: all items from all modules (with storage references resolved)
Checks that every item.storages entry references an existing storage.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

from src.scripts.srm_log import Logger

PROG_NAME = "srm-project-merge"

def load_project_json(path: Path, logger: Logger) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"invalid JSON in {path}: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"cannot read {path}: {e}")
        sys.exit(1)

def resolve(modules: List[Dict], logger: Logger) -> Dict[str, Any]:
    storages: Dict[str, dict] = {}
    items: List[dict] = []
    types: Dict[str, dict] = {}

    # Build module map for extern_type resolution
    mod_map: Dict[str, Dict] = {m["module"]["name"]: m for m in modules}

    # Phase 1: Collect all local_storages and local_types first
    for mod in modules:
        mod_name = mod["module"]["name"]

        for storage in mod.get("local_storages", []):
            name = storage.get("name")
            if not name:
                logger.error(f"module '{mod_name}': local storage missing 'name'")
                sys.exit(1)
            if name in storages:
                logger.error(f"duplicate storage name '{name}' (from module '{mod_name}')")
                sys.exit(1)
            storages[name] = storage

        for type_def in mod.get("local_types", []):
            type_name = type_def.get("name")
            if not type_name:
                logger.error(f"module '{mod_name}': local type missing 'name'")
                sys.exit(1)
            if type_name in types:
                logger.error(
                    f"duplicate type name '{type_name}' (from module '{mod_name}')"
                )
                sys.exit(1)
            types[type_name] = type_def

    # Phase 2: Resolve extern_types (local_types are already all collected)
    for mod in modules:
        mod_name = mod["module"]["name"]

        for ext in mod.get("extern_types", []):
            ext_name = ext.get("name")
            source_mod = ext.get("source_module")
            if not ext_name or not source_mod:
                logger.error(
                    f"module '{mod_name}': extern_type missing 'name' or 'source_module'"
                )
                sys.exit(1)
            if ext_name in types:
                # Already defined as local_type in another module — skip
                continue
            if source_mod not in mod_map:
                logger.error(
                    f"module '{mod_name}': extern_type '{ext_name}' references "
                    f"unknown source_module '{source_mod}'"
                )
                sys.exit(1)
            source_types = {
                t["name"]: t
                for t in mod_map[source_mod].get("local_types", [])
                if "name" in t
            }
            if ext_name not in source_types:
                logger.error(
                    f"module '{mod_name}': extern_type '{ext_name}' not found "
                    f"in source_module '{source_mod}' local_types"
                )
                sys.exit(1)
            types[ext_name] = source_types[ext_name]

    # Phase 3: Collect items
    for mod in modules:
        mod_name = mod["module"]["name"]
        mod_file = mod.get("_file_path", ".")

        for item in mod.get("items", []):
            name = item.get("name")
            if not name:
                logger.error(f"module '{mod_name}': item missing 'name'")
                sys.exit(1)
            
            # 解析 file_value 相对路径为绝对路径
            if "file_value" in item:
                item_file_path = Path(mod_file).parent / item["file_value"]
                if not item_file_path.is_file():
                    logger.error(
                        f"module '{mod_name}', item '{name}': "
                        f"file_value path not found: {item_file_path}"
                    )
                    sys.exit(1)
                item["_file_value_resolved"] = str(item_file_path.resolve())
            
            items.append(item)

    # Phase 4: Validate item storage references
    for item in items:
        name = item.get("name")
        storage_refs = item.get("storages", [])
        if not storage_refs:
            logger.error(f"item '{name}' has empty or missing 'storages' list")
            sys.exit(1)
        for sname in storage_refs:
            if sname not in storages:
                logger.error(
                    f"item '{name}' references storage '{sname}' "
                    f"which is not defined in any module's local_storages"
                )
                sys.exit(1)

    return {"storages": storages, "items": items, "types": types}

def main():
    parser = argparse.ArgumentParser(
        description="Resolve srm_project.json into a flat storages+items structure."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="srm_project.json",
        help="input project JSON file (default: srm_project.json)",
    )
    parser.add_argument(
        "-o", "--output",
        default="srm_resolved.json",
        help="output file name (default: srm_resolved.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show detailed processing information",
    )
    args = parser.parse_args()

    logger = Logger(PROG_NAME)

    input_path = Path(args.input_file)
    if not input_path.is_file():
        logger.error(f"input file not found: {input_path}")
        sys.exit(1)

    project_data = load_project_json(input_path, logger)

    if "modules" not in project_data:
        logger.error("missing 'modules' top-level key")
        sys.exit(1)
    modules = project_data["modules"]
    if not isinstance(modules, list):
        logger.error("'modules' must be an array")
        sys.exit(1)

    if args.verbose:
        logger.info(f"loaded {len(modules)} modules from {input_path}")

    resolved = resolve(modules, logger)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resolved, f, indent=2, ensure_ascii=False)

    logger.ok(f"resolved {len(resolved['storages'])} storages and {len(resolved['items'])} items")
    if args.verbose:
        logger.verbose(f"output written to {output_path.resolve()}")

if __name__ == "__main__":
    main()