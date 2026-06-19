# SRM - Static Resource Manager 构建工具链说明

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

## 快速上手

### 1. 编写模块描述文件
在项目任意子目录下创建 `srm_module.json`，例如：
```json
{
  "module": { "name": "sensor" },
  "local_storages": [
    { "name": "sensor_data", "size": 64 }
  ],
  "items": [
    {
      "name": "temperature",
      "data_type": "measure",
      "storages": ["sensor_data"]
    }
  ]
}
```

### 2. 定义数据类型长度
编辑 `src/scripts/srm_types.json`，例如：
```json
{
  "types": [
    { "name": "measure", "length": 8 }
  ]
}
```

### 3. 运行构建流水线
```bash
python src/scripts/srm_build.py --root . --output-dir build/srm
```

## 约束规则
- module.name 全局唯一。
- local_storages 中的 name 全局唯一。
- items 中的 name 全局唯一。
- external_storages 的 source_module 必须指向存在的模块。
- 每个 item 的 storages 数组中的名称必须在本模块内已定义（本地或外部）。
- 若某个数据类型的定义要求特定字段（如 log 类型要求 format），则必须提供。

## 输出结果
- C 头文件：定义存储区大小宏、各项在各存储区中的偏移量宏。
- C 源文件：预留实现占位。

## 在其他项目中引用

### FetchContent 集成（推荐）

通过 CMake FetchContent 引入 edfx 工具链：

```cmake
include(FetchContent)
FetchContent_Declare(edfx
    GIT_REPOSITORY https://github.com/CYK-dot/srm.git
    GIT_TAG        main  # 或指定版本标签
)
FetchContent_MakeAvailable(edfx)

# 此后可使用 srm_* 函数
include(srm)
```

### CMake 接口

| 接口 | 层级 | 用途 |
|------|------|------|
| `target_link_srm_library` | 项目级 | 生成 SRM 代码并创建静态库 |
| `target_link_srm_interface` | 组件级 | 仅添加头文件路径，不链接实现 |

### 完整用法示例

**1. 准备 SRM 配置目录**

```
my_project/
├── CMakeLists.txt
└── srm/
    ├── srm_types.json
    └── module_sensor/
        └── srm_module.json
```

**2. 项目顶层 CMakeLists.txt**

```cmake
cmake_minimum_required(VERSION 3.20)
project(my_app C)

# 引入 edfx 工具链
include(FetchContent)
FetchContent_Declare(edfx
    GIT_REPOSITORY https://github.com/CYK-dot/srm.git
    GIT_TAG        main
)
FetchContent_MakeAvailable(edfx)
include(srm)

# 创建 SRM 实现库
target_link_srm_library(my_srm
    ROOT_DIR   ${CMAKE_SOURCE_DIR}/srm
    OUTPUT_DIR ${CMAKE_BINARY_DIR}/srm_generated
)

# 添加子项目
add_subdirectory(components/a_component)
add_subdirectory(components/b_component)

# 最终可执行文件
add_executable(my_app main.c)
target_link_libraries(my_app PRIVATE my_srm a_component b_component)
```

**3. 组件 CMakeLists.txt（如 b_component）**

```cmake
add_library(b_component STATIC b_component.c)

# 仅获取 SRM 头文件接口，不链接实现
target_link_srm_interface(b_component
    LINK_LIBRARY my_srm
)

# 链接 SRM 实现库（由项目顶层控制）
target_link_libraries(b_component PRIVATE my_srm)
```

**4. 组件源码中调用 SRM 函数**

```c
#include "srm_layout.h"

void read_sensor_data(void) {
    uint16_t offset = srm_get_offset(SRM_STORAGE_SENSOR_DATA_ID, SRM_ITEM_TEMPERATURE_ID);
    if (offset != 0xFFFF) {
        // 有效偏移量，读取数据
    }
}
```

### 多组件协作场景

```
项目结构：
  a_component - 定义 SRM 资源（生产者）
  b_component - 仅调用 SRM 函数（消费者）
  my_app      - 最终可执行文件
```

关键点：
- **只有项目顶层**调用 `target_link_srm_library` 创建实现库
- **所有组件**通过 `target_link_srm_interface` 获取头文件接口
- **链接权在项目层**，组件不自行决定链接哪个 SRM 库

### 接口参数

**target_link_srm_library**

| 参数 | 必填 | 说明 |
|------|------|------|
| `ROOT_DIR` | 是 | SRM 配置目录（含 `srm_types.json` 和模块子目录） |
| `OUTPUT_DIR` | 是 | 生成文件的输出目录 |

**target_link_srm_interface**

| 参数 | 必填 | 说明 |
|------|------|------|
| `LINK_LIBRARY` | 二选一 | 引用的 SRM 库目标名称（自动获取输出目录） |
| `OUTPUT_DIR` | 二选一 | 直接指定 SRM 生成文件目录 |

## 运行测试

项目有变更时，运行测试验证：

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
