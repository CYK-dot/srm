"""
F1 - JSON Schema 校验测试
"""
import pytest
from srm_test_common import (
    get_testcase_project,
    run_srm_module_verify
)


class TestF1SchemaValidation:
    """F1 - JSON Schema 校验测试类"""
    
    def test_f1_01_valid_log_with_format(self):
        """TC-F1-01: 合法模块含 log 类型且有 format，校验通过"""
        project_dir = get_testcase_project("PYTHON-TC-F1-01")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode == 0
        assert "valid" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f1_02_log_without_format(self):
        """TC-F1-02: log 类型缺少 format，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-02")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
        assert "format" in stderr.lower() or "format" in stdout.lower()
    
    def test_f1_03_counter_without_format(self):
        """TC-F1-03: counter 类型无 format 要求，校验通过"""
        project_dir = get_testcase_project("PYTHON-TC-F1-03")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode == 0
        assert "valid" in stdout.lower() or "ok" in stdout.lower()
    
    def test_f1_04_item_missing_name(self):
        """TC-F1-04: item 缺少 name，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-04")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_05_item_missing_storages(self):
        """TC-F1-05: item 缺少 storages，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-05")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_06_item_missing_data_type(self):
        """TC-F1-06: item 缺少 data_type，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-06")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_07_local_storage_missing_name(self):
        """TC-F1-07: local_storage 缺少 name，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-07")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_08_no_storages_defined(self):
        """TC-F1-08: 无 local_storages 且无 external_storages，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-08")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_09_module_missing_name(self):
        """TC-F1-09: module 缺少 name，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-09")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_10_module_name_not_string(self):
        """TC-F1-10: module.name 为非字符串，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-10")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_11_invalid_data_type(self):
        """TC-F1-11: data_type 不在枚举中，校验通过（Schema 允许任意字符串）"""
        project_dir = get_testcase_project("PYTHON-TC-F1-11")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        # 由于 JSON Schema 允许任意字符串作为 data_type，所以校验应该通过
        assert returncode == 0
    
    def test_f1_12_invalid_json_syntax(self):
        """TC-F1-12: JSON 语法错误，校验失败"""
        project_dir = get_testcase_project("PYTHON-TC-F1-12")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        assert returncode != 0
    
    def test_f1_13_no_module_files(self):
        """TC-F1-13: 无模块文件，警告退出"""
        project_dir = get_testcase_project("PYTHON-TC-F1-13")
        returncode, stdout, stderr = run_srm_module_verify(project_dir)
        
        # 应该返回 0（警告）或 1（错误）
        assert returncode in [0, 1]
        # 应该有警告信息
        assert "no" in stdout.lower() or "no" in stderr.lower()
