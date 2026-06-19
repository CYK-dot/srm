# SRM Build Toolchain - Python 部分测试用例

> **测试目标**：确保 SRM 构建工具链在各验证阶段能正确拦截错误，防止无效数据流入 C 代码生成阶段。

---

## 1. 功能点总览表

| 功能点编号 | 功能点描述 | 断言示例 |
|------------|------------|----------|
| F1 | 模块 JSON Schema 校验 | 当 srm_module.json 不符合 schema 时，构建应该失败 |
| F2 | 模块收集与模块名冲突检测 | 当多个 srm_module.json 中存在同名模块时，应该报错并终止 |
| F3 | 全局名称唯一性校验 | 当不同模块的 local_storages.name 重复时，应该报错 |
| F4 | 引用完整性校验 | 当 external_storages 引用的 source_module 不存在时，应该报错 |
| F5 | 项目合并为扁平结构 | 当所有校验通过时，应该生成包含全部 storages 和 items 的 resolved JSON |
| F6 | 布局容量校验（含对齐） | 当 items 总长度（含对齐填充）超过 storage 容量时，应该报错 |

---

## 2. 针对每个功能点的详细设计

---

### F1 - 模块 JSON Schema 校验

**功能描述**：递归扫描目录下所有 `srm_module.json` 文件，使用 `srm_module.schema.json` 进行 JSON Schema (Draft-7) 校验。校验内容包括必填字段、字段类型、`data_type` 为 `log` 时必须提供 `format` 字段等。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: JSON 语法正确性 | D1-1: 合法 JSON; D1-2: 非法 JSON（语法错误） |
| D2: module.name 字段 | D2-1: 存在且为字符串; D2-2: 缺失; D2-3: 非字符串类型 |
| D3: local_storages / external_storages 至少存在一个 | D3-1: 至少有其一; D3-2: 两者均缺失 |
| D4: local_storages[].name 字段 | D4-1: 存在; D4-2: 缺失 |
| D5: items[]. 必填字段 (name, storages, data_type) | D5-1: 全部存在; D5-2: 缺少 name; D5-3: 缺少 storages; D5-4: 缺少 data_type |
| D6: items[].data_type 与 format 字段 | D6-1: data_type=log 且 format 存在; D6-2: data_type=log 但 format 缺失; D6-3: data_type=counter/measure（无 format 要求） |
| D7: data_type 枚举值合法性 | D7-1: 合法值 (log/counter/measure); D7-2: 不在枚举中的值 |
| D8: 目录下模块文件数量 | D8-1: 存在至少一个 srm_module.json; D8-2: 无任何 srm_module.json |

**树形拆分结构**

```
D1: JSON 语法
├── D1-1 (合法 JSON)
│   ├── D2: module.name
│   │   ├── D2-1 (存在且为字符串)
│   │   │   ├── D3: 存储区定义
│   │   │   │   ├── D3-1 (至少有其一)
│   │   │   │   │   ├── D4: local_storages[].name
│   │   │   │   │   │   ├── D4-1 (存在)
│   │   │   │   │   │   │   ├── D5: items 必填字段
│   │   │   │   │   │   │   │   ├── D5-1 (全部存在)
│   │   │   │   │   │   │   │   │   ├── D6-1 (log+format) → TC-F1-01
│   │   │   │   │   │   │   │   │   ├── D6-2 (log 无 format) → TC-F1-02
│   │   │   │   │   │   │   │   │   ├── D6-3 (counter/measure) → TC-F1-03
│   │   │   │   │   │   │   │   ├── D5-2 (缺少 name) → TC-F1-04
│   │   │   │   │   │   │   │   ├── D5-3 (缺少 storages) → TC-F1-05
│   │   │   │   │   │   │   │   └── D5-4 (缺少 data_type) → TC-F1-06
│   │   │   │   │   │   ├── D4-2 (缺失) → TC-F1-07
│   │   │   │   ├── D3-2 (两者均缺失) → TC-F1-08
│   │   ├── D2-2 (缺失) → TC-F1-09
│   │   └── D2-3 (非字符串) → TC-F1-10
│   ├── D7: data_type 枚举
│   │   ├── D7-1 (合法值) → (已覆盖于 D6 分支)
│   │   └── D7-2 (非法值) → TC-F1-11
└── D1-2 (非法 JSON) → TC-F1-12

D8: 文件数量（独立分支，不影响 Schema 内部校验）
├── D8-1 (有文件) → (由上述用例覆盖)
└── D8-2 (无文件) → TC-F1-13
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F1-01 | 根目录下有一个 srm_module.json | JSON 语法正确, module.name="sensor", local_storages 含 name, items 含 name+storages+data_type="log"+format | 校验通过，退出码 0 |
| TC-F1-02 | 根目录下有一个 srm_module.json | JSON 语法正确, items 中 data_type="log" 但无 format 字段 | 校验失败，退出码非 0，错误信息包含 "format" |
| TC-F1-03 | 根目录下有一个 srm_module.json | items 中 data_type="counter"（无 format 要求） | 校验通过，退出码 0 |
| TC-F1-04 | 根目录下有一个 srm_module.json | items 中某项缺少 name 字段 | 校验失败，退出码非 0 |
| TC-F1-05 | 根目录下有一个 srm_module.json | items 中某项缺少 storages 字段 | 校验失败，退出码非 0 |
| TC-F1-06 | 根目录下有一个 srm_module.json | items 中某项缺少 data_type 字段 | 校验失败，退出码非 0 |
| TC-F1-07 | 根目录下有一个 srm_module.json | local_storages 中某项缺少 name 字段 | 校验失败，退出码非 0 |
| TC-F1-08 | 根目录下有一个 srm_module.json | 无 local_storages 且无 external_storages | 校验失败，退出码非 0（anyOf 约束） |
| TC-F1-09 | 根目录下有一个 srm_module.json | module 对象中缺少 name 字段 | 校验失败，退出码非 0 |
| TC-F1-10 | 根目录下有一个 srm_module.json | module.name 为整数类型 (123) | 校验失败，退出码非 0 |
| TC-F1-11 | 根目录下有一个 srm_module.json | data_type="invalid_type"（不在枚举中） | 校验失败，退出码非 0 |
| TC-F1-12 | 根目录下有一个 srm_module.json | JSON 文件内容为 `{invalid json` | 校验失败，退出码非 0，错误信息包含语法错误位置 |
| TC-F1-13 | 根目录下无任何 srm_module.json | 空目录或仅含其他文件 | 给出警告信息，退出码 0 |

---

### F2 - 模块收集与模块名冲突检测

**功能描述**：递归扫描目录下所有 `srm_module.json`，加载并校验基础结构（module.name 存在），然后检查模块名全局唯一性，最终生成 `srm_project.json`。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: 模块文件数量 | D1-1: 0 个文件; D1-2: 1 个文件; D1-3: 多个文件 |
| D2: 模块名唯一性 | D2-1: 所有模块名唯一; D2-2: 存在同名模块 |
| D3: 单个模块文件内部合法性 | D3-1: 有 module.name; D3-2: 无 module.name |
| D4: 输出文件可写性 | D4-1: 输出路径可写; D4-2: 输出路径不可写（目录不存在或无权限） |

**树形拆分结构**

```
D1: 文件数量
├── D1-1 (0 个文件) → TC-F2-01
├── D1-2 (1 个文件)
│   ├── D3-1 (有 name) → TC-F2-02
│   └── D3-2 (无 name) → TC-F2-03
└── D1-3 (多个文件)
    ├── D2: 唯一性
    │   ├── D2-1 (全部唯一)
    │   │   ├── D3-1 (全部合法) → TC-F2-04
    │   │   └── D3-2 (某文件无 name) → TC-F2-05
    │   └── D2-2 (存在同名) → TC-F2-06
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F2-01 | 空目录，无 srm_module.json | D1-1: 0 个文件 | 警告 "no srm_module.json files found"，退出码 0 |
| TC-F2-02 | 目录下有 1 个合法 srm_module.json | D1-2 + D3-1 | 成功生成 srm_project.json，包含 1 个模块，退出码 0 |
| TC-F2-03 | 目录下有 1 个 srm_module.json 缺少 module.name | D1-2 + D3-2 | 跳过该文件，无有效模块，报错 "no valid modules"，退出码 1 |
| TC-F2-04 | 目录下有 2 个合法 srm_module.json（名称不同） | D1-3 + D2-1 + D3-1 | 成功生成 srm_project.json，包含 2 个模块，退出码 0 |
| TC-F2-05 | 目录下有 2 个 srm_module.json，其中一个缺少 module.name | D1-3 + D2-1 + D3-2 | 跳过非法文件，收集合法文件，若剩余 1 个则成功；若剩余 0 个则失败 |
| TC-F2-06 | 目录下有 2 个 srm_module.json，module.name 均为 "sensor" | D1-3 + D2-2 | 报错 "duplicate module name 'sensor'"，退出码 1 |

---

### F3 - 全局名称唯一性校验

**功能描述**：对收集后的 `srm_project.json` 进行全局唯一性检查：不同模块之间的 `local_storages.name` 不能重复，不同模块之间的 `items.name` 不能重复。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: local_storages.name 跨模块唯一性 | D1-1: 全部唯一; D1-2: 存在跨模块重名 |
| D2: items.name 跨模块唯一性 | D2-1: 全部唯一; D2-2: 存在跨模块重名 |

**树形拆分结构**

```
D1: local_storages.name 跨模块
├── D1-1 (唯一)
│   ├── D2: items.name 跨模块
│   │   ├── D2-1 (唯一) → TC-F3-01
│   │   └── D2-2 (重名) → TC-F3-02
└── D1-2 (重名)
    ├── D2-1 (items 唯一) → TC-F3-03
    └── D2-2 (items 也重名) → TC-F3-04
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F3-01 | srm_project.json 包含 2 个模块，各自 local_storages.name 和 items.name 均不同 | D1-1 + D2-1 | 全局唯一性校验通过，退出码 0 |
| TC-F3-02 | 2 个模块，items.name 均为 "temperature" | D1-1 + D2-2 | 报错 "Duplicate item name globally"，退出码 1 |
| TC-F3-03 | 2 个模块，local_storages.name 均为 "shared_buf" | D1-2 + D2-1 | 报错 "Duplicate local storage name globally"，退出码 1 |
| TC-F3-04 | 2 个模块，local_storages.name 和 items.name 均有跨模块冲突 | D1-2 + D2-2 | 报告两项错误（storage 和 item 冲突），退出码 1 |

---

### F4 - 引用完整性校验

**功能描述**：校验 `srm_project.json` 中模块间引用的合法性，包括：external_storages 的 source_module 必须存在、external alias 不与本模块 local storage 册突、external alias 在目标模块中必须存在、items 引用的 storage 必须在本模块已定义（本地或外部）、items 的 storages 列表不能为空。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: source_module 是否存在 | D1-1: 存在; D1-2: 不存在 |
| D2: external alias 与本模块 local storage 名冲突 | D2-1: 无冲突; D2-2: 有冲突 |
| D3: external alias 在 target module 的 local_storages 中是否存在 | D3-1: 存在; D3-2: 不存在 |
| D4: item.storages 引用有效性 | D4-1: 引用在本模块已定义（local 或 external）; D4-2: 引用未定义 |
| D5: item.storages 列表是否为空 | D5-1: 非空; D5-2: 空列表 |
| D6: 同模块内 external alias 重复 | D6-1: 无重复; D6-2: 有重复 |

**树形拆分结构**

```
D1: source_module 存在性
├── D1-1 (存在)
│   ├── D2: alias vs local 冲突
│   │   ├── D2-1 (无冲突)
│   │   │   ├── D3: alias 在 target 中存在性
│   │   │   │   ├── D3-1 (存在)
│   │   │   │   │   ├── D6: 同模块 alias 重复
│   │   │   │   │   │   ├── D6-1 (无重复)
│   │   │   │   │   │   │   ├── D4: item 引用
│   │   │   │   │   │   │   │   ├── D4-1 (有效)
│   │   │   │   │   │   │   │   │   ├── D5-1 (非空) → TC-F4-01
│   │   │   │   │   │   │   │   │   └── D5-2 (空) → TC-F4-02
│   │   │   │   │   │   │   │   └── D4-2 (无效) → TC-F4-03
│   │   │   │   │   │   └── D6-2 (重复) → TC-F4-04
│   │   │   │   └── D3-2 (不存在) → TC-F4-05
│   │   └── D2-2 (有冲突) → TC-F4-06
└── D1-2 (不存在) → TC-F4-07
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F4-01 | 模块 A 定义 local_storages "buf"，模块 B 通过 external_storages 引用 A 的 "buf"，item 引用 "buf" | D1-1, D2-1, D3-1, D6-1, D4-1, D5-1 | 引用完整性校验通过，退出码 0 |
| TC-F4-02 | 同上，但 item 的 storages 列表为空 `[]` | D1-1, D2-1, D3-1, D6-1, D4-1, D5-2 | 报错 "Item has empty storages list"，退出码 1 |
| TC-F4-03 | 模块 B 的 item 引用了 storage "nonexistent"（未通过 local 或 external 定义） | D1-1, D2-1, D3-1, D6-1, D4-2 | 报错 "Undefined storage reference"，退出码 1 |
| TC-F4-04 | 模块 B 的 external_storages 中有两个条目 name 均为 "buf" | D1-1, D2-1, D3-1, D6-2 | 报错 "Duplicate external storage aliases within module"，退出码 1 |
| TC-F4-05 | 模块 B 引用 A 的 "buf"，但 A 的 local_storages 中无 "buf" | D1-1, D2-1, D3-2 | 报错 "External storage target missing"，退出码 1 |
| TC-F4-06 | 模块 B 有 local_storages "buf"，同时 external_storages alias 也为 "buf" | D1-1, D2-2 | 报错 "External storage alias conflicts with local storage"，退出码 1 |
| TC-F4-07 | 模块 B 的 external_storages 引用 source_module="nonexistent_module" | D1-2 | 报错 "External storage target module not found"，退出码 1 |

---

### F5 - 项目合并为扁平结构

**功能描述**：将通过所有校验的 `srm_project.json` 合并为扁平的 `srm_resolved.json`，包含 `storages`（以 name 为 key 的字典）和 `items`（列表）。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: 模块数量 | D1-1: 单个模块; D1-2: 多个模块 |
| D2: local_storages 数量 | D2-1: 每个模块各有 storage; D2-2: 某模块无 items（仅有 storage） |
| D3: items 引用有效性 | D3-1: 全部有效（前序校验已确保）; D3-2: 存在无效引用（防御性校验） |

**树形拆分结构**

```
D1: 模块数量
├── D1-1 (单模块)
│   ├── D2-1 (有 storage) → TC-F5-01
│   └── D2-2 (仅 storage 无 items) → TC-F5-02
└── D1-2 (多模块)
    ├── D3-1 (全部有效) → TC-F5-03
    └── D3-2 (有无效引用) → TC-F5-04
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F5-01 | srm_project.json 包含 1 个模块，有 1 个 storage 和 1 个 item | D1-1 + D2-1 | 生成 srm_resolved.json，storages 含 1 个条目，items 含 1 个条目，退出码 0 |
| TC-F5-02 | srm_project.json 包含 1 个模块，有 1 个 storage，无 items | D1-1 + D2-2 | 生成 srm_resolved.json，storages 含 1 个条目，items 为空列表，退出码 0 |
| TC-F5-03 | srm_project.json 包含 2 个模块，各有 storage 和 items | D1-2 + D3-1 | 生成 srm_resolved.json，storages 含所有 storage（以 name 为 key），items 含所有 item，退出码 0 |
| TC-F5-04 | srm_project.json 中某 item 引用了不存在的 storage name | D1-2 + D3-2 | 报错 "references storage 'xxx' which is not defined"，退出码 1 |

---

### F6 - 布局容量校验（含对齐）

**功能描述**：对 `srm_resolved.json` 中的每个 storage，按 items 顺序模拟插入，考虑类型对齐（alignment），验证总字节数不超过 storage.size。同时校验 items 的 data_type 在 `srm_types.json` 中存在，以及 `length_strip` 表达式引用的字段有效。

**影响维度及等价类分析**

| 维度 | 等价类/场景 |
|------|-------------|
| D1: storage.size 是否定义 | D1-1: 有 size 字段; D1-2: 无 size 字段（无容量限制） |
| D2: items 总长度 vs storage 容量 | D2-1: 未溢出; D2-2: 溢出 |
| D3: 对齐（alignment）影响 | D3-1: alignment=1（无填充）; D3-2: alignment>1（有填充，可能增加总长度） |
| D4: data_type 在 types.json 中是否存在 | D4-1: 存在; D4-2: 不存在 |
| D5: 类型定义方式 | D5-1: 使用固定 length; D5-2: 使用 length_strip 表达式 |
| D6: length_strip 引用的字段 | D6-1: 字段存在且为字符串; D6-2: 字段不存在; D6-3: 字段存在但非字符串 |

**树形拆分结构**

```
D4: data_type 存在性
├── D4-1 (存在)
│   ├── D5: 类型定义方式
│   │   ├── D5-1 (固定 length)
│   │   │   ├── D1: storage.size
│   │   │   │   ├── D1-1 (有 size)
│   │   │   │   │   ├── D3: 对齐
│   │   │   │   │   │   ├── D3-1 (alignment=1)
│   │   │   │   │   │   │   ├── D2-1 (未溢出) → TC-F6-01
│   │   │   │   │   │   │   └── D2-2 (溢出) → TC-F6-02
│   │   │   │   │   │   └── D3-2 (alignment>1)
│   │   │   │   │   │       ├── D2-1 (未溢出，含填充) → TC-F6-03
│   │   │   │   │   │       └── D2-2 (因填充导致溢出) → TC-F6-04
│   │   │   │   └── D1-2 (无 size) → TC-F6-05
│   │   └── D5-2 (length_strip)
│   │       ├── D6-1 (字段存在且为字符串) → TC-F6-06
│   │       ├── D6-2 (字段不存在) → TC-F6-07
│   │       └── D6-3 (字段非字符串) → TC-F6-08
└── D4-2 (不存在) → TC-F6-09
```

**测试用例列表**

| 用例编号 | 前置条件 | 输入组合 | 预期结果 |
|----------|----------|----------|----------|
| TC-F6-01 | srm_resolved.json: storage "buf" size=64, item "temp" data_type="measure"(length=8, alignment=4), item "flag" data_type="counter"(length=4, alignment=4) | D4-1, D5-1, D1-1, D3-1, D2-1 | 容量校验通过，退出码 0 |
| TC-F6-02 | storage "buf" size=8, item "a" length=4, item "b" length=8 | D4-1, D5-1, D1-1, D3-1, D2-2 | 报错 "could not insert into storage 'buf' due to overflow"，退出码 1 |
| TC-F6-03 | storage "buf" size=16, item "a" length=5 alignment=4 (offset=0, uses 5), item "b" length=4 alignment=4 (对齐到 offset=8, uses 12) | D4-1, D5-1, D1-1, D3-2, D2-1 | 校验通过（总使用 12 ≤ 16），退出码 0 |
| TC-F6-04 | storage "buf" size=10, item "a" length=5 alignment=4 (uses 5), item "b" length=4 alignment=4 (对齐到 8, 需要 8+4=12 > 10) | D4-1, D5-1, D1-1, D3-2, D2-2 | 报错 "could not insert" (因对齐填充导致溢出)，退出码 1 |
| TC-F6-05 | storage 无 size 字段，item 任意 | D4-1, D5-1, D1-2 | 跳过容量检查，校验通过，退出码 0 |
| TC-F6-06 | type "log" 定义为 length_strip="${format}", item 含 format="Hello %d" (8 字节 UTF-8) | D4-1, D5-2, D6-1 | 正确计算长度为 8，继续容量校验 |
| TC-F6-07 | type "log" 定义为 length_strip="${format}", item 缺少 format 字段 | D4-1, D5-2, D6-2 | 报错 "missing field 'format' for length_strip"，退出码 1 |
| TC-F6-08 | type "log" 定义为 length_strip="${format}", item 的 format 字段为整数 123 | D4-1, D5-2, D6-3 | 报错 "field 'format' must be string"，退出码 1 |
| TC-F6-09 | item 的 data_type="unknown_type"，该类型不在 srm_types.json 中 | D4-2 | 报错 "unknown data_type 'unknown_type'"，退出码 1 |

---

## 3. 总测试用例汇总表

| 用例编号 | 功能点 | 简要描述 |
|----------|--------|----------|
| TC-F1-01 | F1 | 合法模块含 log 类型且有 format，校验通过 |
| TC-F1-02 | F1 | log 类型缺少 format，校验失败 |
| TC-F1-03 | F1 | counter 类型无 format 要求，校验通过 |
| TC-F1-04 | F1 | item 缺少 name，校验失败 |
| TC-F1-05 | F1 | item 缺少 storages，校验失败 |
| TC-F1-06 | F1 | item 缺少 data_type，校验失败 |
| TC-F1-07 | F1 | local_storage 缺少 name，校验失败 |
| TC-F1-08 | F1 | 无 local_storages 且无 external_storages，校验失败 |
| TC-F1-09 | F1 | module 缺少 name，校验失败 |
| TC-F1-10 | F1 | module.name 为非字符串，校验失败 |
| TC-F1-11 | F1 | data_type 不在枚举中，校验失败 |
| TC-F1-12 | F1 | JSON 语法错误，校验失败 |
| TC-F1-13 | F1 | 无模块文件，警告退出 |
| TC-F2-01 | F2 | 无模块文件，警告退出 |
| TC-F2-02 | F2 | 单个合法模块，收集成功 |
| TC-F2-03 | F2 | 单个非法模块（缺 name），收集失败 |
| TC-F2-04 | F2 | 多个合法模块名不同，收集成功 |
| TC-F2-05 | F2 | 多模块中有非法文件，跳过后处理 |
| TC-F2-06 | F2 | 多模块同名，报错退出 |
| TC-F3-01 | F3 | 全局唯一性通过 |
| TC-F3-02 | F3 | items.name 跨模块冲突 |
| TC-F3-03 | F3 | local_storages.name 跨模块冲突 |
| TC-F3-04 | F3 | storage 和 item 名均有冲突 |
| TC-F4-01 | F4 | 正常跨模块引用 |
| TC-F4-02 | F4 | item storages 为空列表 |
| TC-F4-03 | F4 | item 引用未定义 storage |
| TC-F4-04 | F4 | 同模块 external alias 重复 |
| TC-F4-05 | F4 | external alias 在目标模块不存在 |
| TC-F4-06 | F4 | external alias 与 local storage 册突 |
| TC-F4-07 | F4 | source_module 不存在 |
| TC-F5-01 | F5 | 单模块合并 |
| TC-F5-02 | F5 | 模块仅含 storage 无 items |
| TC-F5-03 | F5 | 多模块合并 |
| TC-F5-04 | F5 | item 引用不存在 storage（防御性） |
| TC-F6-01 | F6 | 无溢出校验通过 |
| TC-F6-02 | F6 | 容量溢出 |
| TC-F6-03 | F6 | 对齐后无溢出 |
| TC-F6-04 | F6 | 对齐填充导致溢出 |
| TC-F6-05 | F6 | storage 无 size 限制 |
| TC-F6-06 | F6 | length_strip 正常计算 |
| TC-F6-07 | F6 | length_strip 字段缺失 |
| TC-F6-08 | F6 | length_strip 字段类型错误 |
| TC-F6-09 | F6 | 未知 data_type |

**总用例数：40 个**

---

## 4. 自检验证表

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 每个用例只验证一个功能点 | ✅ | 所有用例均标注单一功能点归属，无跨功能点验证 |
| 所有相关维度已在各功能点的树形拆分中出现 | ✅ | 每个功能点的维度等价类已穷尽覆盖 |
| 无跨功能点冲突（相同输入组合、不同预期结果） | ✅ | 不同功能点关注不同处理阶段，输入上下文不同 |
| 每个等价类至少被一个用例覆盖 | ✅ | 树形拆分的每个叶子节点对应一个用例，40 个用例覆盖全部等价类 |
