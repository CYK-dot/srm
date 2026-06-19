# SRM C 代码测试说明

本目录包含 SRM C 代码生成的测试用例，使用 CMake 构建系统和 Unity 测试框架。

## 前置条件

1. **CMake 3.20+**
   - 下载: https://cmake.org/download/
   - 或使用包管理器安装

2. **GCC 编译器**
   - Windows: MinGW 或 MSYS2
   - Linux: `sudo apt install build-essential`
   - Mac: `xcode-select --install`

3. **Python 3.8+**
   - 用于 SRM 工具链代码生成

4. **网络连接**
   - 首次构建时需要下载 Unity 测试框架

## 快速开始

### Windows

```cmd
cd test
build_and_test.bat
```

### Linux/Mac

```bash
cd test
chmod +x build_and_test.sh
./build_and_test.sh
```

## 手动构建

```bash
# 进入测试目录
cd test

# 创建构建目录
mkdir build
cd build

# 配置 CMake
cmake ..

# 构建所有测试
cmake --build .

# 运行所有测试
ctest -V

# 运行单个测试
ctest -R test_c_f1_01_type_enum_single -V

# 运行特定功能点的所有测试
ctest -R test_c_f1 -V
```

## 测试用例列表

| 测试名称 | 功能点 | 验证内容 |
|----------|--------|----------|
| test_c_f1_01_type_enum_single | F1 | 单个类型枚举 |
| test_c_f1_02_type_enum_hyphen | F1 | 连字符类型名转换 |
| test_c_f1_03_type_enum_digit_start | F1 | 数字开头类型名 |
| test_c_f1_04_type_enum_multiple | F1 | 多个类型枚举 |
| test_c_f2_01_storage_macros | F2 | Storage ID 和 SIZE 宏 |
| test_c_f2_02_storage_hyphen | F2 | 连字符 Storage 名 |
| test_c_f2_03_storage_digit_start | F2 | 数字开头 Storage 名 |
| test_c_f2_04_storage_no_size | F2 | 无 size 字段的 Storage |
| test_c_f2_05_storage_multiple | F2 | 多个 Storage |
| test_c_f3_01_item_macros | F3 | Item ID 和 TYPE 宏 |
| test_c_f3_02_item_hyphen | F3 | 连字符 Item 名 |
| test_c_f3_03_item_digit_start | F3 | 数字开头 Item 名 |
| test_c_f3_04_item_multiple | F3 | 多个 Item |
| test_c_f4_01_offset_first_item | F4 | 第一个 Item 偏移量为 0 |
| test_c_f4_02_offset_no_align | F4 | 无对齐偏移量计算 |
| test_c_f4_03_offset_aligned | F4 | 已对齐偏移量计算 |
| test_c_f4_04_offset_need_padding | F4 | 需要填充的偏移量 |
| test_c_f5_01_offset_item_not_in_storage | F5 | Item 不在 Storage 中 |
| test_c_f5_02_offset_invalid_storage | F5 | 无效 Storage ID |
| test_c_f5_03_offset_invalid_item | F5 | 无效 Item ID |
| test_c_f6_01_storage_size_valid | F6 | 有效 Storage Size |
| test_c_f6_02_storage_size_no_size | F6 | 无 Size 字段 |
| test_c_f6_03_storage_size_invalid | F6 | 无效 Storage ID |
| test_c_f7_01_item_size_fixed | F7 | 固定长度类型 |
| test_c_f7_02_item_size_strip | F7 | 动态长度类型 |
| test_c_f7_03_item_size_invalid | F7 | 无效 Item ID |
| test_c_f8_01_name_alphanumeric | F8 | 纯字母数字名称 |
| test_c_f8_02_name_digit_start | F8 | 数字开头名称 |
| test_c_f8_03_name_hyphen | F8 | 连字符名称 |
| test_c_f8_04_name_space | F8 | 空格名称 |
| test_c_f8_05_name_special_char | F8 | 特殊字符名称 |
| test_c_f9_01_align4_already_aligned | F9 | 4字节对齐已对齐 |
| test_c_f9_02_align8_already_aligned | F9 | 8字节对齐已对齐 |
| test_c_f9_03_align4_need_padding | F9 | 4字节对齐需要填充 |
| test_c_f9_04_align8_need_padding | F9 | 8字节对齐需要填充 |
| test_c_f10_srm_interface | F10 | SRM接口分离测试（target_link_srm_library + target_link_srm_interface） |

## 测试输出示例

```
test 1
    Start 1: test_c_f1_01_type_enum_single

1: Test command: C:\03_Projects\esp32\hello_world\edfx\test\build\testcase_tests\c_tests\test_c_f1_01_type_enum_single.exe
1: Test timeout computed to be: 10000000
1: test_f1_type_enum.c:42:test_type_enum_exists:PASS
1: test_f1_type_enum.c:43:test_type_enum_values_start_from_1:PASS
1: test_f1_type_enum.c:44:test_type_enum_hyphen_conversion:PASS
1: test_f1_type_enum.c:45:test_type_enum_digit_start:PASS
1: -----------------------
1: 4 Tests 0 Failures 0 Ignored
1: OK
1/35  Test #1: test_c_f1_01_type_enum_single ...   Passed    0.01 sec
```

## 故障排除

### CMake 找不到 Python

```bash
# 设置 Python 路径
cmake -DPython3_EXECUTABLE=/path/to/python ..
```

### CMake 找不到 GCC

```bash
# 设置编译器路径
cmake -DCMAKE_C_COMPILER=/path/to/gcc ..
```

### Unity 下载失败

如果网络连接有问题，可以手动下载 Unity：

```bash
# 克隆 Unity 仓库
git clone https://github.com/ThrowTheSwitch/Unity.git external/unity

# 修改 CMakeLists.txt 中的 Unity 路径
```

## 目录结构

```
c_tests/
├── CMakeLists.txt              # C测试CMake文件
├── test_srm_common.h           # 公共头文件
├── test_f1_type_enum.c         # F1类型枚举测试
├── test_f2_storage_macros.c    # F2 Storage宏测试
├── test_f3_item_macros.c       # F3 Item宏测试
├── test_f4_offset_valid.c      # F4偏移量有效查询测试
├── test_f5_offset_invalid.c    # F5偏移量无效查询测试
├── test_f6_storage_size.c      # F6 storage size测试
├── test_f7_item_size.c         # F7 item size测试
├── test_f8_name_conversion.c   # F8名称转换测试
├── test_f9_alignment.c         # F9对齐计算测试
└── test_f10_srm_interface.c    # F10 SRM接口分离测试
```