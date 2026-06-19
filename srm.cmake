# srm.cmake - SRM工具链CMake模块
#
# 两层接口设计：
#   target_link_srm_library   - 项目级：生成SRM代码，将.c注入可执行文件
#   target_link_srm_interface - 组件级：暴露 srm.h 和 srm_layout.h 头文件路径
#
# 文件职责：
#   srm.h          - 由 srm 工具链持有（src/srm.h），包含通用函数声明
#   srm_layout.h   - 由 python 脚本生成，包含项目特定的宏定义
#   srm.c          - 由 python 脚本生成，包含函数实现
#
# 用法示例：
#   include(srm)
#
#   # 项目级：将SRM实现注入可执行文件
#   add_executable(my_app main.c)
#   target_link_srm_library(my_app
#       PROJ_ROOT_DIR ${CMAKE_SOURCE_DIR}
#   )
#
#   # 组件级：获取srm.h和srm_layout.h头文件路径
#   target_link_srm_interface(b_component)

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
# 项目级接口：生成SRM代码，将.c注入可执行文件
#
# 参数：
#   TARGET_NAME   - 可执行文件目标名称（必须已通过 add_executable 定义）
#   PROJ_ROOT_DIR - SRM配置目录（包含srm_types.json和模块子目录）
#   OUTPUT_DIR    - 生成文件的输出目录（可选，默认 ${CMAKE_BINARY_DIR}/srm_generated）
#
# 行为：
#   - 生成 srm_layout.h 和 srm.c
#   - 将 srm.c 通过 target_sources 注入到目标可执行文件
#   - 将 srm_layout.h 所在目录添加到目标的包含路径
#   - 设置全局属性 SRM_LAYOUT_HEADER_DIR 供 target_link_srm_interface 读取
# =============================================================================
function(target_link_srm_library TARGET_NAME)
    cmake_parse_arguments(ARG "" "PROJ_ROOT_DIR;OUTPUT_DIR" "" ${ARGN})

    if(NOT ARG_PROJ_ROOT_DIR)
        message(FATAL_ERROR "target_link_srm_library: PROJ_ROOT_DIR is required")
    endif()
    if(NOT TARGET ${TARGET_NAME})
        message(FATAL_ERROR "target_link_srm_library: Target '${TARGET_NAME}' does not exist. Create it with add_executable first.")
    endif()

    get_filename_component(PROJ_ROOT_DIR "${ARG_PROJ_ROOT_DIR}" ABSOLUTE)

    # OUTPUT_DIR 默认值
    if(NOT ARG_OUTPUT_DIR)
        set(ARG_OUTPUT_DIR "${CMAKE_BINARY_DIR}/srm_generated")
    endif()
    get_filename_component(OUTPUT_DIR "${ARG_OUTPUT_DIR}" ABSOLUTE)

    # 收集SRM配置文件作为构建依赖
    file(GLOB_RECURSE SRM_DEPENDS
        "${PROJ_ROOT_DIR}/srm_types.json"
        "${PROJ_ROOT_DIR}/*/srm_module.json"
        "${PROJ_ROOT_DIR}/*/*/srm_module.json"
    )

    list(LENGTH SRM_DEPENDS DEPENDS_COUNT)
    if(DEPENDS_COUNT EQUAL 0)
        message(WARNING "No SRM config found in ${PROJ_ROOT_DIR}")
    endif()

    set(GENERATED_H "${OUTPUT_DIR}/srm_layout.h")
    set(GENERATED_C "${OUTPUT_DIR}/srm_layout.c")

    # 代码生成命令
    add_custom_command(
        OUTPUT ${GENERATED_H} ${GENERATED_C}
        COMMAND ${Python3_EXECUTABLE} "${SRM_BUILD_SCRIPT}"
            --root "${PROJ_ROOT_DIR}"
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

    add_custom_target(${TARGET_NAME}_srm_generate DEPENDS ${GENERATED_H} ${GENERATED_C})

    # 将 srm.c 注入到可执行文件目标
    target_sources(${TARGET_NAME} PRIVATE ${GENERATED_C})
    # 添加 srm_layout.h 所在目录（生成产物目录）
    target_include_directories(${TARGET_NAME} PRIVATE ${OUTPUT_DIR})
    add_dependencies(${TARGET_NAME} ${TARGET_NAME}_srm_generate)

    # 设置全局属性，供 target_link_srm_interface 读取 srm_layout.h 路径
    set_property(GLOBAL PROPERTY SRM_LAYOUT_HEADER_DIR "${OUTPUT_DIR}")
endfunction()

# =============================================================================
# target_link_srm_interface
# 组件级接口：暴露 srm.h 和 srm_layout.h 头文件路径，不耦合任何库目标
#
# 参数：
#   TARGET_NAME - 需要使用SRM接口的组件目标名称
#
# 行为：
#   - 将 srm.h 所在目录（${SRM_PROJECT_ROOT}/src）添加到目标的包含路径
#   - 将 srm_layout.h 所在目录（由 target_link_srm_library 设置的全局属性）添加到目标的包含路径
#   - 组件可 #include "srm.h" 和 #include "srm_layout.h" 使用SRM接口
#   - 组件不链接任何实现库，实现由项目级 target_link_srm_library 注入
# =============================================================================
function(target_link_srm_interface TARGET_NAME)
    if(NOT TARGET ${TARGET_NAME})
        message(FATAL_ERROR "target_link_srm_interface: Target '${TARGET_NAME}' does not exist")
    endif()

    # 暴露 srm.h 路径（通用函数声明）
    target_include_directories(${TARGET_NAME} PRIVATE "${SRM_PROJECT_ROOT}/src")

    # 暴露 srm_layout.h 路径（项目特定宏定义，由 target_link_srm_library 生成）
    get_property(SRM_LAYOUT_HEADER_DIR GLOBAL PROPERTY SRM_LAYOUT_HEADER_DIR)
    if(SRM_LAYOUT_HEADER_DIR)
        target_include_directories(${TARGET_NAME} PRIVATE "${SRM_LAYOUT_HEADER_DIR}")
    endif()
endfunction()

# =============================================================================
# srm_add_test
# 内部函数：添加SRM测试用例（自包含，独立于上述两层接口）
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
        "${SRM_PROJECT_ROOT}/src"     # srm.h
        "${output_dir}"               # srm_layout.h
        "${unity_SOURCE_DIR}/src"
    )

    target_link_libraries(${ARG_NAME} PRIVATE unity)
    add_test(NAME ${ARG_NAME} COMMAND ${ARG_NAME})
endfunction()
