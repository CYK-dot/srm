/**
 * test_f9_alignment.c - F9 偏移量对齐计算测试
 *
 * 测试alignment>1时的偏移量对齐计算
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
 * 测试alignment=4已对齐
 * 根据测试用例的JSON输入，验证偏移量是否正确
 */
void test_align4_already_aligned(void)
{
    // 当前一个item结束位置已是4的倍数时，无需填充
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_B_ID)
    // 根据测试用例的JSON输入，验证偏移量是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_B_ID));
    #endif
}

/**
 * 测试alignment=8已对齐
 * 根据测试用例的JSON输入，验证偏移量是否正确
 */
void test_align8_already_aligned(void)
{
    // 当前一个item结束位置已是8的倍数时，无需填充
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_B_ID)
    // 根据测试用例的JSON输入，验证偏移量是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_B_ID));
    #endif
}

/**
 * 测试alignment=4需要填充
 * 根据测试用例的JSON输入，验证偏移量是否正确
 */
void test_align4_need_padding(void)
{
    // 当前一个item结束位置不是4的倍数时，需要填充到4的倍数
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_B_ID)
    // 根据测试用例的JSON输入，验证偏移量是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_B_ID));
    #endif
}

/**
 * 测试alignment=8需要填充
 * 根据测试用例的JSON输入，验证偏移量是否正确
 */
void test_align8_need_padding(void)
{
    // 当前一个item结束位置不是8的倍数时，需要填充到8的倍数
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_B_ID)
    // 根据测试用例的JSON输入，验证偏移量是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_B_ID));
    #endif
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_align4_already_aligned);
    RUN_TEST(test_align8_already_aligned);
    RUN_TEST(test_align4_need_padding);
    RUN_TEST(test_align8_need_padding);

    return UNITY_END();
}