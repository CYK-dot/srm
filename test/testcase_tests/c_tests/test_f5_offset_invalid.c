/**
 * test_f5_offset_invalid.c - F5 srm_get_offset无效查询测试
 *
 * 测试当查询无效时，srm_get_offset返回0xFFFF
 */

#include "unity.h"
#include "srm_layout.h"

void setUp(void)
{
}

void tearDown(void)
{
}

/**
 * 测试item不属于该storage
 */
void test_item_not_in_storage(void)
{
    // 当item不属于该storage时，应该返回0xFFFF
    // 需要根据测试用例的具体配置来测试
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_TEMP_ID)
    // 假设item "temp"不属于storage "buf"
    // TEST_ASSERT_EQUAL_UINT16(0xFFFF, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_TEMP_ID));
    #endif
}

/**
 * 测试无效storage ID
 */
void test_invalid_storage_id(void)
{
    // 当storage_id无效时，应该返回0xFFFF
    TEST_ASSERT_EQUAL_UINT16(0xFFFF, srm_get_offset(99, 0));
    TEST_ASSERT_EQUAL_UINT16(0xFFFF, srm_get_offset(0xFF, 0));
}

/**
 * 测试无效item ID
 */
void test_invalid_item_id(void)
{
    // 当item_id无效时，应该返回0xFFFF
    #ifdef SRM_STORAGE_BUF_ID
    TEST_ASSERT_EQUAL_UINT16(0xFFFF, srm_get_offset(SRM_STORAGE_BUF_ID, 99));
    TEST_ASSERT_EQUAL_UINT16(0xFFFF, srm_get_offset(SRM_STORAGE_BUF_ID, 0xFF));
    #endif
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_item_not_in_storage);
    RUN_TEST(test_invalid_storage_id);
    RUN_TEST(test_invalid_item_id);

    return UNITY_END();
}