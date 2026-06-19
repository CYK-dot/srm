# python_tests/CMakeLists.txt - SRM Python测试

# 查找Python解释器
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# 查找pytest可执行文件
execute_process(
    COMMAND ${Python3_EXECUTABLE} -m pytest --version
    RESULT_VARIABLE PYTEST_RESULT
    OUTPUT_QUIET
    ERROR_QUIET
)

if(NOT PYTEST_RESULT EQUAL 0)
    message(WARNING "pytest not found. Python tests will be skipped.")
    return()
endif()

# 获取Python测试目录的绝对路径
get_filename_component(PYTHON_TESTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}" ABSOLUTE)

# 添加Python测试 - 运行所有测试
add_test(
    NAME python_tests_all
    COMMAND ${Python3_EXECUTABLE} -m pytest "${PYTHON_TESTS_DIR}" -v
    WORKING_DIRECTORY "${PYTHON_TESTS_DIR}"
)

# 按功能点添加单独的测试
set(PYTHON_TEST_FILES
    test_f1_schema.py
    test_f2_collect.py
    test_f3_uniqueness.py
    test_f4_reference.py
    test_f5_merge.py
    test_f6_layout.py
)

foreach(TEST_FILE ${PYTHON_TEST_FILES})
    # 从文件名提取测试名称（去掉.py后缀）
    get_filename_component(TEST_NAME "${TEST_FILE}" NAME_WE)
    
    add_test(
        NAME ${TEST_NAME}
        COMMAND ${Python3_EXECUTABLE} -m pytest "${PYTHON_TESTS_DIR}/${TEST_FILE}" -v
        WORKING_DIRECTORY "${PYTHON_TESTS_DIR}"
    )
endforeach()
