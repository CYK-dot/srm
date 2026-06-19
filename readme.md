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

或手动执行各步骤：
```bash
cd src/scripts
python srm_module_verify.py . --schema srm_module.schema.json
python srm_module_collect.py . -o build/srm/collected.json
python srm_project_verify.py build/srm/collected.json
python srm_project_merge.py build/srm/collected.json -o build/srm/merged.json
python srm_layout_verify.py --resolved build/srm/merged.json --types srm_types.json
python srm_layout_generate.py --resolved build/srm/merged.json --types srm_types.json --output build/srm/srm_layout --template srm_layout_generate.jinja2
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

推荐通过 CMake FetchContent 引用：

```cmake
include(FetchContent)
FetchContent_Declare(
    edfx
    GIT_REPOSITORY https://github.com/CYK-dot/srm.git
)
FetchContent_MakeAvailable(edfx)

# 使用 add_srm_library 创建静态库
add_srm_library(my_srm
    CONFIG_DIR ${CMAKE_CURRENT_SOURCE_DIR}/srm
    OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/srm_generated
)
target_link_libraries(your_target PRIVATE my_srm)
```

`CONFIG_DIR` 目录结构：
```
srm/
├── srm_types.json
├── module_a/
│   └── srm_module.json
└── module_b/
    └── srm_module.json
```

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
