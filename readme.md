# SRM - Static Resource Manager

SRM 是一套用于嵌入式系统的**静态资源管理工具链**。

通过声明式 JSON 文件定义资源布局，自动生成高效的 C 语言代码，将资源的**定义、布局、访问**三个环节解耦。

## 文档

| 文档 | 内容 |
|------|------|
| [01_overview.md](docs/01_overview.md) | 功能概述、解决的问题、核心价值 |
| [02_dsl.md](docs/02_dsl.md) | 领域语言：Type、Item、Storage、Module、Layout |
| [03_usage.md](docs/03_usage.md) | 使用指南：快速开始、场景示例、API 参考 |
| [04_specs.md](docs/04_specs.md) | IPO 规格：需求编号、输入/处理/输出 |

## 快速开始

### 项目根 CMakeLists.txt

```cmake
include(srm)

# 创建 SRM 静态库（必须在 add_subdirectory 之前）
target_add_srm_library(PROJ_ROOT_DIR ${CMAKE_SOURCE_DIR})

add_subdirectory(sensor)
```

### 组件 CMakeLists.txt

```cmake
add_library(sensor STATIC imu.c)
target_link_srm_library(sensor)
```

### 组件源码

```c
#include "srm.h"
#include "srm_layout.h"

uint16_t offset = srm_get_offset(
    SRM_STORAGE_COUNTER_POOL_ID,
    SRM_ITEM_TICK_CNT_ID
);
```

## 依赖

- Python 3.8+
- `jsonschema`, `jinja2`
