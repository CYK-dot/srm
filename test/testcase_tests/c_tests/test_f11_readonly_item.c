/**
 * test_f11_readonly_item.c - F7 srm_get_readonly_item 测试
 *
 * 测试场景：
 * TC-F7-01: readonly storage 存在 + 有效 storage_id + item_id 属于该 storage → 返回指针
 * TC-F7-02: readonly storage 存在 + 有效 storage_id + item_id 不属于该 storage → 返回 NULL
 * TC-F7-03: 无效 storage_id → 返回 NULL
 */

#include "unity.h"
#include "srm.h"
#include "srm_layout.h"

void setUp(void) {}
void tearDown(void) {}

void test_tc_f7_01_readonly_item_valid(void)
{
    /* TC-F7-01: readonly storage + 属于该 storage 的 item → 返回非 NULL 指针 */
#if defined(SRM_STORAGE_READONLY_STORAGE_ID) && defined(SRM_ITEM_TEST_ITEM_ID)
    const uint8_t *ptr = srm_get_readonly_item(SRM_STORAGE_READONLY_STORAGE_ID, SRM_ITEM_TEST_ITEM_ID);
    TEST_ASSERT_NOT_NULL(ptr);
    /* 验证内容为 "hello" 的 UTF-8 编码 */
    TEST_ASSERT_EQUAL_UINT8('h', ptr[0]);
    TEST_ASSERT_EQUAL_UINT8('e', ptr[1]);
    TEST_ASSERT_EQUAL_UINT8('l', ptr[2]);
    TEST_ASSERT_EQUAL_UINT8('l', ptr[3]);
    TEST_ASSERT_EQUAL_UINT8('o', ptr[4]);
#endif
}

void test_tc_f7_02_readonly_item_invalid_item(void)
{
    /* TC-F7-02: readonly storage + 不属于该 storage 的 item → 返回 NULL */
#if defined(SRM_STORAGE_READONLY_STORAGE_ID)
    const uint8_t *ptr = srm_get_readonly_item(SRM_STORAGE_READONLY_STORAGE_ID, 99);
    TEST_ASSERT_NULL(ptr);
#endif
}

void test_tc_f7_03_readonly_item_invalid_storage(void)
{
    /* TC-F7-03: 无效 storage_id → 返回 NULL */
    const uint8_t *ptr = srm_get_readonly_item(99, 0);
    TEST_ASSERT_NULL(ptr);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_tc_f7_01_readonly_item_valid);
    RUN_TEST(test_tc_f7_02_readonly_item_invalid_item);
    RUN_TEST(test_tc_f7_03_readonly_item_invalid_storage);
    return UNITY_END();
}
