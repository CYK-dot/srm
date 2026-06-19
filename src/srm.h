/**
 * srm.h - SRM Static Resource Manager API
 *
 * 通用函数声明，由 srm 工具链持有，不随项目生成。
 * 组件只需 #include "srm.h" 即可使用 SRM 接口。
 */
#ifndef SRM_H
#define SRM_H

#include <stdint.h>

/**
 * @brief Get the offset of an item within a specific storage.
 * @param storage_id Storage ID (e.g., SRM_STORAGE_xxx_ID)
 * @param item_id    Item ID (e.g., SRM_ITEM_xxx_ID)
 * @return Offset in bytes, or 0xFFFF if the item is not placed in that storage.
 */
uint16_t srm_get_offset(uint16_t storage_id, uint16_t item_id);

/**
 * @brief Get the total size (capacity) of a storage.
 * @param storage_id Storage ID
 * @return Size in bytes, or 0 if storage not found.
 */
uint16_t srm_get_storage_size(uint16_t storage_id);

/**
 * @brief Get the length (size) of an item.
 * @param item_id Item ID
 * @return Length in bytes, or 0 if item not found.
 */
uint16_t srm_get_item_size(uint16_t item_id);

#endif /* SRM_H */
