"""
F2 - 模块收集与模块名冲突检测测试
"""
import pytest
import tempfile
import os
from pathlib import Path
from srm_test_common import (
    get_testcase_project,
    run_srm_module_collect
)


class TestF2ModuleCollection:
    """F2 - 模块收集与模块名冲突检测测试类"""
    
    def test_f2_01_no_module_files(self):
        """TC-F2-01: 无模块文件，警告退出"""
        project_dir = get_testcase_project("PYTHON-TC-F2-01")
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            returncode, stdout, stderr = run_srm_module_collect(project_dir, output_path)
            
            # 应该返回 0（警告）或 1（错误）
            assert returncode in [0, 1]
            # 应该有警告信息
            assert "no" in stdout.lower() or "no" in stderr.lower()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_f2_02_single_valid_module(self):
        """TC-F2-02: 单个合法模块，收集成功"""
        project_dir = get_testcase_project("PYTHON-TC-F2-02")
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            returncode, stdout, stderr = run_srm_module_collect(project_dir, output_path)
            
            assert returncode == 0
            assert os.path.exists(output_path)
            
            # 验证输出文件内容
            import json
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "modules" in data
            assert len(data["modules"]) == 1
            assert data["modules"][0]["module"]["name"] == "sensor"
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_f2_03_module_missing_name(self):
        """TC-F2-03: 单个非法模块（缺 name），收集失败"""
        project_dir = get_testcase_project("PYTHON-TC-F2-03")
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            returncode, stdout, stderr = run_srm_module_collect(project_dir, output_path)
            
            # 应该返回 1（错误）
            assert returncode == 1
            # 应该有错误信息
            assert "no valid modules" in stdout.lower() or "no valid modules" in stderr.lower()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_f2_04_multiple_valid_modules(self):
        """TC-F2-04: 多个合法模块名不同，收集成功"""
        project_dir = get_testcase_project("PYTHON-TC-F2-04")
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            returncode, stdout, stderr = run_srm_module_collect(project_dir, output_path)
            
            assert returncode == 0
            assert os.path.exists(output_path)
            
            # 验证输出文件内容
            import json
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "modules" in data
            assert len(data["modules"]) == 2
            
            module_names = [m["module"]["name"] for m in data["modules"]]
            assert "sensor" in module_names
            assert "actuator" in module_names
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_f2_05_one_module_missing_name(self):
        """TC-F2-05: 多模块中有非法文件，跳过后处理"""
        project_dir = get_testcase_project("PYTHON-TC-F2-05")
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            returncode, stdout, stderr = run_srm_module_collect(project_dir, output_path)
            
            # 应该返回 0（成功，跳过非法文件）或 1（失败）
            assert returncode in [0, 1]
            
            if returncode == 0:
                # 如果成功，应该只有 1 个模块
                import json
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                assert "modules" in data
                assert len(data["modules"]) == 1
                assert data["modules"][0]["module"]["name"] == "sensor"
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_f2_06_duplicate_module_names(self):
        """TC-F2-06: 多模块同名，报错退出"""
        project_dir = get_testcase_project("PYTHON-TC-F2-06")
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            returncode, stdout, stderr = run_srm_module_collect(project_dir, output_path)
            
            # 应该返回 1（错误）
            assert returncode == 1
            # 应该有错误信息
            assert "duplicate" in stdout.lower() or "duplicate" in stderr.lower()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
