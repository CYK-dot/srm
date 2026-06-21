# SRM Specification

## Requirement ID Format

`RQ<major>.<minor>[.<sub>]`

- `major`: 功能模块编号
- `minor`: 功能点编号
- `sub`: 子项编号（可选）

---

## RQ0: 类型系统

### RQ0.F1: SRM 支持本地类型定义

SRM 支持通过 `local_types` 数组在模块中定义数据类型。

| IPO | 内容 |
|-----|------|
| **Input** | `srm_module.json` 中的 `local_types` 数组 |
| **Process** | 每个类型必须包含 `name` 字段；固定长度类型必须包含 `length` 字段（正整数）；只读类型必须包含 `readonly: true`，可省略 `length`；可选 `alignment` 字段（默认 1，必须是 2 的幂） |
| **Output** | 类型注册表，供后续存储区和数据项使用 |

### RQ0.F1b: SRM 支持外部类型引用

SRM 支持通过 `extern_types` 数组引用其他模块定义的类型。

| IPO | 内容 |
|-----|------|
| **Input** | `srm_module.json` 中的 `extern_types` 数组 |
| **Process** | 必须包含 `name` 和 `source_module` 字段；`source_module` 必须指向已定义的模块；目标模块的 `local_types` 中必须包含指定的类型 |
| **Output** | 外部类型引用注册表，合并到全局类型注册表 |

### RQ0.F2: SRM 支持类型命名校验

SRM 支持对类型名称进行唯一性和格式校验。

| IPO | 内容 |
|-----|------|
| **Input** | 类型名称字符串 |
| **Process** | 类型名称全局唯一；只允许字母、数字、下划线；不能为空 |
| **Output** | 验证通过或报错 |

---

## RQ1: 存储区

### RQ1.F1: SRM 支持本地存储区定义

SRM 支持通过 `local_storages` 数组定义模块本地拥有的存储区。

| IPO | 内容 |
|-----|------|
| **Input** | `local_storages` 数组中的存储区对象 |
| **Process** | 必须包含 `name` 字段；`name` 全局唯一；只读存储区（`readonly: true`）可省略 `size`；非只读存储区必须提供 `size`（正整数） |
| **Output** | 存储区注册表 |

### RQ1.F2: SRM 支持只读存储区生成

SRM 支持将只读存储区生成为 `const` 数组，存放在 Flash 中。

| IPO | 内容 |
|-----|------|
| **Input** | 存储区对象，`readonly: true` |
| **Process** | 存储区大小从包含的数据项自动计算；生成为 `const` 数组，存放在 Flash 中；命名格式：`g_srm_<name>_value[]` |
| **Output** | 只读存储区数组声明和定义 |

### RQ1.F3: SRM 支持禁用只读存储区

SRM 支持通过 `disabled: true` 禁用只读存储区，使其不参与代码生成。

| IPO | 内容 |
|-----|------|
| **Input** | 存储区对象，`disabled: true` |
| **Process** | 仅对 `readonly: true` 的存储区生效；禁用的存储区不生成代码；引用禁用存储区的数据项被跳过（警告） |
| **Output** | 禁用存储区不出现在生成代码中 |

### RQ1.F4: SRM 支持外部存储区引用

SRM 支持通过 `external_storages` 引用其他模块的存储区。

| IPO | 内容 |
|-----|------|
| **Input** | `external_storages` 数组中的引用对象 |
| **Process** | 必须包含 `name` 和 `source_module` 字段；`source_module` 必须指向已定义的模块；本模块可引用该存储区，但不拥有它 |
| **Output** | 外部存储区引用注册表 |

---

## RQ2: 数据项

### RQ2.F1: SRM 支持数据项定义

SRM 支持通过 `items` 数组定义存储区中的数据项。

| IPO | 内容 |
|-----|------|
| **Input** | `items` 数组中的数据项对象 |
| **Process** | 必须包含 `name`、`storages`、`data_type` 字段；`name` 全局唯一；`data_type` 必须在 `local_types` 或 `extern_types` 中定义；`storages` 数组中的每个名称必须存在于当前模块 |
| **Output** | 数据项注册表 |

### RQ2.F2: SRM 支持固定长度数据项

SRM 支持固定长度数据项的偏移计算和对齐处理。

| IPO | 内容 |
|-----|------|
| **Input** | 数据项对象，对应类型有固定 `length` |
| **Process** | 数据项长度 = 类型定义的 `length`；在存储区中按对齐要求放置 |
| **Output** | 数据项 ID、类型码、长度 |

### RQ2.F3: SRM 支持只读字符串数据项

SRM 支持将 `string_value` 生成为只读字节数组。

| IPO | 内容 |
|-----|------|
| **Input** | 数据项对象，类型为只读，提供 `string_value` |
| **Process** | 数据项长度 = `string_value` 的 UTF-8 编码字节数；内容生成为十六进制数组；注释显示原始字符串 |
| **Output** | 只读数据项的偏移、大小、字节数组 |

### RQ2.F4: SRM 支持只读文件数据项

SRM 支持将文件内容生成为只读字节数组。

| IPO | 内容 |
|-----|------|
| **Input** | 数据项对象，类型为只读，提供 `file_value` |
| **Process** | `file_value` 是相对于 `srm_module.json` 的路径；文件必须存在；数据项长度 = 文件字节数；内容生成为十六进制数组 |
| **Output** | 只读数据项的偏移、大小、字节数组 |

### RQ2.F5: SRM 支持 Doxygen 注释生成

SRM 支持将 `comments` 数组生成为 Doxygen 风格注释。

| IPO | 内容 |
|-----|------|
| **Input** | 数据项对象，`comments` 数组 |
| **Process** | `comments` 数组非空时，生成 Doxygen 风格注释；注释放在对应 `#define` 宏的上方；格式：`/** ... */` |
| **Output** | 生成代码中的注释块 |

---

## RQ3: 模块

### RQ3.F1: SRM 支持模块定义

SRM 支持通过 `srm_module.json` 定义逻辑模块。

| IPO | 内容 |
|-----|------|
| **Input** | `srm_module.json` 文件 |
| **Process** | 必须包含 `module` 对象，其中 `name` 字段必填；`module.name` 全局唯一；必须包含 `local_storages` 或 `external_storages` 至少一个 |
| **Output** | 模块注册表 |

### RQ3.F2: SRM 支持模块验证

SRM 支持对所有模块进行格式和约束验证。

| IPO | 内容 |
|-----|------|
| **Input** | 所有模块的 `srm_module.json` |
| **Process** | 验证 JSON 格式符合 schema；验证全局唯一性约束；验证存储区引用有效性；验证数据项引用有效性 |
| **Output** | 验证通过或报错 |

---

## RQ4: 生成代码

### RQ4.F1: SRM 支持头文件生成

SRM 支持生成 `srm_layout.h` 头文件。

| IPO | 内容 |
|-----|------|
| **Input** | 合并后的 resolved.json |
| **Process** | 生成 `srm_layout.h`；包含类型枚举 `srm_type_t`；包含存储区 ID 和大小宏；包含数据项 ID 和类型宏；包含只读存储区数组声明；包含只读数据项偏移和大小宏 |
| **Output** | `srm_layout.h` 文件 |

### RQ4.F2: SRM 支持源文件生成

SRM 支持生成 `srm_layout.c` 源文件。

| IPO | 内容 |
|-----|------|
| **Input** | 合并后的 resolved.json |
| **Process** | 生成 `srm_layout.c`；包含只读存储区数组定义（16 字节/行）；包含运行时查询函数实现；数组内容带注释标注每个数据项 |
| **Output** | `srm_layout.c` 文件 |

### RQ4.F3: SRM 支持运行时查询

SRM 支持运行时查询存储区和数据项信息。

| IPO | 内容 |
|-----|------|
| **Input** | 存储区 ID 和数据项 ID |
| **Process** | `srm_get_offset(storage_id, item_id)`: 返回数据项在存储区中的偏移；`srm_get_storage_size(storage_id)`: 返回存储区大小；`srm_get_item_size(item_id)`: 返回数据项大小；`srm_get_readonly_item(storage_id, item_id)`: 返回只读数据项指针；`srm_get_readonly_storage(storage_id)`: 返回只读存储区指针；未找到时返回 0xFFFF 或 NULL |
| **Output** | 偏移量、大小或指针 |

### RQ4.F4: SRM 支持命名规范

SRM 支持按照规范自动生成标识符命名。

| IPO | 内容 |
|-----|------|
| **Input** | 存储区和数据项名称 |
| **Process** | 存储区 ID: `SRM_STORAGE_<NAME>_ID`；存储区大小: `SRM_STORAGE_<NAME>_SIZE`；数据项 ID: `SRM_ITEM_<NAME>_ID`；数据项类型: `SRM_ITEM_<NAME>_TYPE`；只读数组: `g_srm_<name>_value`；只读偏移: `SRM_ITEM_<NAME>_OFFSET`；只读大小: `SRM_ITEM_<NAME>_SIZE`；`<NAME>` 转换为大写（宏）或小写（变量） |
| **Output** | 符合命名规范的标识符 |

---

## RQ5: CMake 集成

### RQ5.F1: SRM 支持项目级静态库创建

SRM 支持通过 `target_add_srm_library` 在项目根创建静态库。

| IPO | 内容 |
|-----|------|
| **Input** | 项目根目录（PROJ_ROOT_DIR） |
| **Process** | 扫描所有模块的 srm_module.json；生成 srm_layout.h 和 srm_layout.c；创建静态库目标 srm（libsrm.a）；设置头文件路径 |
| **Output** | 可链接的静态库目标 |

### RQ5.F2: SRM 支持组件级库链接

SRM 支持通过 `target_link_srm_library` 在组件级链接静态库。

| IPO | 内容 |
|-----|------|
| **Input** | 目标名称 |
| **Process** | 正常模式：链接 SRM 静态库，传播头文件路径；独立编译模式：仅添加头文件路径，组件需自行提供 mock 头文件 |
| **Output** | 组件获得 SRM 头文件和链接依赖 |

### RQ5.F3: SRM 支持自动构建顺序

SRM 支持自动处理代码生成和编译的构建顺序。

| IPO | 内容 |
|-----|------|
| **Input** | 依赖 SRM 的组件 |
| **Process** | 代码生成在编译前执行；任何链接 SRM 的组件自动获得构建顺序依赖 |
| **Output** | 正确的构建顺序 |

---

## RQ6: 约束和错误处理

### RQ6.F1: SRM 支持全局唯一性校验

SRM 支持对模块、存储区、类型、数据项名称进行全局唯一性校验。

| IPO | 内容 |
|-----|------|
| **Input** | 所有模块的存储区、类型和数据项 |
| **Process** | 模块名称全局唯一；存储区名称全局唯一；类型名称全局唯一；数据项名称全局唯一；重复时构建失败并报错 |
| **Output** | 验证通过或报错 |

### RQ6.F2: SRM 支持引用有效性校验

SRM 支持对所有引用关系进行有效性校验。

| IPO | 内容 |
|-----|------|
| **Input** | 所有引用关系 |
| **Process** | 数据项引用的存储区必须存在；外部存储区引用的模块必须存在；外部类型引用的模块和类型必须存在；引用无效时构建失败并报错 |
| **Output** | 验证通过或报错 |

### RQ6.F3: SRM 支持文件存在性校验

SRM 支持对 `file_value` 路径进行文件存在性校验。

| IPO | 内容 |
|-----|------|
| **Input** | `file_value` 路径 |
| **Process** | 文件必须存在于指定路径；文件不存在时构建失败并报错 |
| **Output** | 验证通过或报错 |
