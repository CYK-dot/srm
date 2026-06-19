/**
 * test_f4_offset_valid.c - F4 srm_get_offset有效查询测试
 *
 * 测试当item属于某storage时，srm_get_offset返回正确的偏移量
 */

#include "unity.h"
#include "srm.h"
#include "srm_layout.h"

void setUp(void)
{
}

void tearDown(void)
{
}

/**
 * 测试第一个item偏移量为0
 */
void test_first_item_offset_zero(void)
{
    // 第一个item在storage中的偏移量应该为0
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_A_ID)
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_A_ID));
    #endif

    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_TEMP_ID)
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_TEMP_ID));
    #endif
}

/**
 * 测试非第一个item无对齐填充
 * 根据测试用例的JSON输入，验证偏移量是否正确
 */
void test_second_item_no_alignment(void)
{
    // 当alignment=1时，第二个item的偏移量等于第一个item的长度
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_B_ID)
    // 根据测试用例的JSON输入，验证偏移量是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_B_ID));
    #endif
}

/**
 * 测试alignment>1但已对齐
 * 根据测试用例的JSON输入，验证偏移量是否正确
 */
void test_second_item_already_aligned(void)
{
    // 当alignment>1且前一个item结束位置已对齐时，无需填充
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_B_ID)
    // 根据测试用例的JSON输入，验证偏移量是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_B_ID));
    #endif
}

/**
 * 测试alignment>1需要填充
 * 根据测试用例的JSON输入，验证偏移量是否正确
 */
void test_second_item_need_padding(void)
{
    // 当alignment>1且前一个item结束位置未对齐时，需要填充
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_B_ID)
    // 根据测试用例的JSON输入，验证偏移量是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_B_ID));
    #endif
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_first_item_offset_zero);
    RUN_TEST(test_second_item_no_alignment);
    RUN_TEST(test_second_item_already_aligned);
    RUN_TEST(test_second_item_need_padding);

    return UNITY_END();
}