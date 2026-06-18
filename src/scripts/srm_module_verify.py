#!/usr/bin/env python3
"""
Recursively validate all srm_module.json files against JSON Schema.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("\033[31m[srm-module-verify] error: jsonschema library not installed. Run: pip install jsonschema\033[0m", file=sys.stderr)
    sys.exit(1)

from src.scripts.srm_log import Logger

PROG_NAME = "srm-module-verify"

def load_schema(schema_path: Path, logger: Logger) -> dict:
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"cannot load schema file {schema_path}: {e}")
        sys.exit(1)

def find_module_files(root_dir: Path) -> List[Path]:
    return list(root_dir.rglob("srm_module.json"))

def validate_json_syntax(file_path: Path) -> Tuple[Optional[dict], Optional[str]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        error_msg = f"{e.lineno}:{e.colno}: JSON parse error - {e.msg}"
        return None, error_msg
    except Exception as e:
        return None, f"failed to read file: {e}"

def validate_against_schema(data: dict, file_path: Path, validator: Draft7Validator) -> List[str]:
    errors = []
    for error in validator.iter_errors(data):
        path_parts = []
        for part in error.absolute_path:
            if isinstance(part, int):
                path_parts.append(f"[{part}]")
            else:
                path_parts.append(f"/{part}")
        json_path = "".join(path_parts) if path_parts else "root"
        errors.append(f"{file_path}: field {json_path} -> {error.message}")
    return errors

def main():
    parser = argparse.ArgumentParser(
        description="Recursively validate all srm_module.json against a schema"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="root directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--schema",
        default="srm_module.schema.json",
        help="path to JSON Schema file (default: srm_module.schema.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show detailed validation results for valid files",
    )
    args = parser.parse_args()

    logger = Logger(PROG_NAME)

    root_path = Path(args.root_dir).resolve()
    if not root_path.is_dir():
        logger.error(f"'{root_path}' is not a valid directory")
        sys.exit(1)

    schema_path = Path(args.schema)
    if not schema_path.is_file():
        logger.error(f"schema file '{schema_path}' does not exist")
        sys.exit(1)

    schema = load_schema(schema_path, logger)
    validator = Draft7Validator(schema)

    module_files = find_module_files(root_path)
    if not module_files:
        logger.warn(f"no srm_module.json files found under {root_path}")
        sys.exit(0)

    logger.info(f"found {len(module_files)} module file(s), starting validation...")
    has_error = False

    for file_path in module_files:
        data, syntax_err = validate_json_syntax(file_path)
        if syntax_err:
            logger.error(f"{file_path}:{syntax_err}")
            has_error = True
            continue

        schema_errors = validate_against_schema(data, file_path, validator)
        if schema_errors:
            for err in schema_errors:
                logger.error(err)
            has_error = True
        elif args.verbose:
            logger.ok(f"valid: {file_path}")

    if has_error:
        logger.error("some module files failed validation, please fix them")
        sys.exit(1)
    else:
        logger.ok("all module files are valid")
        sys.exit(0)

if __name__ == "__main__":
    main()