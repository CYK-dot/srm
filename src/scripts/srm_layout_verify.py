#!/usr/bin/env python3
"""
Verify srm_resolved.json: For each storage, ensure total length of all items
assigned to it does not exceed storage's size, considering alignment.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from src.scripts.srm_log import Logger

PROG_NAME = "srm-layout-verify"

def load_json(path: Path, logger: Logger, description: str) -> dict:
    if not path.is_file():
        logger.error(f"{description} file not found: {path}")
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

def get_item_length(item: dict, type_map: dict, logger: Logger) -> Optional[int]:
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

def simulate_insertion(
    items: list,
    storages: dict,
    item_lengths: Dict[str, int],
    type_map: dict,
    logger: Logger,
    verbose: bool,
) -> bool:
    """
    Simulate inserting items into storages with alignment.
    """
    usage: Dict[str, int] = {}
    storage_contents: Dict[str, List[str]] = {}
    all_ok = True

    for item in items:
        name = item.get("name")
        if not name or name not in item_lengths:
            continue

        length = item_lengths[name]
        data_type = item.get("data_type", "unknown")
        # Get alignment, default 1
        alignment = type_map.get(data_type, {}).get("alignment", 1)

        for storage_name in item.get("storages", []):
            if storage_name not in storages:
                logger.error(f"item '{name}' references unknown storage '{storage_name}'")
                all_ok = False
                continue

            storage = storages[storage_name]
            max_size = storage.get("size")
            if not isinstance(max_size, int):
                # No size limit
                if verbose:
                    logger.verbose(f"storage '{storage_name}' has no size limit, skipping capacity check")
                usage.setdefault(storage_name, 0)
                storage_contents.setdefault(storage_name, []).append(name)
                continue

            current_usage = usage.get(storage_name, 0)
            # Apply alignment
            if alignment > 1:
                aligned_offset = ((current_usage + alignment - 1) // alignment) * alignment
            else:
                aligned_offset = current_usage

            # Check overflow
            if aligned_offset + length <= max_size:
                usage[storage_name] = aligned_offset + length
                storage_contents.setdefault(storage_name, []).append(name)
            else:
                lines = [
                    f"storage '{storage_name}' size {max_size}, before insert uses {current_usage}",
                    f"item '{name}' requires alignment {alignment}, aligned offset {aligned_offset}, length {length}",
                    f"would exceed capacity"
                ]
                logger.error_multiline(
                    f"item '{name}' could not insert into storage '{storage_name}' due to overflow",
                    lines
                )
                all_ok = False

    if verbose and all_ok:
        logger.info("Final storage composition:")
        for storage_name in sorted(storage_contents.keys()):
            items_in = storage_contents[storage_name]
            total_usage = usage.get(storage_name, 0)
            max_size = storages.get(storage_name, {}).get("size", "unlimited")
            logger.verbose(f"  {storage_name}: {total_usage}/{max_size} bytes, items: {items_in}")
    elif verbose and not all_ok:
        logger.verbose("Skipping final storage composition due to insertion errors")

    return all_ok

def main():
    parser = argparse.ArgumentParser(
        description="Verify storage capacities by simulating item insertion with alignment."
    )
    parser.add_argument(
        "--types",
        default="srm_types.json",
        help="path to type definition file",
    )
    parser.add_argument(
        "--resolved",
        default="srm_resolved.json",
        help="path to resolved project JSON",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logger = Logger(PROG_NAME)

    types_data = load_json(Path(args.types), logger, "Types")
    if "types" not in types_data:
        logger.error("srm_types.json missing 'types' array")
        sys.exit(1)
    type_map = {entry["name"]: entry for entry in types_data["types"] if "name" in entry}

    resolved = load_json(Path(args.resolved), logger, "Resolved")
    if "storages" not in resolved or "items" not in resolved:
        logger.error("resolved file must contain 'storages' and 'items' keys")
        sys.exit(1)

    storages = resolved["storages"]
    items = resolved["items"]

    if args.verbose:
        logger.info(f"loaded {len(storages)} storages, {len(items)} items")

    # Compute length for each item
    item_lengths = {}
    invalid = []
    for item in items:
        name = item.get("name")
        if not name:
            logger.error("item without 'name' found, skipping")
            invalid.append("<unnamed>")
            continue
        length = get_item_length(item, type_map, logger)
        if length is None:
            invalid.append(name)
            continue
        item_lengths[name] = length

    if invalid:
        logger.error(f"failed to compute length for items: {invalid}")
        sys.exit(1)

    ok = simulate_insertion(items, storages, item_lengths, type_map, logger, args.verbose)

    if ok:
        logger.ok("all items successfully inserted into their storages")
        sys.exit(0)
    else:
        logger.error("verification failed")
        sys.exit(1)

if __name__ == "__main__":
    main()