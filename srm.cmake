# srm.cmake - SRM工具链CMake模块（统一版本）
#
# 提供函数用于：
# 1. 外部项目集成（FetchContent模式）
# 2. 内部测试支持
#
# 用法（外部项目）:
#   include(FetchContent)
#   FetchContent_Declare(srm URL ...)
#   FetchContent_MakeAvailable(srm)
#   add_srm_library(my_srm)
#
# 用法（内部测试）:
#   list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}")
#   include(srm)
#   srm_generate_layout(
#       ROOT_DIR <root_dir>
#       OUTPUT_DIR <output_dir>
#       [TARGETS <target1> <target2> ...]
#   )
#   srm_add_test(
#       NAME <name>
#       ROOT_DIR <root_dir>
#       TEST_FILE <test_file>
#       [UNITY_DEPS <dep1> <dep2> ...]
#   )

# 自动检测项目根目录和脚本目录
# CMAKE_CURRENT_LIST_DIR 指向项目根目录
get_filename_component(SRM_PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
set(SRM_SCRIPTS_DIR "${SRM_PROJECT_ROOT}/src/scripts" CACHE PATH "SRM scripts directory")

# Python解释器
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# SRM构建脚本
set(SRM_BUILD_SCRIPT "${SRM_SCRIPTS_DIR}/srm_build.py")

# 检查SRM脚本是否存在
if(NOT EXISTS "${SRM_BUILD_SCRIPT}")
    message(FATAL_ERROR "SRM build script not found: ${SRM_BUILD_SCRIPT}")
endif()

#[=======================================================================[.rst:
add_srm_library
---------------

为外部项目添加SRM库（FetchContent模式）。

.. code-block:: cmake

    add_srm_library(my_srm
        [CONFIG_DIR <config_dir>]
        [OUTPUT_DIR <output_dir>]
    )

参数:
    CONFIG_DIR - SRM配置目录（默认: ${CMAKE_CURRENT_SOURCE_DIR}/srm）
    OUTPUT_DIR - 输出目录（默认: ${CMAKE_CURRENT_BINARY_DIR}/srm_generated）
#]=======================================================================]
function(add_srm_library TARGET_NAME)
    set(options "")
    set(oneValueArgs CONFIG_DIR OUTPUT_DIR)
    set(multiValueArgs "")
    cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(NOT ARG_CONFIG_DIR)
        set(ARG_CONFIG_DIR "${CMAKE_CURRENT_SOURCE_DIR}/srm")
    endif()
    if(NOT ARG_OUTPUT_DIR)
        set(ARG_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/srm_generated")
    endif()

    get_filename_component(CONFIG_DIR "${ARG_CONFIG_DIR}" ABSOLUTE)
    get_filename_component(OUTPUT_DIR "${ARG_OUTPUT_DIR}" ABSOLUTE)

    file(GLOB_RECURSE SRM_DEPENDS
        "${CONFIG_DIR}/srm_types.json"
        "${CONFIG_DIR}/*/srm_module.json"
        "${CONFIG_DIR}/*/*/srm_module.json"
    )

    list(LENGTH SRM_DEPENDS DEPENDS_COUNT)
    if(DEPENDS_COUNT EQUAL 0)
        message(WARNING "No SRM configuration files found in ${CONFIG_DIR}. Add srm_types.json and module subdirectories.")
    endif()

    set(GENERATED_H "${OUTPUT_DIR}/srm_layout.h")
    set(GENERATED_C "${OUTPUT_DIR}/srm_layout.c")

    add_custom_command(
        OUTPUT ${GENERATED_H} ${GENERATED_C}
        COMMAND ${Python3_EXECUTABLE}
            "${SRM_BUILD_SCRIPT}"
            --root "${CONFIG_DIR}"
            --output-dir "${OUTPUT_DIR}"
        DEPENDS ${SRM_DEPENDS}
                "${SRM_BUILD_SCRIPT}"
                "${SRM_SCRIPTS_DIR}/srm_module_verify.py"
                "${SRM_SCRIPTS_DIR}/srm_module_collect.py"
                "${SRM_SCRIPTS_DIR}/srm_project_verify.py"
                "${SRM_SCRIPTS_DIR}/srm_project_merge.py"
                "${SRM_SCRIPTS_DIR}/srm_layout_verify.py"
                "${SRM_SCRIPTS_DIR}/srm_layout_generate.py"
                "${SRM_SCRIPTS_DIR}/srm_log.py"
        COMMENT "Generating SRM layout for ${TARGET_NAME} from ${CONFIG_DIR}"
        VERBATIM
    )

    add_custom_target(${TARGET_NAME}_generate DEPENDS ${GENERATED_H} ${GENERATED_C})

    add_library(${TARGET_NAME} STATIC ${GENERATED_C})
    target_include_directories(${TARGET_NAME} PUBLIC ${OUTPUT_DIR})
    add_dependencies(${TARGET_NAME} ${TARGET_NAME}_generate)
endfunction()

#[=======================================================================[.rst:
srm_generate_layout
-------------------

调用SRM工具链生成C代码。

.. code-block:: cmake

    srm_generate_layout(
        ROOT_DIR <root_dir>
        OUTPUT_DIR <output_dir>
        [TARGETS <target1> <target2> ...]
    )

参数:
    ROOT_DIR - SRM项目根目录（包含srm_types.json和模块目录）
    OUTPUT_DIR - 输出目录
    TARGETS - 可选，需要链接生成代码的CMake目标
#]=======================================================================]
function(srm_generate_layout)
    cmake_parse_arguments(
        ARG
        ""
        "ROOT_DIR;OUTPUT_DIR"
        "TARGETS"
        ${ARGN}
    )

    if(NOT ARG_ROOT_DIR)
        message(FATAL_ERROR "srm_generate_layout: ROOT_DIR is required")
    endif()

    if(NOT ARG_OUTPUT_DIR)
        message(FATAL_ERROR "srm_generate_layout: OUTPUT_DIR is required")
    endif()

    # 生成的文件路径
    set(H_FILE "${ARG_OUTPUT_DIR}/srm_layout.h")
    set(C_FILE "${ARG_OUTPUT_DIR}/srm_layout.c")

    # 创建输出目录
    file(MAKE_DIRECTORY "${ARG_OUTPUT_DIR}")

    # 添加自定义命令调用SRM构建脚本
    add_custom_command(
        OUTPUT "${H_FILE}" "${C_FILE}"
        COMMAND "${Python3_EXECUTABLE}" "${SRM_BUILD_SCRIPT}"
            --root "${ARG_ROOT_DIR}"
            --output-dir "${ARG_OUTPUT_DIR}"
        DEPENDS "${SRM_BUILD_SCRIPT}"
        COMMENT "Generating SRM layout for ${ARG_ROOT_DIR}"
        VERBATIM
    )

    # 如果指定了目标，将生成的文件添加到目标
    if(ARG_TARGETS)
        foreach(target IN LISTS ARG_TARGETS)
            target_sources(${target} PRIVATE "${C_FILE}")
            target_include_directories(${target} PRIVATE "${ARG_OUTPUT_DIR}")
        endforeach()
    endif()
endfunction()

#[=======================================================================[.rst:
srm_add_test
------------

添加SRM测试用例。

.. code-block:: cmake

    srm_add_test(
        NAME <name>
        ROOT_DIR <root_dir>
        TEST_FILE <test_file>
        [UNITY_DEPS <dep1> <dep2> ...]
    )

参数:
    NAME - 测试名称
    ROOT_DIR - SRM项目根目录
    TEST_FILE - 测试源文件
    UNITY_DEPS - 可选，Unity依赖
#]=======================================================================]
function(srm_add_test)
    cmake_parse_arguments(
        ARG
        ""
        "NAME;ROOT_DIR;TEST_FILE"
        "UNITY_DEPS"
        ${ARGN}
    )

    if(NOT ARG_NAME)
        message(FATAL_ERROR "srm_add_test: NAME is required")
    endif()

    if(NOT ARG_ROOT_DIR)
        message(FATAL_ERROR "srm_add_test: ROOT_DIR is required")
    endif()

    if(NOT ARG_TEST_FILE)
        message(FATAL_ERROR "srm_add_test: TEST_FILE is required")
    endif()

    # 输出目录（使用 _generated 后缀避免与可执行文件冲突）
    set(output_dir "${CMAKE_CURRENT_BINARY_DIR}/${ARG_NAME}_generated")

    # 生成的文件
    set(h_file "${output_dir}/srm_layout.h")
    set(c_file "${output_dir}/srm_layout.c")

    # 创建输出目录
    file(MAKE_DIRECTORY "${output_dir}")

    # 获取ROOT_DIR的绝对路径
    get_filename_component(ARG_ROOT_DIR "${ARG_ROOT_DIR}" ABSOLUTE)

    # 添加自定义命令生成SRM代码
    add_custom_command(
        OUTPUT "${h_file}" "${c_file}"
        COMMAND "${Python3_EXECUTABLE}" "${SRM_BUILD_SCRIPT}"
            --root "${ARG_ROOT_DIR}"
            --output-dir "${output_dir}"
        DEPENDS "${SRM_BUILD_SCRIPT}"
        COMMENT "Generating SRM layout for ${ARG_NAME}"
        VERBATIM
    )

    # 创建测试可执行文件
    add_executable(${ARG_NAME}
        "${ARG_TEST_FILE}"
        "${c_file}"
    )

    # 添加包含目录
    target_include_directories(${ARG_NAME} PRIVATE
        "${output_dir}"
        "${unity_SOURCE_DIR}/src"
    )

    # 链接Unity
    target_link_libraries(${ARG_NAME} PRIVATE unity)

    # 添加到CTest
    add_test(NAME ${ARG_NAME} COMMAND ${ARG_NAME})
endfunction()
