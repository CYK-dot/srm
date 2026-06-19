"""
F5 - 项目合并为扁平结构测试
"""
import pytest
import tempfile
import os
import json
from pathlib import Path
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF5ProjectMerge:
    """F5 - 项目合并为扁平结构测试类"""
    
    def test_f5_01_single_module(self):
        """TC-F5-01: 单模块合并"""
        project_dir = get_testcase_project("PYTHON-TC-F5-01")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            
            # 检查生成的 merged.json
            merged_file = output_dir / "merged.json"
            assert merged_file.exists()
            
            with open(merged_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "storages" in data
            assert "items" in data
            assert len(data["storages"]) == 1
            assert len(data["items"]) == 1
    
    def test_f5_02_storage_only_no_items(self):
        """TC-F5-02: 模块仅含 storage 无 items"""
        project_dir = get_testcase_project("PYTHON-TC-F5-02")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            # 由于 items 为空，srm_layout_generate.py 会报错
            assert returncode == 1
            assert "no valid items found" in stdout.lower() or "no valid items found" in stderr.lower()
    
    def test_f5_03_multiple_modules(self):
        """TC-F5-03: 多模块合并"""
        project_dir = get_testcase_project("PYTHON-TC-F5-03")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            
            # 检查生成的 merged.json
            merged_file = output_dir / "merged.json"
            assert merged_file.exists()
            
            with open(merged_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "storages" in data
            assert "items" in data
            assert len(data["storages"]) == 2
            assert len(data["items"]) == 2
    
    def test_f5_04_invalid_storage_reference(self):
        """TC-F5-04: item 引用不存在 storage（防御性）"""
        project_dir = get_testcase_project("PYTHON-TC-F5-04")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "not defined" in stdout.lower() or "not defined" in stderr.lower()
