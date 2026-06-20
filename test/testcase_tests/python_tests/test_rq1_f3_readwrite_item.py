"""
F3 - Item 值约束测试：readwrite item 不允许有值
"""
import pytest
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF3ReadwriteItemConstraint:
    """F3 - Item 值约束测试类"""

    def test_tc_f3_01_readwrite_without_value(self):
        """TC-F3-01: readwrite type + 无 value → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F3_05")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f3_02_readwrite_with_string_value(self):
        """TC-F3-02: readwrite type + string_value → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F3_06")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "string_value" in stderr.lower() or "readonly" in stderr.lower()

    def test_tc_f3_03_readwrite_with_file_value(self):
        """TC-F3-03: readwrite type + file_value → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F3_07")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "file_value" in stderr.lower() or "readonly" in stderr.lower()
