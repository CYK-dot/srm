cmake_minimum_required(VERSION 3.20)

project(SRM_Tests C)

# 设置C标准
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# 启用CTest
enable_testing()

# 包含SRM工具链模块（位于项目根目录）
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/..")
include(srm)

# FetchContent用于获取Unity测试框架
include(FetchContent)
FetchContent_Declare(
    unity
    GIT_REPOSITORY https://github.com/ThrowTheSwitch/Unity.git
    GIT_TAG v2.5.2
)
FetchContent_MakeAvailable(unity)

# 测试用例目录
set(TESTCASE_PROJECTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/testcase_projects")

# 添加测试子目录
add_subdirectory(testcase_tests/c_tests)
add_subdirectory(testcase_tests/python_tests)