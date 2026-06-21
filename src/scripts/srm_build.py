#!/usr/bin/env python3
"""
SRM 跨平台构建脚本
Usage: python srm_build.py --root /path/to/project --output-dir /path/to/build
"""
import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name, args, cwd, logger=None):
    """运行单个 Python 脚本并检查返回值"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name
    
    # 确保cwd是有效的目录
    cwd = Path(cwd)
    if not cwd.is_dir():
        print(f"[SRM] ERROR: Working directory does not exist: {cwd}")
        sys.exit(1)
    
    # 设置PYTHONPATH环境变量，确保模块导入正常
    # 项目根目录是脚本目录的父目录的父目录
    project_root = script_dir.parent.parent
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root) + os.pathsep + env.get("PYTHONPATH", "")
    
    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, cwd=str(cwd), env=env)
    if result.returncode != 0:
        print(f"[SRM] ERROR: {script_name} failed with code {result.returncode}")
        sys.exit(result.returncode)

def _write_empty_layout(out_base: Path) -> None:
    """Generate minimal empty srm_layout.h and srm_layout.c when no modules exist."""
    out_base.parent.mkdir(parents=True, exist_ok=True)
    h_path = out_base.with_suffix(".h")
    c_path = out_base.with_suffix(".c")

    h_content = """\
/*
 * srm_layout.h - Auto-generated SRM layout header (empty project)
 */
#ifndef SRM_LAYOUT_H
#define SRM_LAYOUT_H

#include <stdint.h>

/* No modules defined — this is a placeholder file. */

#endif /* SRM_LAYOUT_H */
"""
    c_content = """\
/*
 * srm_layout.c - Auto-generated SRM layout implementation (empty project)
 */
#include "srm.h"
#include "srm_layout.h"
#include <stddef.h>

/* No modules defined — stub implementations. */

uint16_t srm_get_offset(uint16_t storage_id, uint16_t item_id)
{
    (void)storage_id; (void)item_id;
    return 0xFFFF;
}

uint16_t srm_get_storage_size(uint16_t storage_id)
{
    (void)storage_id;
    return 0;
}

uint16_t srm_get_item_size(uint16_t item_id)
{
    (void)item_id;
    return 0;
}
"""
    with open(h_path, "w", encoding="utf-8") as f:
        f.write(h_content)
    with open(c_path, "w", encoding="utf-8") as f:
        f.write(c_content)
    print(f"[SRM] Generated empty layout: {h_path}, {c_path}")

def _has_modules(collected_json: Path) -> bool:
    """Return True if collected.json contains at least one module."""
    import json
    try:
        with open(collected_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("modules"))
    except Exception:
        return False

def _validate_merged_json(merged_json: Path, schema_path: Path) -> None:
    """Validate srm_merged.json against srm_merged.schema.json."""
    import json
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        print("[SRM] WARNING: jsonschema not installed, skipping schema validation", file=sys.stderr)
        return

    try:
        with open(merged_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[SRM] ERROR: cannot read {merged_json}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception as e:
        print(f"[SRM] ERROR: cannot read schema {schema_path}: {e}", file=sys.stderr)
        sys.exit(1)

    validator = Draft7Validator(schema)
    errors = []
    for error in validator.iter_errors(data):
        path_parts = []
        for part in error.absolute_path:
            if isinstance(part, int):
                path_parts.append(f"[{part}]")
            else:
                path_parts.append(f"/{part}")
        json_path = "".join(path_parts) if path_parts else "root"
        errors.append(f"field {json_path} -> {error.message}")

    if errors:
        print(f"[SRM] ERROR: {merged_json} failed schema validation:", file=sys.stderr)
        for err in errors:
            print(f"    {err}", file=sys.stderr)
        sys.exit(1)

    print(f"[SRM] {merged_json.name} passed schema validation")

def main():
    parser = argparse.ArgumentParser(description="SRM cross-platform build")
    parser.add_argument("--root", default=".", help="SRM root directory (contains SRM modules)")
    parser.add_argument("--output-dir", default="build/srm", help="Output directory for generated files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取脚本所在目录
    script_dir = Path(__file__).parent

    # 定义各步骤输出文件
    collected_json = output_dir / "collected.json"
    merged_json    = output_dir / "srm_merged.json"
    out_base       = output_dir / "srm_layout"  # 无扩展名

    print()  # 空行分隔

    # 1. 验证组件
    run_script("srm_module_verify.py", ["--schema", str(script_dir / "srm_module.schema.json")], cwd=root)

    # 2. 收集所有模块
    run_script("srm_module_collect.py", ["-o", str(collected_json)], cwd=root)

    # 2b. 如果没有模块，生成空的输出文件并提前结束
    if not _has_modules(collected_json):
        print("[SRM] No modules found, skipping code generation")
        _write_empty_layout(out_base)
        print(f"[SRM] Build completed (no modules). Empty files in {output_dir}")
        return

    # 3. 校验项目（全局唯一性等）
    run_script("srm_project_verify.py", [str(collected_json)], cwd=root)

    # 4. 合并为平坦结构
    run_script("srm_project_merge.py", [str(collected_json), "-o", str(merged_json)], cwd=root)

    # 4b. 校验合并产物的 JSON Schema
    schema_path = script_dir / "srm_merged.schema.json"
    _validate_merged_json(merged_json, schema_path)

    # 5. 验证存储区容量 (types now come from resolved JSON)
    run_script("srm_layout_verify.py", ["--resolved", str(merged_json)], cwd=root)

    # 6. 生成 C 代码 (types now come from resolved JSON)
    run_script("srm_layout_generate.py", [
        "--resolved", str(merged_json),
        "--output", str(out_base),
        "--template", str(script_dir / "srm_layout_generate.jinja2")
    ], cwd=root)

    print(f"[SRM] Build completed. Generated files in {output_dir}")
    print()  # 空行分隔

if __name__ == "__main__":
    main()