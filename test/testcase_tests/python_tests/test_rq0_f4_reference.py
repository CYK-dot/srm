"""
F4 - 引用完整性校验测试
"""
import pytest
import tempfile
from pathlib import Path
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF4ReferenceIntegrity:
    """F4 - 引用完整性校验测试类"""
    
    def test_f4_01_valid_reference(self):
        """TC-F4-01: 正常跨模块引用"""
        project_dir = get_testcase_project("RQ0_PYTHON_F4_01")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            assert "all validation checks passed" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f4_02_empty_storages_list(self):
        """TC-F4-02: item storages 为空列表"""
        project_dir = get_testcase_project("RQ0_PYTHON_F4_02")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "empty" in stdout.lower() or "empty" in stderr.lower()
    
    def test_f4_03_undefined_storage(self):
        """TC-F4-03: item 引用未定义 storage"""
        project_dir = get_testcase_project("RQ0_PYTHON_F4_03")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "undefined" in stdout.lower() or "undefined" in stderr.lower()
    
    def test_f4_04_duplicate_external_alias(self):
        """TC-F4-04: 同模块 external alias 重复"""
        project_dir = get_testcase_project("RQ0_PYTHON_F4_04")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "duplicate" in stdout.lower() or "duplicate" in stderr.lower()
    
    def test_f4_05_alias_not_in_target(self):
        """TC-F4-05: external alias 在目标模块不存在"""
        project_dir = get_testcase_project("RQ0_PYTHON_F4_05")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "missing" in stdout.lower() or "missing" in stderr.lower()
    
    def test_f4_06_alias_conflicts_with_local(self):
        """TC-F4-06: external alias 与 local storage 册突"""
        project_dir = get_testcase_project("RQ0_PYTHON_F4_06")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "conflict" in stdout.lower() or "conflict" in stderr.lower()
    
    def test_f4_07_source_module_not_found(self):
        """TC-F4-07: source_module 不存在"""
        project_dir = get_testcase_project("RQ0_PYTHON_F4_07")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "not found" in stdout.lower() or "not found" in stderr.lower()
