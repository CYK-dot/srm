"""
F6 - 只读数组代码生成测试
"""
import pytest
import re
from pathlib import Path
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF6ReadonlyArrayCodeGeneration:
    """F6 - 只读数组代码生成测试类"""

    def test_tc_f6_01_string_value_generates_const_array(self):
        """TC-F6-01: string_value item 生成 const 数组"""
        project_dir = get_testcase_project("RQ1_PYTHON_F5_01")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"构建失败: {stderr}"

        # 检查生成的 .c 文件是否包含 const 数组
        c_files = list((project_dir / "build").glob("*.c"))
        assert len(c_files) > 0, "未生成 .c 文件"

        c_content = c_files[0].read_text(encoding="utf-8")
        assert "const" in c_content.lower(), "未生成 const 数组"
        assert "TEST_ITEM" in c_content.upper(), "未找到 TEST_ITEM 定义"

    def test_tc_f6_02_file_value_generates_const_array(self):
        """TC-F6-02: file_value item 生成 const 数组"""
        project_dir = get_testcase_project("RQ1_PYTHON_F5_02")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"构建失败: {stderr}"

        # 检查生成的 .c 文件是否包含 const 数组
        c_files = list((project_dir / "build").glob("*.c"))
        assert len(c_files) > 0, "未生成 .c 文件"

        c_content = c_files[0].read_text(encoding="utf-8")
        assert "const" in c_content.lower(), "未生成 const 数组"
        assert "TEST_ITEM" in c_content.upper(), "未找到 TEST_ITEM 定义"
