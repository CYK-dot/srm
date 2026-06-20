/**
 * test_f13_offset_readonly.c - F9 srm_get_offset 兼容性测试
 *
 * 测试场景：
 * TC-F9-01: readonly storage + 属于该 storage 的 item → 返回正确偏移值
 * TC-F9-02: readwrite storage + 属于该 storage 的 item → 返回正确偏移值（向后兼容）
 * TC-F9-03: readonly storage + 不属于该 storage 的 item → 返回 0xFFFF
 */

#include "unity.h"
#include "srm.h"
#include "srm_layout.h"

void setUp(void) {}
void tearDown(void) {}

void test_tc_f9_01_offset_readonly_valid(void)
{
    /* TC-F9-01: readonly storage + 属于该 storage 的 item → 返回正确偏移值 */
#if defined(SRM_STORAGE_READONLY_STORAGE_ID) && defined(SRM_ITEM_TEST_ITEM_ID)
    uint16_t offset = srm_get_offset(SRM_STORAGE_READONLY_STORAGE_ID, SRM_ITEM_TEST_ITEM_ID);
    /* 第一个 item 的偏移量应为 0 */
    TEST_ASSERT_EQUAL_UINT16(0, offset);
#endif
}

void test_tc_f9_02_offset_readwrite_compatible(void)
{
    /* TC-F9-02: readwrite storage + 属于该 storage 的 item → 返回正确偏移值 */
#if defined(SRM_STORAGE_READWRITE_STORAGE_ID) && defined(SRM_ITEM_TEST_ITEM_ID)
    uint16_t offset = srm_get_offset(SRM_STORAGE_READWRITE_STORAGE_ID, SRM_ITEM_TEST_ITEM_ID);
    /* 第一个 item 的偏移量应为 0 */
    TEST_ASSERT_EQUAL_UINT16(0, offset);
#endif
}

void test_tc_f9_03_offset_readonly_item_not_in_storage(void)
{
    /* TC-F9-03: readonly storage + 不属于该 storage 的 item → 返回 0xFFFF */
#if defined(SRM_STORAGE_READONLY_STORAGE_ID)
    uint16_t offset = srm_get_offset(SRM_STORAGE_READONLY_STORAGE_ID, 99);
    TEST_ASSERT_EQUAL_UINT16(0xFFFF, offset);
#endif
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_tc_f9_01_offset_readonly_valid);
    RUN_TEST(test_tc_f9_02_offset_readwrite_compatible);
    RUN_TEST(test_tc_f9_03_offset_readonly_item_not_in_storage);
    return UNITY_END();
}
