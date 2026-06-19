"""
SRM 测试公共套件
提供测试辅助函数和工具
"""
import subprocess
import sys
import os
from pathlib import Path


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent.parent.parent


def get_testcase_project(testcase_id):
    """获取测试用例项目路径"""
    return get_project_root() / "test" / "testcase_projects" / testcase_id


def run_srm_build(root_dir, output_dir):
    """
    运行 srm_build.py 完整构建流程
    
    Args:
        root_dir: SRM 根目录（包含 srm_types.json 和模块目录）
        output_dir: 输出目录
    
    Returns:
        returncode: 返回码
        stdout: 标准输出
        stderr: 标准错误
    """
    script_path = get_project_root() / "src" / "scripts" / "srm_build.py"
    
    cmd = [
        sys.executable, str(script_path),
        "--root", str(root_dir),
        "--output-dir", str(output_dir)
    ]
    
    # 设置 PYTHONPATH 环境变量，确保模块导入正常
    env = os.environ.copy()
    env["PYTHONPATH"] = str(get_project_root())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(get_project_root()),
        env=env
    )
    
    return result.returncode, result.stdout, result.stderr


def run_srm_module_verify(project_dir, schema_path=None):
    """
    运行 srm_module_verify.py
    
    Args:
        project_dir: 项目目录路径
        schema_path: schema 文件路径（可选）
    
    Returns:
        returncode: 返回码
        stdout: 标准输出
        stderr: 标准错误
    """
    script_path = get_project_root() / "src" / "scripts" / "srm_module_verify.py"
    
    # 如果未指定 schema 路径，使用默认路径
    if schema_path is None:
        schema_path = get_project_root() / "src" / "scripts" / "srm_module.schema.json"
    
    cmd = [sys.executable, str(script_path), str(project_dir), "--schema", str(schema_path)]
    
    # 设置 PYTHONPATH 环境变量，确保模块导入正常
    env = os.environ.copy()
    env["PYTHONPATH"] = str(get_project_root())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(get_project_root()),
        env=env
    )
    
    return result.returncode, result.stdout, result.stderr


def run_srm_module_collect(project_dir, output_path):
    """
    运行 srm_module_collect.py
    
    Args:
        project_dir: 项目目录路径
        output_path: 输出文件路径
    
    Returns:
        returncode: 返回码
        stdout: 标准输出
        stderr: 标准错误
    """
    script_path = get_project_root() / "src" / "scripts" / "srm_module_collect.py"
    
    cmd = [sys.executable, str(script_path), str(project_dir), "-o", str(output_path)]
    
    # 设置 PYTHONPATH 环境变量，确保模块导入正常
    env = os.environ.copy()
    env["PYTHONPATH"] = str(get_project_root())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(get_project_root()),
        env=env
    )
    
    return result.returncode, result.stdout, result.stderr


def run_srm_project_verify(project_file):
    """
    运行 srm_project_verify.py
    
    Args:
        project_file: srm_project.json 文件路径
    
    Returns:
        returncode: 返回码
        stdout: 标准输出
        stderr: 标准错误
    """
    script_path = get_project_root() / "src" / "scripts" / "srm_project_verify.py"
    
    cmd = [sys.executable, str(script_path), str(project_file)]
    
    # 设置 PYTHONPATH 环境变量，确保模块导入正常
    env = os.environ.copy()
    env["PYTHONPATH"] = str(get_project_root())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(get_project_root()),
        env=env
    )
    
    return result.returncode, result.stdout, result.stderr


def run_srm_project_merge(project_file, output_path):
    """
    运行 srm_project_merge.py
    
    Args:
        project_file: srm_project.json 文件路径
        output_path: 输出文件路径
    
    Returns:
        returncode: 返回码
        stdout: 标准输出
        stderr: 标准错误
    """
    script_path = get_project_root() / "src" / "scripts" / "srm_project_merge.py"
    
    cmd = [sys.executable, str(script_path), str(project_file), "-o", str(output_path)]
    
    # 设置 PYTHONPATH 环境变量，确保模块导入正常
    env = os.environ.copy()
    env["PYTHONPATH"] = str(get_project_root())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(get_project_root()),
        env=env
    )
    
    return result.returncode, result.stdout, result.stderr


def run_srm_layout_verify(resolved_file, types_file):
    """
    运行 srm_layout_verify.py
    
    Args:
        resolved_file: srm_resolved.json 文件路径
        types_file: srm_types.json 文件路径
    
    Returns:
        returncode: 返回码
        stdout: 标准输出
        stderr: 标准错误
    """
    script_path = get_project_root() / "src" / "scripts" / "srm_layout_verify.py"
    
    cmd = [
        sys.executable, str(script_path),
        "--resolved", str(resolved_file),
        "--types", str(types_file)
    ]
    
    # 设置 PYTHONPATH 环境变量，确保模块导入正常
    env = os.environ.copy()
    env["PYTHONPATH"] = str(get_project_root())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(get_project_root()),
        env=env
    )
    
    return result.returncode, result.stdout, result.stderr


def run_srm_layout_generate(resolved_file, types_file, output_base):
    """
    运行 srm_layout_generate.py
    
    Args:
        resolved_file: srm_resolved.json 文件路径
        types_file: srm_types.json 文件路径
        output_base: 输出文件基础名（不含扩展名）
    
    Returns:
        returncode: 返回码
        stdout: 标准输出
        stderr: 标准错误
    """
    script_path = get_project_root() / "src" / "scripts" / "srm_layout_generate.py"
    
    cmd = [
        sys.executable, str(script_path),
        "--resolved", str(resolved_file),
        "--types", str(types_file),
        "--output", str(output_base)
    ]
    
    # 设置 PYTHONPATH 环境变量，确保模块导入正常
    env = os.environ.copy()
    env["PYTHONPATH"] = str(get_project_root())
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(get_project_root()),
        env=env
    )
    
    return result.returncode, result.stdout, result.stderr
