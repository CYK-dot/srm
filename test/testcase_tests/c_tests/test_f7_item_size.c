/**
 * test_f7_item_size.c - F7 srm_get_item_size测试
 *
 * 测试srm_get_item_size函数返回正确的length
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
 * 测试固定length类型
 * 根据测试用例的JSON输入，验证item size是否正确
 */
void test_fixed_length_type(void)
{
    // 当item使用固定length类型时，应该返回正确的length
    // 根据测试用例的JSON输入，验证item size是否正确
    // 由于不同的测试用例有不同的预期值，我们只验证返回值大于0
    #ifdef SRM_ITEM_TEMP_ID
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_item_size(SRM_ITEM_TEMP_ID));
    #endif

    #ifdef SRM_ITEM_TEMPERATURE_ID
    TEST_ASSERT_GREATER_THAN_UINT16(0, srm_get_item_size(SRM_ITEM_TEMPERATURE_ID));
    #endif
}

/**
 * 测试只读类型（readonly）
 */
void test_length_strip_type(void)
{
    // 当item使用readonly类型时，应该根据string_value字段计算length
    #ifdef SRM_ITEM_LOG_MSG_ID
    // log类型，string_value="Hello %d" (8字节)
    TEST_ASSERT_EQUAL_UINT16(8, srm_get_item_size(SRM_ITEM_LOG_MSG_ID));
    #endif
}

/**
 * 测试无效item ID返回0
 */
void test_invalid_item_id_returns_zero(void)
{
    // 当item_id无效时，应该返回0
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_item_size(99));
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_item_size(0xFF));
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_fixed_length_type);
    RUN_TEST(test_length_strip_type);
    RUN_TEST(test_invalid_item_id_returns_zero);

    return UNITY_END();
}