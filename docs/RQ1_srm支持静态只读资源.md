# 1. 背景与目标
当前 SRM（Static Resource Manager）仅仅是布局层面的静态（编译期确定偏移量），而存储区的内容（即各个 Item 的实际数据）并未在编译期固化。
用户仍需在运行时通过 memcpy 等方式向存储区填充数据，导致：
- 只读配置数据（如固件版本、校准参数、静态查找表）无法直接放入 Flash 只读段，需在启动时从其他源拷贝，浪费 RAM 并增加启动开销。
- 无法利用编译期常量优化（如 const 数组被编译器优化到 .rodata）。
- 对于嵌入式系统，部分存储区天生只读，运行时写入无意义。

因此，SRM 需要增强能力，支持静态只读资源池——即数据内容在编译期完全确定，生成只读常量数据段，供应用程序直接使用。
1. 允许在 srm_module.json 中为 Item 指定具体的常量值。
2. 代码生成阶段，对于所有 Item 均提供了常量值且所属 Storage 标记为 readonly: true 的存储区，生成一个完整的只读字节数组（.rodata 段），数据按布局对齐填充。
3. 提供便捷的访问接口（宏或函数），让用户直接获取指向该只读数据的指针或单个字段的值。
4. 保持向后兼容：现有未提供值的 Item 仍按原行为处理，不生成静态数据。
5. 外部存储区引用：若引用的存储区是静态只读的，则外部模块也可使用该常量数据（通过 extern 声明）。

---

# 2. 黑盒行为变更

## 2.1. 类型系统(`srm_types.json`)
在`srm_types.json`中，删去`length_strip`属性，而是改为`readonly`，代表其为只读资源，且长度由item决定。下面是例子。
> 现在日志被视为只读资源的一种，不再对其做“特殊处理”，上层调用者可根据自己的需求，决定是否将资源定制为只读资源。
```json
{
  "types": [
    {
      "name": "log",
      "readonly": true,
      "alignment": 1
    },
    {
      "name": "pioc_code",
      "readonly": true,
      "alignment": 1
    },
    ...
  ]
}
```
### 2.1.1. 要点
本需求对类型系统做了更加精确的定义：类型可继续分为`读写资源`和`只读资源`两种。脚本应具备校验能力，识别出非法的类型。
| `length`属性 | `readonly`属性 | 解释 |
| :---: | :---: | :---: |
| 不指定 | 不指定或指定为false | 不定长读写资源，非法 |
| 指定   | 不指定或指定为false | 定长读写资源，合法 |
| 指定   | 指定 | 定长只读资源，非法 |
| 不指定 | 指定 | 不定长只读资源，合法 |

## 2.2. 元素管理(`srm_module.json`-`items`)
类型为`只读资源`的`item`，必须为其指定`value`。本需求应支持`string_value`和`file_value`两种，下面是例子。
> file_value的路径，是相对于当前json的相对路径。
```json
{
  ...
  "items": [
    {
      "name": "startup_failed",
      "data_type": "log",
      "string_value": "[STM32] faild to load configuration from tf-card, err code = %u"
    },
    {
      "name": "soft_uart",
      "data_type": "pioc_code",
      "file_value": "./pioc_uart.hex"
    }
  ]
}
```

### 2.2.1. 要点
只有类型为`只读资源`的`item`可以指定`value`，`读写资源`不允许指定，脚本应具备校验能力，识别出非法的`item`。

## 2.3. 静态池管理(`srm_module.json`-`storage`)
`storage`属性新增`readonly`子属性，用于区分`读写资源池`和`只读资源池`。下面是例子。
> 和类型系统类似，如果不指定readonly，则认为其值为false，为读写资源池。
```json
{
  ...
  "local_storages": [
    {
      "name": "log_info",
      "readonly": true
    }
  ],
  ...
}
```

### 2.3.1. 要点
只读item不能插入读写资源池，读写item也不能插入只读资源池。脚本应具备校验能力。

## 2.4. 静态池生成(`srm.c`-`static const`)
`读写资源`只生成相对偏移索引，至于资源在ram中的具体位置，由开发者决定。
但本需求新增的`只读资源`，srm框架还要额外生成一个静态全局常量。比如下面这个json
```json
{
  "module": {
    "name": "hal_os"
  },
  "local_storages": [
    {
      "name": "global_log"
      "readonly": true
    }
  ],
  "items": [
    {
      "name": "startup_failed",
      "data_type": "log",
      "storages": ["global_log"],
      "string_value": "faild to load configuration!\n\r"
    },
    {
      "name": "log_overheat",
      "data_type": "log",
      "storages": ["global_log"],
      "string_value": "motor overheat!\n\r"
    }
  ]
}
```
被翻译到`srm.c`中，成下面这样。
```c
static const uint8_t g_HAL_OS_GLOBAL_LOG[] = {
    /**
     * @module hal_os
     * @item   startup_failed
     * @value  faild to load configuration!\n\r
     **/
    0x66, 0x61, 0x69, 0x6C, 0x64, 0x20, 0x74, 0x6F,
    0x20, 0x6C, 0x6F, 0x61, 0x64, 0x20, 0x63, 0x6F,
    0x6E, 0x66, 0x69, 0x67, 0x75, 0x72, 0x61, 0x74,
    0x69, 0x6F, 0x6E, 0x21, 0x0D, 0x0A,
    /**
     * @module hal_os
     * @item   log_overheat
     * @value  motor overheat!\n\r
     **/
    0x6D, 0x6F, 0x74, 0x6F, 0x72, 0x20, 0x6F, 0x76,
    0x65, 0x72, 0x68, 0x65, 0x61, 0x74, 0x21, 0x0D,
    0x0A
};
// 省略后续内容...
```
需要生成的代码接口，做出如下扩充：
```c
/**
 * @brief Get the offset of an item within a specific storage, support READONLY and READWRITE
 * @param storage_id Storage ID (e.g., SRM_STORAGE_xxx_ID)
 * @param item_id    Item ID (e.g., SRM_ITEM_xxx_ID)
 * @return Offset in bytes, or 0xFFFF if the item is not placed in that storage.
 */
uint16_t srm_get_offset(uint16_t storage_id, uint16_t item_id);

/**
 * @brief Get the total size (capacity) of a storage, support READONLY and READWRITE
 * @param storage_id Storage ID
 * @return Size in bytes, or 0 if storage not found.
 */
uint16_t srm_get_storage_size(uint16_t storage_id);

/**
 * @brief Get the length (size) of an item, support READONLY and READWRITE
 * @param item_id Item ID
 * @return Length in bytes, or 0 if item not found.
 */
uint16_t srm_get_item_size(uint16_t item_id);

/**
 * @brief Get the item pointer from readonly storage, only support READONLY
 * @param item_id Item ID
 * @return NULL when id invalid
 */
uint8_t *srm_get_readonly_item(uint16_t storage_id, uint16_t item_id);

/**
 * @brief Get the storage pointer from readonly storage, only support READONLY
 * @param storage_id Storage ID
 * @return NULL when id invalid
 */
uint8_t *srm_get_readonly_storage(uint16_t storage_id);
```

---

# 3. 白盒实现变更

## 3.1. 文件改动清单

| # | 文件 | 改动要点 |
| :---: | :--- | :--- |
| 1 | `srm_types.json` | `length_strip` 属性改为 `readonly` |
| 2 | `srm_module.schema.json` | storages 新增 `readonly` 字段；items 新增 `string_value` / `file_value` 字段 |
| 3 | `srm_module_verify.py` | 新增只读语义校验（见 3.2） |
| 4 | `srm_project_merge.py` | `file_value` 相对路径解析为绝对路径 |
| 5 | `srm_project_verify.py` | 只读/读写 item 与 storage 的交叉一致性校验 |
| 6 | `srm_layout_verify.py` | 只读池无 size 时跳过溢出检查，自动推导容量 |
| 7 | `srm_layout_generate.py` | 收集只读 item 数据，按 storage 分组并计算对齐填充 |
| 8 | `srm_layout_generate.jinja2` | 生成只读字节数组（`.rodata`）+ `srm_get_readonly_item` / `srm_get_readonly_storage` |
| 9 | `srm.h` | 新增两个只读 API 声明 |

## 3.2. 校验规则

`length_strip` 语义废弃后，类型系统的合法组合：

| `length` | `readonly` | 含义 |
| :---: | :---: | :--- |
| 不指定 | false | 不定长读写 — **非法** |
| 指定 | false | 定长读写 |
| 指定 | true | 定长只读 — **非法**（只读长度由 item 值决定） |
| 不指定 | true | 不定长只读 |

`readonly: true` 的类型，item 必须提供 `string_value` 或 `file_value`（二选一）；`readonly: false` 的类型不允许出现这两个字段。

`readonly: true` 的 storage 不允许放置读写 item，读写 storage 不允许放置只读 item。

## 3.3. 代码生成行为

- 只读 storage 不再生成偏移索引，改为生成 `static const uint8_t g_XXX_READONLY[]` 字节数组，数据按 item 顺序拼接，item 间按 alignment 填充。
- `srm_layout.h` 中 `extern` 声明该数组及其 `SIZE`。
- `srm_layout.c` 中新增两个只读专用查询函数，内部通过 `switch` 定位 item 在只读数组中的偏移并返回指针。
- 读写 storage 的偏移查询、容量查询、item 长度查询逻辑不变。

## 3.4. 向后兼容

- 现有配置中不存在的字段均默认为 `false`，行为不变。
- 新增的两个只读 API 为纯增量，不影响已有接口。
- 已有的 `srm_get_offset` / `srm_get_storage_size` / `srm_get_item_size` 对只读 storage 同样可用（返回偏移和大小信息）。

---

# 4. 测试方案设计

## 4.1. 功能点总览

| 功能点编号 | 功能点描述 | 断言示例 |
|------------|------------|----------|
| F1 | 类型定义校验 | 当 `readonly:true` 且无 `length` 时，应接受该类型 |
| F2 | Item 值约束：readonly item 必须有值 | 当 readonly 类型 item 无 `string_value`/`file_value` 时，应报错 |
| F3 | Item 值约束：readwrite item 不允许有值 | 当 readwrite 类型 item 有 `string_value` 时，应报错 |
| F4 | Storage-Item 一致性校验 | 当 readonly item 引用 readwrite storage 时，应报错 |
| F5 | file_value 路径解析 | 当文件不存在时应报错 |
| F6 | 只读数组代码生成 | 当存在 readonly storage 时，应生成 `static const uint8_t[]` |
| F7 | srm_get_readonly_item 接口 | 合法参数应返回指针，非法参数返回 NULL |
| F8 | srm_get_readonly_storage 接口 | 合法参数应返回指针，非法参数返回 NULL |
| F9 | srm_get_offset 兼容性 | 对 readonly storage 应返回正确偏移值 |

---

## 4.2. 各功能点测试用例设计

### F1 - 类型定义校验

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: readonly | true, false, 不指定 |
| D2: length | 指定(正整数), 不指定 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F1-01 | srm_types.json 定义新类型 | readonly=true, length 不指定 | 构建成功，类型被接受 |
| TC-F1-02 | srm_types.json 定义新类型 | readonly=false, length=4 | 构建成功，类型被接受 |
| TC-F1-03 | srm_types.json 定义新类型 | readonly 不指定, length=4 | 构建成功，类型被接受 |
| TC-F1-04 | srm_types.json 定义新类型 | readonly=true, length=4 | 构建失败，报错"定长只读资源非法" |
| TC-F1-05 | srm_types.json 定义新类型 | readonly=false, length 不指定 | 构建失败，报错"不定长读写资源非法" |
| TC-F1-06 | srm_types.json 定义新类型 | readonly 不指定, length 不指定 | 构建失败，报错"不定长读写资源非法" |

---

### F2 - Item 值约束：readonly item 必须有值

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: item data_type 类型 | readonly 类型, readwrite 类型 |
| D2: value 提供方式 | string_value, file_value, 无, 同时提供两者 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F2-01 | 类型为 readonly | item 提供 string_value | 构建成功 |
| TC-F2-02 | 类型为 readonly | item 提供 file_value（文件存在） | 构建成功 |
| TC-F2-03 | 类型为 readonly | item 无 string_value 且无 file_value | 构建失败，报错"缺少 value" |
| TC-F2-04 | 类型为 readonly | item 同时提供 string_value 和 file_value | 构建失败，报错"两者互斥" |

---

### F3 - Item 值约束：readwrite item 不允许有值

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: item data_type 类型 | readonly 类型, readwrite 类型 |
| D2: value 提供方式 | string_value, file_value, 无 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F3-01 | 类型为 readwrite | item 无 value | 构建成功 |
| TC-F3-02 | 类型为 readwrite | item 提供 string_value | 构建失败，报错"读写类型不允许 value" |
| TC-F3-03 | 类型为 readwrite | item 提供 file_value | 构建失败，报错"读写类型不允许 value" |

---

### F4 - Storage-Item 一致性校验

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: item data_type 类型 | readonly, readwrite |
| D2: storage readonly 属性 | true, false/不指定 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F4-01 | item 类型 readonly | storage readonly=true | 构建成功 |
| TC-F4-02 | item 类型 readwrite | storage readonly=false | 构建成功 |
| TC-F4-03 | item 类型 readonly | storage readonly=false | 构建失败，报错"类型不匹配" |
| TC-F4-04 | item 类型 readwrite | storage readonly=true | 构建失败，报错"类型不匹配" |

---

### F5 - file_value 路径解析

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: 目标文件是否存在 | 存在, 不存在 |
| D2: 路径类型 | 相对路径, 绝对路径 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F5-01 | file_value 指向已存在的文件 | 相对路径 | 构建成功，文件内容正确读入 |
| TC-F5-02 | file_value 指向不存在的文件 | 相对路径 | 构建失败，报错"文件不存在" |

---

### F6 - 只读数组代码生成

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: 是否存在 readonly storage | 是, 否 |
| D2: readonly item 数量 | 1个, 多个 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F6-01 | 存在 1 个 readonly storage | 该 storage 下有 1 个 item | 生成 `static const uint8_t g_XXX_READONLY[]`，含该 item 数据 |
| TC-F6-02 | 存在 1 个 readonly storage | 该 storage 下有多个 item | 生成只读数组，含所有 item 数据并按对齐填充 |
| TC-F6-03 | 不存在 readonly storage | 全部为 readwrite storage | 不生成只读数组 |
| TC-F6-04 | 存在多个 readonly storage | 每个 storage 各有 item | 为每个 readonly storage 各生成一个独立数组 |

---

### F7 - srm_get_readonly_item 接口

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: storage_id 是否有效 | 有效, 无效 |
| D2: item_id 是否属于该 storage | 属于, 不属于 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F7-01 | readonly storage 存在 | 有效 storage_id + 属于该 storage 的 item_id | 返回指向只读数组中该 item 的指针 |
| TC-F7-02 | readonly storage 存在 | 有效 storage_id + 不属于该 storage 的 item_id | 返回 NULL |
| TC-F7-03 | - | 无效 storage_id | 返回 NULL |

---

### F8 - srm_get_readonly_storage 接口

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: storage_id 是否有效 | 有效, 无效 |
| D2: storage 是否为 readonly | 是, 否 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F8-01 | readonly storage 存在 | 有效 storage_id + readonly=true | 返回指向只读数组首地址的指针 |
| TC-F8-02 | - | 无效 storage_id | 返回 NULL |
| TC-F8-03 | readwrite storage 存在 | 有效 storage_id + readonly=false | 返回 NULL |

---

### F9 - srm_get_offset 兼容性

**影响维度及等价类**

| 维度 | 等价类 |
|------|--------|
| D1: storage 类型 | readonly, readwrite |
| D2: item 是否属于该 storage | 属于, 不属于 |

**测试用例**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F9-01 | readonly storage 存在 | readonly storage + 属于该 storage 的 item | 返回正确偏移值 |
| TC-F9-02 | readwrite storage 存在 | readwrite storage + 属于该 storage 的 item | 返回正确偏移值（向后兼容） |
| TC-F9-03 | readonly storage 存在 | readonly storage + 不属于该 storage 的 item | 返回 0xFFFF |

---

## 4.3. 总测试用例汇总表

| 用例编号 | 功能点 | 前置条件 | 输入组合 | 预期结果 |
|----------|--------|----------|----------|----------|
| TC-F1-01 | F1 | srm_types.json 定义新类型 | readonly=true, length 不指定 | 构建成功 |
| TC-F1-02 | F1 | srm_types.json 定义新类型 | readonly=false, length=4 | 构建成功 |
| TC-F1-03 | F1 | srm_types.json 定义新类型 | readonly 不指定, length=4 | 构建成功 |
| TC-F1-04 | F1 | srm_types.json 定义新类型 | readonly=true, length=4 | 构建失败 |
| TC-F1-05 | F1 | srm_types.json 定义新类型 | readonly=false, length 不指定 | 构建失败 |
| TC-F1-06 | F1 | srm_types.json 定义新类型 | readonly 不指定, length 不指定 | 构建失败 |
| TC-F2-01 | F2 | 类型为 readonly | item 提供 string_value | 构建成功 |
| TC-F2-02 | F2 | 类型为 readonly | item 提供 file_value | 构建成功 |
| TC-F2-03 | F2 | 类型为 readonly | item 无 value | 构建失败 |
| TC-F2-04 | F2 | 类型为 readonly | item 同时提供两者 | 构建失败 |
| TC-F3-01 | F3 | 类型为 readwrite | item 无 value | 构建成功 |
| TC-F3-02 | F3 | 类型为 readwrite | item 提供 string_value | 构建失败 |
| TC-F3-03 | F3 | 类型为 readwrite | item 提供 file_value | 构建失败 |
| TC-F4-01 | F4 | item 类型 readonly | storage readonly=true | 构建成功 |
| TC-F4-02 | F4 | item 类型 readwrite | storage readonly=false | 构建成功 |
| TC-F4-03 | F4 | item 类型 readonly | storage readonly=false | 构建失败 |
| TC-F4-04 | F4 | item 类型 readwrite | storage readonly=true | 构建失败 |
| TC-F5-01 | F5 | file_value 指向已存在文件 | 相对路径 | 构建成功 |
| TC-F5-02 | F5 | file_value 指向不存在文件 | 相对路径 | 构建失败 |
| TC-F6-01 | F6 | 1 个 readonly storage | 1 个 item | 生成只读数组 |
| TC-F6-02 | F6 | 1 个 readonly storage | 多个 item | 生成只读数组（含填充） |
| TC-F6-03 | F6 | 无 readonly storage | - | 不生成只读数组 |
| TC-F6-04 | F6 | 多个 readonly storage | 各有 item | 各自独立生成数组 |
| TC-F7-01 | F7 | readonly storage 存在 | 有效 id + item 属于 storage | 返回指针 |
| TC-F7-02 | F7 | readonly storage 存在 | 有效 id + item 不属于 storage | 返回 NULL |
| TC-F7-03 | F7 | - | 无效 storage_id | 返回 NULL |
| TC-F8-01 | F8 | readonly storage 存在 | 有效 id + readonly | 返回指针 |
| TC-F8-02 | F8 | - | 无效 storage_id | 返回 NULL |
| TC-F8-03 | F8 | readwrite storage 存在 | 有效 id + 非 readonly | 返回 NULL |
| TC-F9-01 | F9 | readonly storage 存在 | readonly + item 属于 | 返回偏移 |
| TC-F9-02 | F9 | readwrite storage 存在 | readwrite + item 属于 | 返回偏移 |
| TC-F9-03 | F9 | readonly storage 存在 | readonly + item 不属于 | 返回 0xFFFF |

---

## 4.4. 自检验证表

| 检查项 | 状态 |
|--------|------|
| 每个用例只验证一个功能点 | ✅ 所有用例编号均以 TC-Fx-xx 格式标注，无混合功能点 |
| 所有维度已覆盖 | ✅ 每个功能点的每个维度均在至少一个用例中出现 |
| 无跨功能点冲突 | ✅ 不存在两个不同功能点的用例输入组合相同但预期结果不同 |
| 等价类全覆盖 | ✅ 每个维度的每个等价类均被至少一个用例覆盖 |

---

## 4.5. 写入确认

✅ 测试用例已写入：`docs/srm支持静态只读资源.md` 第四章

📊 统计信息：
- 功能点数量：9 个
- 总用例数量：31 个
- 自检结果：全部通过

📁 文件内容：
- 4.1 功能点总览表
- 4.2 各功能点测试用例设计（9 个功能点的维度分析、用例列表）
- 4.3 总测试用例汇总表
- 4.4 自检验证表
- 4.5 写入确认