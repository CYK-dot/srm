#!/usr/bin/env python3
"""
Recursively scan for 'srm_module.json' files and merge them into 'srm_project.json'.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.scripts.srm_log import Logger

PROG_NAME = "srm-module-collect"

def _srm_self_dir() -> Optional[Path]:
    """Return the SRM root directory (parent of src/scripts/), or None."""
    try:
        # __file__ = .../srm/src/scripts/srm_module_collect.py
        # srm root = parent of src/
        return Path(__file__).resolve().parent.parent.parent
    except Exception:
        return None

def find_module_files(root_dir: Path) -> List[Path]:
    srm_dir = _srm_self_dir()

    # Only exclude SRM's own directory when the scan root is OUTSIDE it.
    # When root_dir is inside srm_dir (e.g. running tests), don't exclude.
    exclude_srm = False
    if srm_dir is not None:
        try:
            root_dir.resolve().relative_to(srm_dir)
        except ValueError:
            # root_dir is outside srm_dir → submodule scenario → exclude
            exclude_srm = True

    results: List[Path] = []
    for p in root_dir.rglob("srm_module.json"):
        if exclude_srm:
            try:
                p.resolve().relative_to(srm_dir)
                continue  # inside SRM dir — skip
            except ValueError:
                pass
        results.append(p)
    return results

def load_and_validate_module(file_path: Path) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse error: {file_path} - {e}")
    except Exception as e:
        raise IOError(f"failed to read file: {file_path} - {e}")

    if "module" not in data:
        raise ValueError(f"missing top-level 'module' key: {file_path}")
    if "name" not in data["module"]:
        raise ValueError(f"module missing 'name' field: {file_path}")

    data.setdefault("local_storages", [])
    data.setdefault("external_storages", [])
    data.setdefault("items", [])

    data["_file_path"] = str(file_path.resolve())
    return data

def check_duplicate_modules(modules: List[Dict[str, Any]]) -> None:
    name_map = {}
    for mod in modules:
        mod_name = mod["module"]["name"]
        if mod_name in name_map:
            existing_path = name_map[mod_name]
            raise ValueError(
                f"duplicate module name '{mod_name}':\n"
                f"  first seen at: {existing_path}\n"
                f"  also at: {mod['_file_path']}"
            )
        name_map[mod_name] = mod["_file_path"]

def generate_project_json(root_dir: Path, modules: List[Dict[str, Any]], output_path: Path, logger: Logger) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    project_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "root_directory": str(root_dir.resolve()),
            "module_count": len(modules),
        },
        "modules": modules,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)
    logger.ok(f"generated: {output_path.resolve()}")

def main():
    parser = argparse.ArgumentParser(
        description="Recursively collect all srm_module.json and merge into srm_project.json"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        default="srm_project.json",
        help="output file name (default: srm_project.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show detailed processing information",
    )
    args = parser.parse_args()

    logger = Logger(PROG_NAME)

    root_path = Path(args.root_dir).resolve()
    if not root_path.is_dir():
        logger.error(f"'{root_path}' is not a valid directory")
        sys.exit(1)

    module_files = find_module_files(root_path)
    if args.verbose:
        logger.verbose(f"found {len(module_files)} srm_module.json files under {root_path}")

    modules = []
    for file_path in module_files:
        if args.verbose:
            rel = file_path.relative_to(root_path)
            logger.verbose(f"loading: {rel}")
        try:
            mod_data = load_and_validate_module(file_path)
            modules.append(mod_data)
        except (ValueError, IOError) as e:
            logger.error(f"skipping invalid file: {file_path}\n    reason: {e}")
            continue

    if not module_files:
        # No files found at all — warn but succeed (empty project)
        logger.warn("no srm_module.json files found")
    elif not modules:
        # Files existed but all were invalid — error
        logger.error("no valid modules to merge")
        sys.exit(1)

    if modules:
        try:
            check_duplicate_modules(modules)
        except ValueError as e:
            logger.error(f"module name conflict: {e}")
            sys.exit(1)

    output_path = Path(args.output)
    generate_project_json(root_path, modules, output_path, logger)

    if args.verbose:
        logger.verbose(f"merged {len(modules)} modules")

if __name__ == "__main__":
    main()