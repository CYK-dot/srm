"""
F4 - Storage-Item 一致性校验测试
"""
import pytest
from srm_test_common import (
    get_testcase_project,
    run_srm_build
)


class TestF4StorageItemConsistency:
    """F4 - Storage-Item 一致性校验测试类"""

    def test_tc_f4_01_readonly_item_in_readonly_storage(self):
        """TC-F4-01: readonly item + readonly storage → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F3_01")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f4_02_readwrite_item_in_readwrite_storage(self):
        """TC-F4-02: readwrite item + readwrite storage → 应通过"""
        project_dir = get_testcase_project("RQ1_PYTHON_F3_02")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode == 0, f"应通过但失败: {stderr}"

    def test_tc_f4_03_readonly_item_in_readwrite_storage(self):
        """TC-F4-03: readonly item + readwrite storage → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F3_03")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "readonly" in stderr.lower() or "readwrite" in stderr.lower() or "不匹配" in stderr or "mismatch" in stderr.lower()

    def test_tc_f4_04_readwrite_item_in_readonly_storage(self):
        """TC-F4-04: readwrite item + readonly storage → 应失败"""
        project_dir = get_testcase_project("RQ1_PYTHON_F3_04")
        returncode, stdout, stderr = run_srm_build(project_dir, project_dir / "build")

        assert returncode != 0, f"应失败但通过了"
        assert "readonly" in stderr.lower() or "readwrite" in stderr.lower() or "不匹配" in stderr or "mismatch" in stderr.lower()
