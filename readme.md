# SRM - Static Resource Manager

SRM 是一套用于管理嵌入式系统中静态资源（如配置数据、共享内存布局、常量表）的构建工具链。  
它通过声明式 JSON 文件定义模块（module）、存储区（storage）和数据项（item），自动完成全局唯一性校验、容量规划、偏移量计算，并生成高效的 C 语言头/源文件。

## 核心概念

- **模块（Module）**：一个逻辑单元（如传感器驱动、通信协议栈），声明其拥有的存储区和数据项。
- **存储区（Storage）**：一段连续字节区域，具有固定容量（size，单位字节）。分为：
  - 本地存储区（local_storages）：由模块自身拥有。
  - 外部存储区引用（external_storages）：引用其他模块的本地存储区（只读）。
- **数据项（Item）**：一个具有类型的数据元素，可放入一个或多个存储区。每个项有名称（全局唯一）、数据类型（由 `srm_types.json` 定义）以及所存放的存储区列表。
- **类型系统（Types）**：定义每种数据类型的字节长度，可以是固定长度或根据某个字段动态计算（如字符串长度）。

## 依赖环境

- Python 3.8+
- 必装包：`jsonschema`, `jinja2`

## 约束规则

- module.name 全局唯一。
- local_storages 中的 name 全局唯一。
- items 中的 name 全局唯一。
- external_storages 的 source_module 必须指向存在的模块。
- 每个 item 的 storages 数组中的名称必须在本模块内已定义（本地或外部）。
- 若某个数据类型的定义要求特定字段（如 log 类型要求 format），则必须提供。

## 如何在项目中引用

### 1. 引入 srm 工具链

```cmake
include(FetchContent)
FetchContent_Declare(srm
    GIT_REPOSITORY https://github.com/CYK-dot/srm.git
)
FetchContent_MakeAvailable(srm)
include(srm)
```

### 2. CMake 接口

| 接口 | 层级 | 用途 |
|------|------|------|
| `target_link_srm_library` | 项目级 | 生成 SRM 代码，将 .c 注入可执行文件 |
| `target_link_srm_interface` | 组件级 | 暴露 srm.h 和 srm_layout.h 头文件路径 |

### 3. 文件职责

| 文件 | 来源 | 内容 |
|------|------|------|
| `srm.h` | srm 工具链持有（`src/srm.h`） | SRM接口声明（`srm_get_offset` 等） |
| `srm_layout.h` | python 脚本生成 | 项目特定的宏定义（`SRM_STORAGE_*_ID`, `SRM_ITEM_*_ID`） |
| `srm.c` | python 脚本生成 | 基于项目自动生成的SRM接口实现 |

### 4. 用法示例

**项目结构**

```
my_project/
├── CMakeLists.txt
├── srm_types.json
└── sensor/
    ├── srm_module.json
    ├── imu.c
    └── CMakeLists.txt
```

**项目顶层 CMakeLists.txt**

```cmake
cmake_minimum_required(VERSION 3.20)
project(my_app C)

include(FetchContent)
FetchContent_Declare(srm
    GIT_REPOSITORY https://github.com/CYK-dot/srm.git
)
FetchContent_MakeAvailable(srm)
include(srm)

# 项目级：生成 SRM 代码，将 .c 注入可执行文件
# 必须在 add_subdirectory 之前调用，以便全局属性 SRM_LAYOUT_HEADER_DIR 被设置
add_executable(my_app main.c)
target_link_srm_library(my_app
    PROJ_ROOT_DIR ${CMAKE_SOURCE_DIR}
)

# 组件级：组件通过 target_link_srm_interface 获取 srm.h 和 srm_layout.h 路径
add_subdirectory(sensor)

target_link_libraries(my_app PRIVATE sensor)
```

**组件 CMakeLists.txt**

```cmake
add_library(sensor STATIC imu.c)
target_link_srm_interface(sensor)
```

**组件源码**

```c
#include "srm.h"
#include "srm_layout.h"
#include <string.h>

/* 传感器数据存储区 */
static uint8_t sensor_buf[SRM_STORAGE_SENSOR_DATA_SIZE];

void sensor_write_temperature(int16_t temp) {
    uint16_t offset = srm_get_offset(SRM_STORAGE_SENSOR_DATA_ID, SRM_ITEM_TEMPERATURE_ID);
    memcpy(sensor_buf + offset, &temp, sizeof(temp));
}

int16_t sensor_read_temperature(void) {
    int16_t temp;
    uint16_t offset = srm_get_offset(SRM_STORAGE_SENSOR_DATA_ID, SRM_ITEM_TEMPERATURE_ID);
    memcpy(&temp, sensor_buf + offset, sizeof(temp));
    return temp;
}
```

### 5. 接口参数

**target_link_srm_library**

| 参数 | 必填 | 说明 |
|------|------|------|
| `TARGET_NAME` | 是 | 可执行文件目标名称（必须已通过 `add_executable` 定义） |
| `PROJ_ROOT_DIR` | 是 | SRM 配置目录（含 `srm_types.json` 和模块子目录） |
| `OUTPUT_DIR` | 否 | 生成文件的输出目录（默认 `${CMAKE_BINARY_DIR}/srm_generated`） |

**target_link_srm_interface**

| 参数 | 必填 | 说明 |
|------|------|------|
| `TARGET_NAME` | 是 | 需要使用 SRM 接口的组件目标名称 |

## 运行测试

### Python 测试

```bash
cd test/testcase_tests
pytest python_tests -v
```

### C 代码测试

```bash
cd test
mkdir -p build && cd build
cmake ..
cmake --build .
ctest -V
```

详细测试说明见 [test/README.md](test/README.md)。

## 扩展性

- 可修改 `src/scripts/srm_types.json` 增加新数据类型。
- 可自定义 Jinja2 模板以调整生成的代码风格。
- 可增加对其它语言（如 Rust）的后端支持（修改生成器即可）。
