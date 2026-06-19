"""
F3 - 全局名称唯一性校验测试
"""
import pytest
import tempfile
from pathlib import Path
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF3GlobalUniqueness:
    """F3 - 全局名称唯一性校验测试类"""
    
    def test_f3_01_all_unique(self):
        """TC-F3-01: 全局唯一性通过"""
        project_dir = get_testcase_project("PYTHON-TC-F3-01")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            assert "all validation checks passed" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f3_02_duplicate_item_names(self):
        """TC-F3-02: items.name 跨模块冲突"""
        project_dir = get_testcase_project("PYTHON-TC-F3-02")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "duplicate" in stdout.lower() or "duplicate" in stderr.lower()
            assert "item" in stdout.lower() or "item" in stderr.lower()
    
    def test_f3_03_duplicate_storage_names(self):
        """TC-F3-03: local_storages.name 跨模块冲突"""
        project_dir = get_testcase_project("PYTHON-TC-F3-03")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "duplicate" in stdout.lower() or "duplicate" in stderr.lower()
            assert "storage" in stdout.lower() or "storage" in stderr.lower()
    
    def test_f3_04_both_duplicates(self):
        """TC-F3-04: storage 和 item 名均有冲突"""
        project_dir = get_testcase_project("PYTHON-TC-F3-04")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "duplicate" in stdout.lower() or "duplicate" in stderr.lower()
