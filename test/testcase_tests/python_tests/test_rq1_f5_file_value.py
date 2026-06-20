"""
F5 - file_value 路径解析测试
"""
import pytest
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF5FileValuePathResolution:
    """F5 - file_value 路径解析测试类"""

    def test_tc_f5_01_file_value_existing_relative_path(self):
        """TC-F5-01: file_value 指向存在的相对路径 → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F4_01")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f5_02_file_value_nonexistent_path(self):
        """TC-F5-02: file_value 指向不存在的路径 → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F4_02")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
