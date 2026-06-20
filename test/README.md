# SRM 测试指南

本目录包含 SRM 构建工具链的测试用例。

## 测试用例命名规范

测试用例目录采用 `{RQ编号}_{用例环境}_{需求功能点编号}_{测试套编号}` 格式：

- **RQ0**：初始项目功能
- **RQ1**：srm支持静态只读资源
- **PYTHON**：Python 测试用例
- **C**：C 语言测试用例

示例：
- `RQ0_PYTHON_F1_01` - RQ0 功能点 F1 的第 01 个 Python 测试用例
- `RQ1_C_F6_01` - RQ1 功能点 F6 的第 01 个 C 测试用例

## 功能点编号映射

| RQ | 功能点编号 | 功能点描述 | 测试环境 |
|----|-----------|-----------|----------|
| RQ0 | F1 | 模块 JSON Schema 校验 | PYTHON |
| RQ0 | F2 | 模块收集与模块名冲突检测 | PYTHON |
| RQ0 | F3 | 全局名称唯一性校验 | PYTHON |
| RQ0 | F4 | 引用完整性校验 | PYTHON |
| RQ0 | F5 | 项目合并为扁平结构 | PYTHON |
| RQ0 | F6 | 布局容量校验（含对齐） | PYTHON |
| RQ0 | F7 | 类型枚举生成 | C |
| RQ0 | F8 | Storage 宏生成 | C |
| RQ0 | F9 | Item 宏生成 | C |
| RQ0 | F10 | srm_get_offset 有效查询 | C |
| RQ0 | F11 | srm_get_offset 无效查询 | C |
| RQ0 | F12 | srm_get_storage_size | C |
| RQ0 | F13 | srm_get_item_size | C |
| RQ0 | F14 | 名称到 C 标识符转换 | C |
| RQ0 | F15 | 偏移量对齐计算 | C |
| RQ0 | F16 | SRM 接口分离测试 | C |
| RQ1 | F1 | 静态只读资源类型验证 | PYTHON |
| RQ1 | F2 | 静态只读资源 item value 验证 | PYTHON |
| RQ1 | F3 | 静态只读资源 storage-item 一致性 | PYTHON |
| RQ1 | F4 | 静态只读资源数组支持 | PYTHON |
| RQ1 | F5 | 静态只读资源文件值支持 | PYTHON |
| RQ1 | F6 | srm_get_readonly_item | C |
| RQ1 | F7 | srm_get_readonly_storage | C |
| RQ1 | F8 | srm_get_offset 兼容性测试 | C |

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
pytest python_tests/test_rq0_f1_schema.py -v

# 运行 C 测试中的特定用例
cd test/build
ctest -R test_rq0_c_f7_01_type_enum_single -V

# 运行特定功能点的所有测试
cd test/testcase_tests
pytest python_tests -k "RQ0_F1" -v
```

## 测试用例统计

| 测试环境 | 用例数量 |
|----------|----------|
| RQ0 Python | 40 |
| RQ0 C | 36 |
| RQ1 Python | 19 |
| RQ1 C | 9 |
| **总计** | **104** |
