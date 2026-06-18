#!/usr/bin/env python3
"""
Validate srm_project.json:
- Global uniqueness of local_storages.name and items.name
- External storage alias uniqueness and source_module existence
- Item storage references must be valid within the module
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

from src.scripts.srm_log import Logger

PROG_NAME = "srm-project-verify"

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

def validate_global_uniqueness(modules: List[Dict]) -> Tuple[bool, List[Tuple[str, List[str]]]]:
    errors = []
    storage_owners: Dict[str, str] = {}   # local storage name -> module name
    item_owners: Dict[str, str] = {}      # item name -> module name

    for mod in modules:
        mod_name = mod["module"]["name"]
        for storage in mod.get("local_storages", []):
            name = storage["name"]
            if name in storage_owners:
                errors.append((
                    "Duplicate local storage name globally",
                    [
                        f"Storage '{name}' is already defined in module '{storage_owners[name]}'",
                        f"Also defined in module '{mod_name}'"
                    ]
                ))
            else:
                storage_owners[name] = mod_name
        for item in mod.get("items", []):
            name = item["name"]
            if name in item_owners:
                errors.append((
                    "Duplicate item name globally",
                    [
                        f"Item '{name}' is already defined in module '{item_owners[name]}'",
                        f"Also defined in module '{mod_name}'"
                    ]
                ))
            else:
                item_owners[name] = mod_name

    return len(errors) == 0, errors

def validate_module_references(modules: List[Dict]) -> Tuple[bool, List[Tuple[str, List[str]]]]:
    errors = []
    mod_map: Dict[str, Dict] = {m["module"]["name"]: m for m in modules}

    for mod in modules:
        mod_name = mod["module"]["name"]
        local_names = {s["name"] for s in mod.get("local_storages", [])}
        ext_storages = mod.get("external_storages", [])
        ext_names = [e["name"] for e in ext_storages]

        # Duplicate external aliases within module
        if len(set(ext_names)) != len(ext_names):
            duplicates = [n for n in ext_names if ext_names.count(n) > 1]
            errors.append((
                "Duplicate external storage aliases within module",
                [f"Module '{mod_name}' has duplicate alias(es): {sorted(set(duplicates))}"]
            ))

        # External alias conflicts with local storage
        for alias in ext_names:
            if alias in local_names:
                errors.append((
                    "External storage alias conflicts with local storage",
                    [
                        f"Module '{mod_name}' defines external alias '{alias}'",
                        f"But a local storage with the same name exists in this module"
                    ]
                ))

        # Check each external reference
        for ext in ext_storages:
            alias = ext.get("name")
            target_mod = ext.get("source_module")
            if not alias or not target_mod:
                errors.append((
                    "Malformed external_storages entry",
                    [f"In module '{mod_name}': entry missing 'name' or 'source_module': {ext}"]
                ))
                continue
            if target_mod not in mod_map:
                errors.append((
                    "External storage target module not found",
                    [
                        f"Module '{mod_name}' references external alias '{alias}'",
                        f"Target module '{target_mod}' does not exist"
                    ]
                ))
                continue
            target = mod_map[target_mod]
            target_local_names = {s["name"] for s in target.get("local_storages", [])}
            if alias not in target_local_names:
                errors.append((
                    "External storage target missing",
                    [
                        f"Module '{mod_name}' references alias '{alias}' from module '{target_mod}'",
                        f"Module '{target_mod}' has no local storage named '{alias}'",
                        f"Available: {sorted(target_local_names)}"
                    ]
                ))

        # Item storage references
        all_storage_names = local_names.union(set(ext_names))
        for item in mod.get("items", []):
            item_name = item.get("name")
            storages = item.get("storages", [])
            if not storages:
                errors.append((
                    "Item has empty storages list",
                    [f"Module '{mod_name}', item '{item_name}' has empty 'storages'"]
                ))
            for storage_ref in storages:
                if storage_ref not in all_storage_names:
                    errors.append((
                        "Undefined storage reference",
                        [
                            f"Module '{mod_name}', item '{item_name}'",
                            f"References storage '{storage_ref}' which is not defined in this module",
                            f"Available: {sorted(all_storage_names)}"
                        ]
                    ))

    return len(errors) == 0, errors

def main():
    parser = argparse.ArgumentParser(
        description="Validate srm_project.json: global uniqueness and reference integrity"
    )
    parser.add_argument(
        "project_file",
        nargs="?",
        default="srm_project.json",
        help="path to srm_project.json (default: srm_project.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show detailed processing information",
    )
    args = parser.parse_args()

    logger = Logger(PROG_NAME)

    project_path = Path(args.project_file)
    if not project_path.is_file():
        logger.error(f"project file not found: {project_path}")
        sys.exit(1)

    project_data = load_project_json(project_path, logger)

    if "modules" not in project_data:
        logger.error("missing 'modules' top-level key")
        sys.exit(1)
    modules = project_data["modules"]
    if not isinstance(modules, list):
        logger.error("'modules' must be an array")
        sys.exit(1)

    if args.verbose:
        logger.info(f"loaded {len(modules)} modules from {project_path}")

    has_errors = False

    ok_unique, unique_errors = validate_global_uniqueness(modules)
    if not ok_unique:
        has_errors = True
        for title, lines in unique_errors:
            logger.error_multiline(title, lines)
    elif args.verbose:
        logger.info("global uniqueness check passed")

    ok_ref, ref_errors = validate_module_references(modules)
    if not ok_ref:
        has_errors = True
        for title, lines in ref_errors:
            logger.error_multiline(title, lines)
    elif args.verbose:
        logger.info("reference integrity check passed")

    if has_errors:
        logger.error("validation failed, please fix the issues above")
        sys.exit(1)
    else:
        logger.ok("all validation checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()