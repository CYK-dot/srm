"""
F6 - 布局容量校验（含对齐）测试
"""
import pytest
import tempfile
from pathlib import Path
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF6LayoutVerification:
    """F6 - 布局容量校验（含对齐）测试类"""
    
    def test_f6_01_no_overflow(self):
        """TC-F6-01: 无溢出校验通过"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_01")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            assert "all items successfully inserted" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f6_02_capacity_overflow(self):
        """TC-F6-02: 容量溢出"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_02")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "overflow" in stdout.lower() or "overflow" in stderr.lower()
    
    def test_f6_03_alignment_no_overflow(self):
        """TC-F6-03: 对齐后无溢出"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_03")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            assert "all items successfully inserted" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f6_04_alignment_causes_overflow(self):
        """TC-F6-04: 对齐填充导致溢出"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_04")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "overflow" in stdout.lower() or "overflow" in stderr.lower()
    
    def test_f6_05_no_size_limit(self):
        """TC-F6-05: storage 无 size 限制"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_05")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            assert "all items successfully inserted" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f6_06_readonly_item_valid(self):
        """TC-F6-06: readonly item 正常计算"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_06")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 0
            assert "all items successfully inserted" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f6_07_readonly_item_missing_value(self):
        """TC-F6-07: readonly item 缺少 string_value/file_value"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_07")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            # 由于 readonly item 缺少 string_value，JSON Schema 验证会失败
            assert returncode == 1
            assert "string_value" in stdout.lower() or "string_value" in stderr.lower()
    
    def test_f6_08_readonly_item_wrong_type(self):
        """TC-F6-08: readonly item 的 string_value 类型错误"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_08")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            # 由于 string_value 字段类型错误，JSON Schema 验证会失败
            assert returncode == 1
            assert "not of type" in stdout.lower() or "not of type" in stderr.lower()
    
    def test_f6_09_unknown_data_type(self):
        """TC-F6-09: 未知 data_type"""
        project_dir = get_testcase_project("RQ0_PYTHON_F6_09")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "build"
            returncode, stdout, stderr = run_srm_build(project_dir, output_dir)
            
            assert returncode == 1
            assert "unknown" in stdout.lower() or "unknown" in stderr.lower()
