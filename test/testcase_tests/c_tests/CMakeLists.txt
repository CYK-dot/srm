# c_tests/CMakeLists.txt - SRM C代码测试

# 测试用例项目目录
# CMAKE_CURRENT_SOURCE_DIR 是 test/testcase_tests/c_tests
# testcase_projects 在 test/testcase_projects
set(TESTCASE_PROJECTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../testcase_projects")

# F1 - 类型枚举生成测试
srm_add_test(
    NAME test_c_f1_01_type_enum_single
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F1-01"
    TEST_FILE "test_f1_type_enum.c"
)

srm_add_test(
    NAME test_c_f1_02_type_enum_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F1-02"
    TEST_FILE "test_f1_type_enum.c"
)

srm_add_test(
    NAME test_c_f1_03_type_enum_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F1-03"
    TEST_FILE "test_f1_type_enum.c"
)

srm_add_test(
    NAME test_c_f1_04_type_enum_multiple
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F1-04"
    TEST_FILE "test_f1_type_enum.c"
)

# F2 - Storage宏生成测试
srm_add_test(
    NAME test_c_f2_01_storage_macros
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F2-01"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_c_f2_02_storage_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F2-02"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_c_f2_03_storage_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F2-03"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_c_f2_04_storage_no_size
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F2-04"
    TEST_FILE "test_f2_storage_macros.c"
)

srm_add_test(
    NAME test_c_f2_05_storage_multiple
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F2-05"
    TEST_FILE "test_f2_storage_macros.c"
)

# F3 - Item宏生成测试
srm_add_test(
    NAME test_c_f3_01_item_macros
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F3-01"
    TEST_FILE "test_f3_item_macros.c"
)

srm_add_test(
    NAME test_c_f3_02_item_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F3-02"
    TEST_FILE "test_f3_item_macros.c"
)

srm_add_test(
    NAME test_c_f3_03_item_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F3-03"
    TEST_FILE "test_f3_item_macros.c"
)

srm_add_test(
    NAME test_c_f3_04_item_multiple
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F3-04"
    TEST_FILE "test_f3_item_macros.c"
)

# F4 - srm_get_offset有效查询测试
srm_add_test(
    NAME test_c_f4_01_offset_first_item
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F4-01"
    TEST_FILE "test_f4_offset_valid.c"
)

srm_add_test(
    NAME test_c_f4_02_offset_no_align
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F4-02"
    TEST_FILE "test_f4_offset_valid.c"
)

srm_add_test(
    NAME test_c_f4_03_offset_aligned
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F4-03"
    TEST_FILE "test_f4_offset_valid.c"
)

srm_add_test(
    NAME test_c_f4_04_offset_need_padding
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F4-04"
    TEST_FILE "test_f4_offset_valid.c"
)

# F5 - srm_get_offset无效查询测试
srm_add_test(
    NAME test_c_f5_01_offset_item_not_in_storage
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F5-01"
    TEST_FILE "test_f5_offset_invalid.c"
)

srm_add_test(
    NAME test_c_f5_02_offset_invalid_storage
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F5-02"
    TEST_FILE "test_f5_offset_invalid.c"
)

srm_add_test(
    NAME test_c_f5_03_offset_invalid_item
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F5-03"
    TEST_FILE "test_f5_offset_invalid.c"
)

# F6 - srm_get_storage_size测试
srm_add_test(
    NAME test_c_f6_01_storage_size_valid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F6-01"
    TEST_FILE "test_f6_storage_size.c"
)

srm_add_test(
    NAME test_c_f6_02_storage_size_no_size
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F6-02"
    TEST_FILE "test_f6_storage_size.c"
)

srm_add_test(
    NAME test_c_f6_03_storage_size_invalid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F6-03"
    TEST_FILE "test_f6_storage_size.c"
)

# F7 - srm_get_item_size测试
srm_add_test(
    NAME test_c_f7_01_item_size_fixed
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F7-01"
    TEST_FILE "test_f7_item_size.c"
)

srm_add_test(
    NAME test_c_f7_02_item_size_strip
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F7-02"
    TEST_FILE "test_f7_item_size.c"
)

srm_add_test(
    NAME test_c_f7_03_item_size_invalid
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F7-03"
    TEST_FILE "test_f7_item_size.c"
)

# F8 - 名称到C标识符转换测试
srm_add_test(
    NAME test_c_f8_01_name_alphanumeric
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F8-01"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_c_f8_02_name_digit_start
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F8-02"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_c_f8_03_name_hyphen
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F8-03"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_c_f8_04_name_space
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F8-04"
    TEST_FILE "test_f8_name_conversion.c"
)

srm_add_test(
    NAME test_c_f8_05_name_special_char
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F8-05"
    TEST_FILE "test_f8_name_conversion.c"
)

# F9 - 偏移量对齐计算测试
srm_add_test(
    NAME test_c_f9_01_align4_already_aligned
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F9-01"
    TEST_FILE "test_f9_alignment.c"
)

srm_add_test(
    NAME test_c_f9_02_align8_already_aligned
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F9-02"
    TEST_FILE "test_f9_alignment.c"
)

srm_add_test(
    NAME test_c_f9_03_align4_need_padding
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F9-03"
    TEST_FILE "test_f9_alignment.c"
)

srm_add_test(
    NAME test_c_f9_04_align8_need_padding
    ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F9-04"
    TEST_FILE "test_f9_alignment.c"
)

# F10 - SRM接口分离测试
# 此测试验证 target_link_srm_library + target_link_srm_interface 的两层接口
# 1. 项目级：使用 target_link_srm_library 将SRM实现注入可执行文件
# 2. 组件级：使用 target_link_srm_interface 仅获取头文件接口，不耦合任何库

# 创建测试可执行文件
add_executable(test_c_f10_srm_interface
    "test_f10_srm_interface.c"
)

# 项目级：将SRM实现（.c）注入可执行文件
target_link_srm_library(test_c_f10_srm_interface
    PROJ_ROOT_DIR "${TESTCASE_PROJECTS_DIR}/C-TC-F4-01"
    OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/f10_srm_generated"
)

# 组件级：仅暴露头文件路径（验证接口分离）
# 此调用不耦合任何库目标，仅从全局属性获取.srm_layout.h路径
target_link_srm_interface(test_c_f10_srm_interface)

# 链接Unity
target_link_libraries(test_c_f10_srm_interface PRIVATE unity)

add_test(NAME test_c_f10_srm_interface COMMAND test_c_f10_srm_interface)