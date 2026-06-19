# srm.cmake - SRM工具链CMake模块
#
# 两层接口设计：
#   target_link_srm_library   - 项目级：生成SRM代码并创建实现库
#   target_link_srm_interface - 组件级：仅提供头文件接口
#
# 用法示例：
#   include(srm)
#
#   # 项目级：创建实现库
#   target_link_srm_library(my_srm
#       ROOT_DIR ${CMAKE_SOURCE_DIR}/srm
#       OUTPUT_DIR ${CMAKE_BINARY_DIR}/srm_generated
#   )
#
#   # 组件级：仅获取接口
#   target_link_srm_interface(b_component LINK_LIBRARY my_srm)
#
#   # 链接
#   target_link_libraries(b_component PRIVATE my_srm)

# --- 基础配置 ---

get_filename_component(SRM_PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
set(SRM_SCRIPTS_DIR "${SRM_PROJECT_ROOT}/src/scripts" CACHE PATH "SRM scripts directory")

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(SRM_BUILD_SCRIPT "${SRM_SCRIPTS_DIR}/srm_build.py")
if(NOT EXISTS "${SRM_BUILD_SCRIPT}")
    message(FATAL_ERROR "SRM build script not found: ${SRM_BUILD_SCRIPT}")
endif()

# =============================================================================
# target_link_srm_library
# 项目级接口：生成SRM代码并创建静态库
#
# 参数：
#   ROOT_DIR   - SRM配置目录（包含srm_types.json和模块子目录）
#   OUTPUT_DIR - 生成文件的输出目录
#
# 输出：
#   创建静态库目标，设置 SRM_OUTPUT_DIR 属性供 interface 使用
# =============================================================================
function(target_link_srm_library TARGET_NAME)
    cmake_parse_arguments(ARG "" "ROOT_DIR;OUTPUT_DIR" "" ${ARGN})

    if(NOT ARG_ROOT_DIR)
        message(FATAL_ERROR "target_link_srm_library: ROOT_DIR is required")
    endif()
    if(NOT ARG_OUTPUT_DIR)
        message(FATAL_ERROR "target_link_srm_library: OUTPUT_DIR is required")
    endif()

    get_filename_component(ROOT_DIR "${ARG_ROOT_DIR}" ABSOLUTE)
    get_filename_component(OUTPUT_DIR "${ARG_OUTPUT_DIR}" ABSOLUTE)

    # 收集SRM配置文件作为构建依赖
    file(GLOB_RECURSE SRM_DEPENDS
        "${ROOT_DIR}/srm_types.json"
        "${ROOT_DIR}/*/srm_module.json"
        "${ROOT_DIR}/*/*/srm_module.json"
    )

    list(LENGTH SRM_DEPENDS DEPENDS_COUNT)
    if(DEPENDS_COUNT EQUAL 0)
        message(WARNING "No SRM config found in ${ROOT_DIR}")
    endif()

    set(GENERATED_H "${OUTPUT_DIR}/srm_layout.h")
    set(GENERATED_C "${OUTPUT_DIR}/srm_layout.c")

    # 代码生成命令
    add_custom_command(
        OUTPUT ${GENERATED_H} ${GENERATED_C}
        COMMAND ${Python3_EXECUTABLE} "${SRM_BUILD_SCRIPT}"
            --root "${ROOT_DIR}"
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
        COMMENT "Generating SRM layout for ${TARGET_NAME}"
        VERBATIM
    )

    add_custom_target(${TARGET_NAME}_generate DEPENDS ${GENERATED_H} ${GENERATED_C})

    # 创建静态库并设置包含路径
    add_library(${TARGET_NAME} STATIC ${GENERATED_C})
    target_include_directories(${TARGET_NAME} PUBLIC ${OUTPUT_DIR})
    add_dependencies(${TARGET_NAME} ${TARGET_NAME}_generate)

    # 存储OUTPUT_DIR供 target_link_srm_interface 读取
    set_target_properties(${TARGET_NAME} PROPERTIES SRM_OUTPUT_DIR "${OUTPUT_DIR}")
endfunction()

# =============================================================================
# target_link_srm_interface
# 组件级接口：仅添加头文件路径，不链接实现库
#
# 参数（二选一）：
#   LINK_LIBRARY - 引用的SRM库目标名称（自动获取OUTPUT_DIR）
#   OUTPUT_DIR   - 直接指定SRM生成文件目录
# =============================================================================
function(target_link_srm_interface TARGET_NAME)
    cmake_parse_arguments(ARG "" "LINK_LIBRARY;OUTPUT_DIR" "" ${ARGN})

    if(NOT ARG_LINK_LIBRARY AND NOT ARG_OUTPUT_DIR)
        message(FATAL_ERROR "target_link_srm_interface: LINK_LIBRARY or OUTPUT_DIR required")
    endif()
    if(ARG_LINK_LIBRARY AND ARG_OUTPUT_DIR)
        message(FATAL_ERROR "target_link_srm_interface: LINK_LIBRARY and OUTPUT_DIR are mutually exclusive")
    endif()

    if(ARG_LINK_LIBRARY)
        if(NOT TARGET ${ARG_LINK_LIBRARY})
            message(FATAL_ERROR "target_link_srm_interface: Target '${ARG_LINK_LIBRARY}' not found")
        endif()
        get_target_property(OUTPUT_DIR ${ARG_LINK_LIBRARY} SRM_OUTPUT_DIR)
        if(NOT OUTPUT_DIR)
            message(FATAL_ERROR "target_link_srm_interface: '${ARG_LINK_LIBRARY}' has no SRM_OUTPUT_DIR property")
        endif()
    else()
        get_filename_component(OUTPUT_DIR "${ARG_OUTPUT_DIR}" ABSOLUTE)
    endif()

    # 仅添加头文件目录
    target_include_directories(${TARGET_NAME} PRIVATE ${OUTPUT_DIR})
endfunction()

# =============================================================================
# srm_add_test
# 内部函数：添加SRM测试用例
#
# 参数：
#   NAME      - 测试名称
#   ROOT_DIR  - SRM项目根目录
#   TEST_FILE - 测试源文件
# =============================================================================
function(srm_add_test)
    cmake_parse_arguments(ARG "" "NAME;ROOT_DIR;TEST_FILE" "UNITY_DEPS" ${ARGN})

    if(NOT ARG_NAME)
        message(FATAL_ERROR "srm_add_test: NAME is required")
    endif()
    if(NOT ARG_ROOT_DIR)
        message(FATAL_ERROR "srm_add_test: ROOT_DIR is required")
    endif()
    if(NOT ARG_TEST_FILE)
        message(FATAL_ERROR "srm_add_test: TEST_FILE is required")
    endif()

    set(output_dir "${CMAKE_CURRENT_BINARY_DIR}/${ARG_NAME}_generated")
    set(h_file "${output_dir}/srm_layout.h")
    set(c_file "${output_dir}/srm_layout.c")

    file(MAKE_DIRECTORY "${output_dir}")
    get_filename_component(ARG_ROOT_DIR "${ARG_ROOT_DIR}" ABSOLUTE)

    add_custom_command(
        OUTPUT "${h_file}" "${c_file}"
        COMMAND "${Python3_EXECUTABLE}" "${SRM_BUILD_SCRIPT}"
            --root "${ARG_ROOT_DIR}"
            --output-dir "${output_dir}"
        DEPENDS "${SRM_BUILD_SCRIPT}"
        COMMENT "Generating SRM layout for ${ARG_NAME}"
        VERBATIM
    )

    add_executable(${ARG_NAME} "${ARG_TEST_FILE}" "${c_file}")

    target_include_directories(${ARG_NAME} PRIVATE
        "${output_dir}"
        "${unity_SOURCE_DIR}/src"
    )

    target_link_libraries(${ARG_NAME} PRIVATE unity)
    add_test(NAME ${ARG_NAME} COMMAND ${ARG_NAME})
endfunction()
