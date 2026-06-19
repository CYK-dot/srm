# SRM C Code Generation - 测试设计文档

> **测试目标**：验证生成的 C 代码（.h/.c）是否 100% 正确反映了 JSON 输入的描述。假设输入 JSON 已通过 Python 部分的校验。

---

## 1. 功能点总览表

| 功能点编号 | 功能点描述 | 断言示例 |
|------------|------------|----------|
| F1 | 类型枚举生成 | 当 srm_types.json 定义了 counter/measure/log 类型时，.h 文件应该生成对应的 srm_type_t 枚举 |
| F2 | Storage 宏生成 | 当 resolved.json 包含 storage "sensor_data" size=64 时，.h 文件应该定义 SRM_STORAGE_SENSOR_DATA_ID 和 SRM_STORAGE_SENSOR_DATA_SIZE |
| F3 | Item 宏生成 | 当 resolved.json 包含 item "temperature" data_type="measure" 时，.h 文件应该定义 SRM_ITEM_TEMPERATURE_ID 和 SRM_ITEM_TEMPERATURE_TYPE |
| F4 | srm_get_offset 函数 - 有效查询 | 当 item 属于某 storage 时，srm_get_offset 应该返回正确的偏移量 |
| F5 | srm_get_offset 函数 - 无效查询 | 当 item 不属于某 storage 时，srm_get_offset 应该返回 0xFFFF |
| F6 | srm_get_storage_size 函数 | 当 storage_id 有效时，srm_get_storage_size 应该返回正确的 size |
| F7 | srm_get_item_size 函数 | 当 item_id 有效时，srm_get_item_size 应该返回正确的 length |
| F8 | 名称到 C 标识符转换 | 当名称含特殊字符或数字开头时，应该正确转换为合法 C 标识符 |
| F9 | 偏移量对齐计算 | 当 alignment>1 时，下一个 item 的偏移量应该向上对齐到 alignment 的倍数 |

---

## 2. 针对每个功能点的详细设计

---

### F1 - 类型枚举生成

**功能描述**：根据 `srm_types.json` 中的类型定义，在 .h 文件中生成 `srm_type_t` 枚举，每个类型分配一个从 1 开始的整数编码。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: 类型数量 | D1-1: 单个类型; D1-2: 多个类型 |
| D2: 类型名称 | D2-1: 纯字母; D2-2: 含特殊字符; D2-3: 数字开头 |

**树形拆分结构**

```
D1: 类型数量
├── D1-1 (单个类型)
│   ├── D2-1 (纯字母) → TC-F1-01
│   ├── D2-2 (含特殊字符) → TC-F1-02
│   └── D2-3 (数字开头) → TC-F1-03
└── D1-2 (多个类型)
    └── D2-1 (纯字母) → TC-F1-04
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F1-01 | srm_types.json 含 1 个类型 "counter" | D1-1 + D2-1 | .h 文件包含 `SRM_TYPE_COUNTER = 1` |
| TC-F1-02 | srm_types.json 含 1 个类型 "my-type" | D1-1 + D2-2 | .h 文件包含 `SRM_TYPE_MY_TYPE = 1`（连字符替换为下划线） |
| TC-F1-03 | srm_types.json 含 1 个类型 "3rdparty" | D1-1 + D2-3 | .h 文件包含 `SRM_TYPE__3RDPARTY = 1`（加前缀下划线） |
| TC-F1-04 | srm_types.json 含 3 个类型 "counter", "measure", "log" | D1-2 + D2-1 | .h 文件包含 `SRM_TYPE_COUNTER = 1`, `SRM_TYPE_MEASURE = 2`, `SRM_TYPE_LOG = 3` |

---

### F2 - Storage 宏生成

**功能描述**：根据 resolved.json 中的 storages，在 .h 文件中为每个 storage 生成 `_ID` 和 `_SIZE` 宏，ID 按 storage 名称字母序分配（从 0 开始）。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: storage 数量 | D1-1: 单个; D1-2: 多个 |
| D2: storage 名称特征 | D2-1: 纯字母数字; D2-2: 含特殊字符; D2-3: 数字开头 |
| D3: size 值 | D3-1: 正整数; D3-2: 无 size 字段（默认 0） |

**树形拆分结构**

```
D1: storage 数量
├── D1-1 (单个)
│   ├── D2-1 + D3-1 → TC-F2-01
│   ├── D2-2 + D3-1 → TC-F2-02
│   ├── D2-3 + D3-1 → TC-F2-03
│   └── D2-1 + D3-2 → TC-F2-04
└── D1-2 (多个)
    └── D2-1 + D3-1 → TC-F2-05
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F2-01 | resolved.json 含 storage "sensor_data" size=64 | D1-1 + D2-1 + D3-1 | .h 文件包含 `#define SRM_STORAGE_SENSOR_DATA_ID 0` 和 `#define SRM_STORAGE_SENSOR_DATA_SIZE 64` |
| TC-F2-02 | resolved.json 含 storage "my-storage" size=32 | D1-1 + D2-2 + D3-1 | .h 文件包含 `#define SRM_STORAGE_MY_STORAGE_ID 0` 和 `#define SRM_STORAGE_MY_STORAGE_SIZE 32` |
| TC-F2-03 | resolved.json 含 storage "3rdparty" size=16 | D1-1 + D2-3 + D3-1 | .h 文件包含 `#define SRM_STORAGE__3RDPARTY_ID 0` 和 `#define SRM_STORAGE__3RDPARTY_SIZE 16` |
| TC-F2-04 | resolved.json 含 storage "unlimited"（无 size 字段） | D1-1 + D2-1 + D3-2 | .h 文件包含 `#define SRM_STORAGE_UNLIMITED_ID 0` 和 `#define SRM_STORAGE_UNLIMITED_SIZE 0` |
| TC-F2-05 | resolved.json 含 storage "alpha" size=10 和 "beta" size=20 | D1-2 + D2-1 + D3-1 | .h 文件包含 `SRM_STORAGE_ALPHA_ID 0`, `SRM_STORAGE_ALPHA_SIZE 10`, `SRM_STORAGE_BETA_ID 1`, `SRM_STORAGE_BETA_SIZE 20`（按字母序分配 ID） |

---

### F3 - Item 宏生成

**功能描述**：根据 resolved.json 中的 items，在 .h 文件中为每个 item 生成 `_ID` 和 `_TYPE` 宏，ID 按 items 列表顺序分配（从 0 开始），_TYPE 为对应类型的编码。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: item 数量 | D1-1: 单个; D1-2: 多个 |
| D2: item 名称特征 | D2-1: 纯字母数字; D2-2: 含特殊字符; D2-3: 数字开头 |
| D3: data_type | D3-1: counter; D3-2: measure; D3-3: log |

**树形拆分结构**

```
D1: item 数量
├── D1-1 (单个)
│   ├── D2-1 + D3-1 → TC-F3-01
│   ├── D2-2 + D3-2 → TC-F3-02
│   ├── D2-3 + D3-3 → TC-F3-03
└── D1-2 (多个)
    └── D2-1 + D3-1/D3-2 → TC-F3-04
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F3-01 | resolved.json 含 item "temperature" data_type="counter", types 含 counter=1 | D1-1 + D2-1 + D3-1 | .h 文件包含 `#define SRM_ITEM_TEMPERATURE_ID 0` 和 `#define SRM_ITEM_TEMPERATURE_TYPE 1` |
| TC-F3-02 | resolved.json 含 item "my-item" data_type="measure", types 含 measure=2 | D1-1 + D2-2 + D3-2 | .h 文件包含 `#define SRM_ITEM_MY_ITEM_ID 0` 和 `#define SRM_ITEM_MY_ITEM_TYPE 2` |
| TC-F3-03 | resolved.json 含 item "3rdval" data_type="log", types 含 log=3 | D1-1 + D2-3 + D3-3 | .h 文件包含 `#define SRM_ITEM__3RDVAL_ID 0` 和 `#define SRM_ITEM__3RDVAL_TYPE 3` |
| TC-F3-04 | resolved.json 含 item "alpha"(counter) 和 "beta"(measure) | D1-2 + D2-1 + D3-1/D3-2 | .h 文件包含 `SRM_ITEM_ALPHA_ID 0`, `SRM_ITEM_ALPHA_TYPE 1`, `SRM_ITEM_BETA_ID 1`, `SRM_ITEM_BETA_TYPE 2`（按列表顺序分配 ID） |

---

### F4 - srm_get_offset 函数 - 有效查询

**功能描述**：当 item 属于某 storage 时，srm_get_offset(storage_id, item_id) 应该返回该 item 在该 storage 中的正确偏移量（考虑对齐）。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: storage 中的 item 位置 | D1-1: 第一个 item（偏移量=0）; D1-2: 非第一个 item |
| D2: 对齐要求 | D2-1: alignment=1（无填充）; D2-2: alignment>1（需要对齐） |
| D3: 对齐是否产生填充 | D3-1: 前一个 item 结束位置已对齐; D3-2: 前一个 item 结束位置未对齐 |

**树形拆分结构**

```
D1: item 位置
├── D1-1 (第一个 item)
│   └── D2-1 → TC-F4-01
└── D1-2 (非第一个)
    ├── D2-1 (alignment=1) → TC-F4-02
    └── D2-2 (alignment>1)
        ├── D3-1 (已对齐) → TC-F4-03
        └── D3-2 (未对齐，需填充) → TC-F4-04
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F4-01 | storage "buf" 含 item "a"(length=4, alignment=1) | D1-1 + D2-1 | `srm_get_offset(BUF_ID, A_ID)` 返回 0 |
| TC-F4-02 | storage "buf" 含 item "a"(length=4) 和 "b"(length=8), alignment=1 | D1-2 + D2-1 | `srm_get_offset(BUF_ID, B_ID)` 返回 4 |
| TC-F4-03 | storage "buf" 含 item "a"(length=4, alignment=4) 和 "b"(length=4, alignment=4) | D1-2 + D2-2 + D3-1 | `srm_get_offset(BUF_ID, B_ID)` 返回 4（4 已是 4 的倍数，无需填充） |
| TC-F4-04 | storage "buf" 含 item "a"(length=5, alignment=1) 和 "b"(length=4, alignment=4) | D1-2 + D2-2 + D3-2 | `srm_get_offset(BUF_ID, B_ID)` 返回 8（5 对齐到 8） |

---

### F5 - srm_get_offset 函数 - 无效查询

**功能描述**：当查询无效时，srm_get_offset 应该返回 0xFFFF。无效情况包括：item 不属于该 storage、storage_id 无效、item_id 无效。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: 查询有效性 | D1-1: item 不属于该 storage; D1-2: storage_id 无效; D1-3: item_id 无效 |

**树形拆分结构**

```
D1: 查询有效性
├── D1-1 (item 不属于 storage) → TC-F5-01
├── D1-2 (storage_id 无效) → TC-F5-02
└── D1-3 (item_id 无效) → TC-F5-03
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F5-01 | storage "buf" 不含 item "temp"，storage "sensor" 含 item "temp" | D1-1 | `srm_get_offset(BUF_ID, TEMP_ID)` 返回 0xFFFF |
| TC-F5-02 | 有效 storage ID 为 0,1，使用 storage_id=99 | D1-2 | `srm_get_offset(99, any_item_id)` 返回 0xFFFF |
| TC-F5-03 | 有效 item ID 为 0,1，使用 item_id=99 | D1-3 | `srm_get_offset(any_storage_id, 99)` 返回 0xFFFF |

---

### F6 - srm_get_storage_size 函数

**功能描述**：当 storage_id 有效时返回正确的 size，无效时返回 0。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: storage_id 有效性 | D1-1: 有效; D1-2: 无效 |
| D2: size 值 | D2-1: 正整数; D2-2: 无 size 字段（返回 0） |

**树形拆分结构**

```
D1: storage_id 有效性
├── D1-1 (有效)
│   ├── D2-1 (有 size) → TC-F6-01
│   └── D2-2 (无 size) → TC-F6-02
└── D1-2 (无效) → TC-F6-03
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F6-01 | storage "buf" size=64 | D1-1 + D2-1 | `srm_get_storage_size(BUF_ID)` 返回 64 |
| TC-F6-02 | storage "unlimited" 无 size 字段 | D1-1 + D2-2 | `srm_get_storage_size(UNLIMITED_ID)` 返回 0 |
| TC-F6-03 | 有效 storage ID 为 0,1，使用 storage_id=99 | D1-2 | `srm_get_storage_size(99)` 返回 0 |

---

### F7 - srm_get_item_size 函数

**功能描述**：当 item_id 有效时返回正确的 length，无效时返回 0。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: item_id 有效性 | D1-1: 有效; D1-2: 无效 |
| D2: 类型长度计算方式 | D2-1: 固定 length; D2-2: length_strip 动态计算 |

**树形拆分结构**

```
D1: item_id 有效性
├── D1-1 (有效)
│   ├── D2-1 (固定 length) → TC-F7-01
│   └── D2-2 (length_strip) → TC-F7-02
└── D1-2 (无效) → TC-F7-03
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F7-01 | item "temp" data_type="measure"(length=8) | D1-1 + D2-1 | `srm_get_item_size(TEMP_ID)` 返回 8 |
| TC-F7-02 | item "log_msg" data_type="log"(length_strip="${format}"), format="Hello %d" (8 字节) | D1-1 + D2-2 | `srm_get_item_size(LOG_MSG_ID)` 返回 8 |
| TC-F7-03 | 有效 item ID 为 0,1，使用 item_id=99 | D1-2 | `srm_get_item_size(99)` 返回 0 |

---

### F8 - 名称到 C 标识符转换

**功能描述**：将 JSON 中的名称转换为合法的 C 宏名称：替换非字母数字字符为下划线，数字开头加前缀下划线，全部大写。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: 名称字符组成 | D1-1: 纯字母数字; D1-2: 含连字符; D1-3: 含空格; D1-4: 含其他特殊字符 |
| D2: 名称首字符 | D2-1: 字母开头; D2-2: 数字开头 |

**树形拆分结构**

```
D1: 字符组成
├── D1-1 (纯字母数字)
│   ├── D2-1 (字母开头) → TC-F8-01
│   └── D2-2 (数字开头) → TC-F8-02
├── D1-2 (含连字符)
│   └── D2-1 → TC-F8-03
├── D1-3 (含空格)
│   └── D2-1 → TC-F8-04
└── D1-4 (含其他特殊字符)
    └── D2-1 → TC-F8-05
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F8-01 | storage name="sensor_data" | D1-1 + D2-1 | 宏名为 `SRM_STORAGE_SENSOR_DATA` |
| TC-F8-02 | storage name="3rdparty" | D1-1 + D2-2 | 宏名为 `SRM_STORAGE__3RDPARTY`（加前缀下划线） |
| TC-F8-03 | storage name="my-storage" | D1-2 + D2-1 | 宏名为 `SRM_STORAGE_MY_STORAGE`（连字符→下划线） |
| TC-F8-04 | storage name="my storage" | D1-3 + D2-1 | 宏名为 `SRM_STORAGE_MY_STORAGE`（空格→下划线） |
| TC-F8-05 | storage name="data@store" | D1-4 + D2-1 | 宏名为 `SRM_STORAGE_DATA_STORE`（@→下划线） |

---

### F9 - 偏移量对齐计算

**功能描述**：当 alignment>1 时，item 的偏移量必须向上对齐到 alignment 的倍数。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: 前一个 item 结束位置 | D1-1: 已是 alignment 倍数; D1-2: 不是 alignment 倍数 |
| D2: alignment 值 | D2-1: alignment=4; D2-2: alignment=8 |

**树形拆分结构**

```
D1: 前一个 item 结束位置
├── D1-1 (已对齐)
│   ├── D2-1 (alignment=4) → TC-F9-01
│   └── D2-2 (alignment=8) → TC-F9-02
└── D1-2 (未对齐)
    ├── D2-1 (alignment=4) → TC-F9-03
    └── D2-2 (alignment=8) → TC-F9-04
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F9-01 | item "a" length=4 alignment=1, item "b" alignment=4 | D1-1 + D2-1 | "b" 偏移量=4（4 是 4 的倍数，无需填充） |
| TC-F9-02 | item "a" length=8 alignment=1, item "b" alignment=8 | D1-1 + D2-2 | "b" 偏移量=8（8 是 8 的倍数，无需填充） |
| TC-F9-03 | item "a" length=5 alignment=1, item "b" alignment=4 | D1-2 + D2-1 | "b" 偏移量=8（5→8，向上对齐到 4 的倍数） |
| TC-F9-04 | item "a" length=10 alignment=1, item "b" alignment=8 | D1-2 + D2-2 | "b" 偏移量=16（10→16，向上对齐到 8 的倍数） |

---

## 3. 总测试用例汇总表

| 用例编号 | 功能点 | 简要描述 |
|----------|--------|----------|
| TC-F1-01 | F1 | 单个纯字母类型，生成正确枚举值 |
| TC-F1-02 | F1 | 类型名含连字符，替换为下划线 |
| TC-F1-03 | F1 | 类型名数字开头，加前缀下划线 |
| TC-F1-04 | F1 | 多个类型，按顺序分配枚举值 |
| TC-F2-01 | F2 | 单个 storage，生成正确 ID 和 SIZE 宏 |
| TC-F2-02 | F2 | storage 名含连字符 |
| TC-F2-03 | F2 | storage 名数字开头 |
| TC-F2-04 | F2 | storage 无 size 字段，默认 0 |
| TC-F2-05 | F2 | 多个 storage，按字母序分配 ID |
| TC-F3-01 | F3 | 单个 item，生成正确 ID 和 TYPE 宏 |
| TC-F3-02 | F3 | item 名含连字符 |
| TC-F3-03 | F3 | item 名数字开头 |
| TC-F3-04 | F3 | 多个 item，按列表顺序分配 ID |
| TC-F4-01 | F4 | 第一个 item，偏移量=0 |
| TC-F4-02 | F4 | 非第一个 item，无对齐填充 |
| TC-F4-03 | F4 | alignment>1 但已对齐，无需填充 |
| TC-F4-04 | F4 | alignment>1 且未对齐，需要填充 |
| TC-F5-01 | F5 | item 不属于该 storage，返回 0xFFFF |
| TC-F5-02 | F5 | storage_id 无效，返回 0xFFFF |
| TC-F5-03 | F5 | item_id 无效，返回 0xFFFF |
| TC-F6-01 | F6 | 有效 storage，返回正确 size |
| TC-F6-02 | F6 | storage 无 size 字段，返回 0 |
| TC-F6-03 | F6 | 无效 storage_id，返回 0 |
| TC-F7-01 | F7 | 固定 length 类型，返回正确值 |
| TC-F7-02 | F7 | length_strip 类型，返回正确值 |
| TC-F7-03 | F7 | 无效 item_id，返回 0 |
| TC-F8-01 | F8 | 纯字母数字名称 |
| TC-F8-02 | F8 | 数字开头名称 |
| TC-F8-03 | F8 | 含连字符名称 |
| TC-F8-04 | F8 | 含空格名称 |
| TC-F8-05 | F8 | 含其他特殊字符名称 |
| TC-F9-01 | F9 | 已对齐，alignment=4 |
| TC-F9-02 | F9 | 已对齐，alignment=8 |
| TC-F9-03 | F9 | 未对齐，alignment=4 |
| TC-F9-04 | F9 | 未对齐，alignment=8 |

**总用例数：35 个**

---

## 4. 自检验证表

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 每个用例只验证一个功能点 | ✅ | 所有用例均标注单一功能点归属，无跨功能点验证 |
| 所有相关维度已在各功能点的树形拆分中出现 | ✅ | 每个功能点的维度等价类已穷尽覆盖 |
| 无跨功能点冲突（相同输入组合、不同预期结果） | ✅ | 不同功能点关注不同输出方面，输入上下文不同 |
| 每个等价类至少被一个用例覆盖 | ✅ | 树形拆分的每个叶子节点对应一个用例，35 个用例覆盖全部等价类 |
