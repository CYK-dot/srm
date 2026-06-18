# srm.cmake - CMake integration for SRM (FetchContent ready)
#
# Usage:
#   include(FetchContent)
#   FetchContent_Declare(srm URL ...)
#   FetchContent_MakeAvailable(srm)
#   add_srm_library(my_srm)   # 自动扫描 ${CMAKE_CURRENT_SOURCE_DIR}/srm 作为配置根目录
#   # 或指定根目录: add_srm_library(my_srm CONFIG_DIR /path/to/config)

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

    find_package(Python3 REQUIRED)

    file(GLOB_RECURSE SRM_DEPENDS
        "${CONFIG_DIR}/srm_types.json"
        "${CONFIG_DIR}/*/srm_module.json"
        "${CONFIG_DIR}/*/*/srm_module.json"
    )

    list(LENGTH SRM_DEPENDS DEPENDS_COUNT)
    if(DEPENDS_COUNT EQUAL 0)
        message(WARNING "No SRM configuration files found in ${CONFIG_DIR}. Add srm_types.json and module subdirectories.")
    endif()

    get_filename_component(SRM_SCRIPT_DIR "${CMAKE_CURRENT_LIST_DIR}/scripts" ABSOLUTE)
    set(SRM_BUILD_PY "${SRM_SCRIPT_DIR}/srm_build.py")

    set(GENERATED_H "${OUTPUT_DIR}/srm_layout.h")
    set(GENERATED_C "${OUTPUT_DIR}/srm_layout.c")

    add_custom_command(
        OUTPUT ${GENERATED_H} ${GENERATED_C}
        COMMAND ${Python3_EXECUTABLE}
            "${SRM_BUILD_PY}"
            --root "${CONFIG_DIR}"
            --output-dir "${OUTPUT_DIR}"
        DEPENDS ${SRM_DEPENDS}
                "${SRM_BUILD_PY}"
                "${SRM_SCRIPT_DIR}/srm_module_verify.py"
                "${SRM_SCRIPT_DIR}/srm_module_collect.py"
                "${SRM_SCRIPT_DIR}/srm_project_verify.py"
                "${SRM_SCRIPT_DIR}/srm_project_merge.py"
                "${SRM_SCRIPT_DIR}/srm_layout_verify.py"
                "${SRM_SCRIPT_DIR}/srm_layout_generate.py"
                "${SRM_SCRIPT_DIR}/srm_log.py"
        COMMENT "Generating SRM layout for ${TARGET_NAME} from ${CONFIG_DIR}"
        VERBATIM
    )

    add_custom_target(${TARGET_NAME}_generate DEPENDS ${GENERATED_H} ${GENERATED_C})

    add_library(${TARGET_NAME} STATIC ${GENERATED_C})
    target_include_directories(${TARGET_NAME} PUBLIC ${OUTPUT_DIR})
    add_dependencies(${TARGET_NAME} ${TARGET_NAME}_generate)
endfunction()