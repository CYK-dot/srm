"""
F2 - Item 值约束测试：readonly item 必须有值
"""
import pytest
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF2ItemValueConstraint:
    """F2 - Item 值约束测试类"""

    def test_tc_f2_01_readonly_with_string_value(self):
        """TC-F2-01: readonly type + string_value → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F1_01")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f2_02_readonly_with_file_value(self):
        """TC-F2-02: readonly type + file_value → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F1_02")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f2_03_readonly_without_value(self):
        """TC-F2-03: readonly type + 无 value → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F1_03")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "readonly" in stderr.lower() or "value" in stderr.lower() or "string_value" in stderr.lower()

    def test_tc_f2_04_readonly_with_both_values(self):
        """TC-F2-04: readonly type + 同时有 string_value 和 file_value → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F1_04")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "互斥" in stderr or "both" in stderr.lower() or "string_value" in stderr.lower()
