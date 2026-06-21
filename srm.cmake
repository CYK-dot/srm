# srm.cmake - SRM工具链CMake模块
#
# 接口设计：
#   target_add_srm_library   - 项目级：创建SRM静态库（生成layout + 编译）
#   target_link_srm_library  - 组件级：链接SRM库（提供头文件路径）
#
# 文件职责：
#   srm.h          - 由 srm 工具链持有（src/srm.h），包含通用函数声明
#   srm_layout.h   - 由 python 脚本生成，包含项目特定的宏定义
#   srm_layout.c   - 由 python 脚本生成，包含函数实现
#
# 用法示例：
#   # 项目根 CMakeLists.txt
#   include(srm)
#   target_add_srm_library(PROJ_ROOT_DIR ${CMAKE_SOURCE_DIR})
#
#   # 子组件 CMakeLists.txt
#   target_link_srm_library(my_component)

# --- 基础配置 ---

get_filename_component(SRM_PROJECT_ROOT "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
set(SRM_SCRIPTS_DIR "${SRM_PROJECT_ROOT}/src/scripts" CACHE PATH "SRM scripts directory")

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(SRM_BUILD_SCRIPT "${SRM_SCRIPTS_DIR}/srm_build.py")
if(NOT EXISTS "${SRM_BUILD_SCRIPT}")
    message(FATAL_ERROR "SRM build script not found: ${SRM_BUILD_SCRIPT}")
endif()

# SRM 库目标名称（固定）
set(SRM_TARGET_NAME "srm")

# =============================================================================
# target_add_srm_library
# 项目级接口：创建SRM静态库（生成layout + 编译）
#
# 参数：
#   PROJ_ROOT_DIR - SRM配置目录（包含模块子目录，types定义在各模块的srm_module.json中）
#   OUTPUT_DIR    - 生成文件的输出目录（可选，默认 ${CMAKE_BINARY_DIR}/srm_generated）
#
# 行为：
#   - 生成 srm_layout.h 和 srm_layout.c
#   - 创建静态库目标 srm（libsrm.a）
#   - 设置头文件路径（srm.h 和 srm_layout.h）
# =============================================================================
function(target_add_srm_library)
    cmake_parse_arguments(ARG "" "PROJ_ROOT_DIR;OUTPUT_DIR" "" ${ARGN})

    if(NOT ARG_PROJ_ROOT_DIR)
        message(FATAL_ERROR "target_add_srm_library: PROJ_ROOT_DIR is required")
    endif()

    get_filename_component(PROJ_ROOT_DIR "${ARG_PROJ_ROOT_DIR}" ABSOLUTE)

    # OUTPUT_DIR 默认值
    if(NOT ARG_OUTPUT_DIR)
        set(ARG_OUTPUT_DIR "${CMAKE_BINARY_DIR}/srm_generated")
    endif()
    get_filename_component(OUTPUT_DIR "${ARG_OUTPUT_DIR}" ABSOLUTE)

    # 收集SRM配置文件作为构建依赖
    file(GLOB_RECURSE SRM_DEPENDS
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
        COMMENT "Generating SRM layout"
        VERBATIM
    )

    # 创建生成目标（供 add_dependencies 使用）
    add_custom_target(${SRM_TARGET_NAME}_generate DEPENDS ${GENERATED_H} ${GENERATED_C})

    # 创建静态库目标（固定名称 srm）
    add_library(${SRM_TARGET_NAME} STATIC ${GENERATED_C})
    add_dependencies(${SRM_TARGET_NAME} ${SRM_TARGET_NAME}_generate)

    # 设置头文件路径
    target_include_directories(${SRM_TARGET_NAME} PUBLIC
        $<BUILD_INTERFACE:${SRM_PROJECT_ROOT}/src>
        $<BUILD_INTERFACE:${OUTPUT_DIR}>
    )

    # 记录 OUTPUT_DIR 供 target_link_srm_library 使用
    set_target_properties(${SRM_TARGET_NAME} PROPERTIES
        SRM_OUTPUT_DIR "${OUTPUT_DIR}"
    )
endfunction()

# =============================================================================
# target_link_srm_library
# 组件级接口：链接SRM库（提供头文件路径）
#
# 参数：
#   target - 要链接SRM的目标名称
#
# 行为：
#   - 链接 srm 静态库
#   - 添加头文件路径（srm.h 和 srm_layout.h）
#
# 独立编译模式：
#   如果 srm 目标不存在（独立编译），此函数仅添加头文件路径
#   组件需要自行提供 srm.h 和 srm_layout.h 的 mock 实现
# =============================================================================
function(target_link_srm_library target)
    if(TARGET ${SRM_TARGET_NAME})
        # 正常模式：链接 SRM 库（PUBLIC 以传播头文件路径）
        target_link_libraries(${target} PUBLIC ${SRM_TARGET_NAME})
    else()
        # 独立编译模式：仅添加头文件路径
        # 组件需要自行提供 mock 的 srm.h 和 srm_layout.h
        message(STATUS "SRM target not found, enabling独立编译 mode for ${target}")

        # 尝试查找 SRM 头文件路径
        if(EXISTS "${SRM_PROJECT_ROOT}/src/srm.h")
            target_include_directories(${target} PUBLIC
                ${SRM_PROJECT_ROOT}/src
            )
        endif()

        # srm_layout.h 需要由组件自行提供（在独立编译时）
    endif()
endfunction()
