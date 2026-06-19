/**
 * test_srm_common.h - SRM测试公共头文件
 *
 * 包含Unity测试框架和SRM布局头文件
 */

#ifndef TEST_SRM_COMMON_H
#define TEST_SRM_COMMON_H

#include "unity.h"
#include "srm_layout.h"

/**
 * 测试无效storage ID
 */
static inline void test_invalid_storage_id(uint16_t invalid_id)
{
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_storage_size(invalid_id));
}

/**
 * 测试无效item ID
 */
static inline void test_invalid_item_id(uint16_t invalid_id)
{
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_item_size(invalid_id));
}

/**
 * 测试无效storage/item组合
 */
static inline void test_invalid_offset(uint16_t storage_id, uint16_t item_id)
{
    TEST_ASSERT_EQUAL_UINT16(0xFFFF, srm_get_offset(storage_id, item_id));
}

#endif /* TEST_SRM_COMMON_H */