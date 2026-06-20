# c_tests/CMakeLists.txt - SRM C代码测试

# 测试用例项目目录
# CMAKE_CURRENT_SOURCE_DIR 是 test/testcase_tests/c_tests
# testcase_projects 在 test/testcase_projects
set(TESTCASE_PROJECTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../testcase_projects")

# ============================================================
# RQ0 测试 - 初始项目功能（C-TC-F* → RQ0_C_F*）
# ============================================================

# RQ0-F7 - 类型枚举生成测试（原 F1）
srm_add_test(
    NAME test_rq0_c_f7_01_type_enum_single
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F7_01"
    TEST_FILE "test_f1_type_enum.c"
)

srm_add_test(
    NAME test_rq0_c_f7_02_type_enum_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F7_02"
    TEST_FILE "test_f1_type_enum.c"
)

srm_add_test(
    NAME test_rq0_c_f7_03_type_enum_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F7_03"
    TEST_FILE "test_f1_type_enum.c"
)

srm_add_test(
    NAME test_rq0_c_f7_04_type_enum_multiple
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F7_04"
    TEST_FILE "test_f1_type_enum.c"
)

# RQ0-F8 - Storage宏生成测试（原 F2）
srm_add_test(
    NAME test_rq0_c_f8_01_storage_macros
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F8_01"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_rq0_c_f8_02_storage_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F8_02"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_rq0_c_f8_03_storage_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F8_03"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_rq0_c_f8_04_storage_no_size
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F8_04"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_rq0_c_f8_05_storage_multiple
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F8_05"
    TEST_FILE "test_f2_storage_macros.c"
)

# RQ0-F9 - Item宏生成测试（原 F3）
srm_add_test(
    NAME test_rq0_c_f9_01_item_macros
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F9_01"
    TEST_FILE "test_f3_item_macros.c"
)

srm_add_test(
    NAME test_rq0_c_f9_02_item_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F9_02"
    TEST_FILE "test_f3_item_macros.c"
)

srm_add_test(
    NAME test_rq0_c_f9_03_item_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F9_03"
    TEST_FILE "test_f3_item_macros.c"
)

srm_add_test(
    NAME test_rq0_c_f9_04_item_multiple
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F9_04"
    TEST_FILE "test_f3_item_macros.c"
)

# RQ0-F10 - srm_get_offset有效查询测试（原 F4）
srm_add_test(
    NAME test_rq0_c_f10_01_offset_first_item
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F10_01"
    TEST_FILE "test_f4_offset_valid.c"
)

srm_add_test(
    NAME test_rq0_c_f10_02_offset_no_align
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F10_02"
    TEST_FILE "test_f4_offset_valid.c"
)

srm_add_test(
    NAME test_rq0_c_f10_03_offset_aligned
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F10_03"
    TEST_FILE "test_f4_offset_valid.c"
)

srm_add_test(
    NAME test_rq0_c_f10_04_offset_need_padding
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F10_04"
    TEST_FILE "test_f4_offset_valid.c"
)

# RQ0-F11 - srm_get_offset无效查询测试（原 F5）
srm_add_test(
    NAME test_rq0_c_f11_01_offset_item_not_in_storage
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F11_01"
    TEST_FILE "test_f5_offset_invalid.c"
)

srm_add_test(
    NAME test_rq0_c_f11_02_offset_invalid_storage
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F11_02"
    TEST_FILE "test_f5_offset_invalid.c"
)

srm_add_test(
    NAME test_rq0_c_f11_03_offset_invalid_item
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F11_03"
    TEST_FILE "test_f5_offset_invalid.c"
)

# RQ0-F12 - srm_get_storage_size测试（原 F6）
srm_add_test(
    NAME test_rq0_c_f12_01_storage_size_valid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F12_01"
    TEST_FILE "test_f6_storage_size.c"
)

srm_add_test(
    NAME test_rq0_c_f12_02_storage_size_no_size
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F12_02"
    TEST_FILE "test_f6_storage_size.c"
)

srm_add_test(
    NAME test_rq0_c_f12_03_storage_size_invalid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F12_03"
    TEST_FILE "test_f6_storage_size.c"
)

# RQ0-F13 - srm_get_item_size测试（原 F7）
srm_add_test(
    NAME test_rq0_c_f13_01_item_size_fixed
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F13_01"
    TEST_FILE "test_f7_item_size.c"
)

srm_add_test(
    NAME test_rq0_c_f13_02_item_size_readonly
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F13_02"
    TEST_FILE "test_f7_item_size.c"
)

srm_add_test(
    NAME test_rq0_c_f13_03_item_size_invalid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F13_03"
    TEST_FILE "test_f7_item_size.c"
)

# RQ0-F14 - 名称到C标识符转换测试（原 F8）
srm_add_test(
    NAME test_rq0_c_f14_01_name_alphanumeric
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_01"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_rq0_c_f14_02_name_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_02"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_rq0_c_f14_03_name_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_03"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_rq0_c_f14_04_name_space
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_04"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_rq0_c_f14_05_name_special_char
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_05"
    TEST_FILE "test_f8_name_conversion.c"
)

# RQ0-F15 - 偏移量对齐计算测试（原 F9）
srm_add_test(
    NAME test_rq0_c_f15_01_align4_already_aligned
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F15_01"
    TEST_FILE "test_f9_alignment.c"
)

srm_add_test(
    NAME test_rq0_c_f15_02_align8_already_aligned
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F15_02"
    TEST_FILE "test_f9_alignment.c"
)

srm_add_test(
    NAME test_rq0_c_f15_03_align4_need_padding
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F15_03"
    TEST_FILE "test_f9_alignment.c"
)

srm_add_test(
    NAME test_rq0_c_f15_04_align8_need_padding
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F15_04"
    TEST_FILE "test_f9_alignment.c"
)

# RQ0-F16 - SRM接口分离测试（原 F10）
add_executable(test_rq0_c_f16_srm_interface
    "test_f10_srm_interface.c"
)

target_link_srm_library(test_rq0_c_f16_srm_interface
    PROJ_ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F10_01"
    OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/f16_srm_generated"
)

target_link_srm_interface(test_rq0_c_f16_srm_interface)

target_link_libraries(test_rq0_c_f16_srm_interface PRIVATE unity)

add_test(NAME test_rq0_c_f16_srm_interface COMMAND test_rq0_c_f16_srm_interface)

# ============================================================
# RQ1 测试 - srm支持静态只读资源（C-TC-F* → RQ1_C_F*）
# ============================================================

# RQ1-F6 - srm_get_readonly_item 测试（复用 RQ0_C_F13 测试数据）
srm_add_test(
    NAME test_rq1_c_f6_01_readonly_item_valid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F13_01"
    TEST_FILE "test_f11_readonly_item.c"
)

srm_add_test(
    NAME test_rq1_c_f6_02_readonly_item_invalid_item
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F13_02"
    TEST_FILE "test_f11_readonly_item.c"
)

srm_add_test(
    NAME test_rq1_c_f6_03_readonly_item_invalid_storage
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F13_03"
    TEST_FILE "test_f11_readonly_item.c"
)

# RQ1-F7 - srm_get_readonly_storage 测试（复用 RQ0_C_F14 测试数据）
srm_add_test(
    NAME test_rq1_c_f7_01_readonly_storage_valid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_01"
    TEST_FILE "test_f12_readonly_storage.c"
)

srm_add_test(
    NAME test_rq1_c_f7_02_readonly_storage_invalid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_02"
    TEST_FILE "test_f12_readonly_storage.c"
)

srm_add_test(
    NAME test_rq1_c_f7_03_readwrite_storage_returns_null
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F14_03"
    TEST_FILE "test_f12_readonly_storage.c"
)

# RQ1-F8 - srm_get_offset 兼容性测试（复用 RQ0_C_F15 测试数据）
srm_add_test(
    NAME test_rq1_c_f8_01_offset_readonly_valid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F15_01"
    TEST_FILE "test_f13_offset_readonly.c"
)

srm_add_test(
    NAME test_rq1_c_f8_02_offset_readwrite_compatible
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F15_02"
    TEST_FILE "test_f13_offset_readonly.c"
)

srm_add_test(
    NAME test_rq1_c_f8_03_offset_readonly_item_not_in_storage
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/RQ0_C_F15_03"
    TEST_FILE "test_f13_offset_readonly.c"
)