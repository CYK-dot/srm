"""
F1 - 类型定义校验测试
验证 srm_types.json 中 readonly + length 的合法性组合
"""
import pytest
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF1TypeValidation:
    """F1 - 类型定义校验测试类"""

    def test_tc_f1_01_readonly_no_length(self):
        """TC-F1-01: readonly=true, 无 length → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F2_01")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f1_02_readwrite_with_length(self):
        """TC-F1-02: readonly=false, length=4 → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F2_02")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f1_03_default_with_length(self):
        """TC-F1-03: readonly 不指定, length=4 → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F2_03")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f1_04_readonly_with_length(self):
        """TC-F1-04: readonly=true, length=4 → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F2_04")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "readonly" in stderr.lower() or "length" in stderr.lower() or "非法" in stderr

    def test_tc_f1_05_readwrite_no_length(self):
        """TC-F1-05: readonly=false, 无 length → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F2_05")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "length" in stderr.lower() or "readonly" in stderr.lower() or "非法" in stderr

    def test_tc_f1_06_default_no_length(self):
        """TC-F1-06: readonly 不指定, 无 length → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F2_06")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "length" in stderr.lower() or "readonly" in stderr.lower() or "非法" in stderr
