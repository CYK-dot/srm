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
    cmd = [sys.executable, script_name] + args
    print(f"[SRM] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"[SRM] ERROR: {script_name} failed with code {result.returncode}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="SRM cross-platform build")
    parser.add_argument("--root", default=".", help="SRM root directory (contains srm_types.json and modules)")
    parser.add_argument("--output-dir", default="build/srm", help="Output directory for generated files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 定义各步骤输出文件
    collected_json = output_dir / "collected.json"
    merged_json    = output_dir / "merged.json"
    out_base       = output_dir / "srm_layout"  # 无扩展名

    # 1. 验证组件
    run_script("srm_module_verify.py", ["--schema", str(root / "srm_module.schema.json")], cwd=root)

    # 2. 收集所有模块
    run_script("srm_module_collect.py", ["-o", str(collected_json)], cwd=root)

    # 3. 校验项目（全局唯一性等）
    run_script("srm_project_verify.py", [str(collected_json)], cwd=root)

    # 4. 合并为平坦结构
    run_script("srm_project_merge.py", [str(collected_json), "-o", str(merged_json)], cwd=root)

    # 5. 验证存储区容量
    run_script("srm_layout_verify.py", ["--resolved", str(merged_json), "--types", str(root / "srm_types.json")], cwd=root)

    # 6. 生成 C 代码
    run_script("srm_layout_generate.py", [
        "--resolved", str(merged_json),
        "--types", str(root / "srm_types.json"),
        "--output", str(out_base)
    ], cwd=root)

    print(f"[SRM] Build completed. Generated files in {output_dir}")

if __name__ == "__main__":
    main()