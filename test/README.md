# SRM 测试指南

本目录包含 SRM 构建工具链的测试用例。

## 运行测试

### 前置条件

1. 安装 Python 依赖：
   ```bash
   pip install jsonschema jinja2 pytest
   ```

2. 安装 CMake 3.20+ 和 GCC（MinGW 或 MSYS2）

### 运行 Python 测试

```bash
cd test/testcase_tests
pytest python_tests -v
```

### 运行 C 代码测试

```bash
cd test
mkdir -p build && cd build
cmake ..
cmake --build .
ctest -V
```

### 运行所有测试

```bash
# Python 测试
cd test/testcase_tests
pytest python_tests -v

# C 测试
cd test/build
ctest -V
```

### 运行特定测试

```bash
# 运行单个 Python 测试文件
cd test/testcase_tests
pytest python_tests/test_f1_schema.py -v

# 运行 C 测试中的特定用例
cd test/build
ctest -R test_c_f1_01_type_enum_single -V
```
