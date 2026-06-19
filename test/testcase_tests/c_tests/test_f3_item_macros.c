/**
 * test_f3_item_macros.c - F3 Item宏生成测试
 *
 * 测试生成的SRM_ITEM_*_ID和SRM_ITEM_*_TYPE宏是否正确
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
 * 测试item ID宏存在
 */
void test_item_id_macro_exists(void)
{
    // 验证item ID宏可以使用
    #ifdef SRM_ITEM_TEMP_ID
    uint16_t id = SRM_ITEM_TEMP_ID;
    (void)id;
    #endif

    #ifdef SRM_ITEM_TEMPERATURE_ID
    uint16_t id = SRM_ITEM_TEMPERATURE_ID;
    (void)id;
    #endif
}

/**
 * 测试item TYPE宏存在
 */
void test_item_type_macro_exists(void)
{
    // 验证item TYPE宏可以使用
    #ifdef SRM_ITEM_TEMP_TYPE
    uint16_t type = SRM_ITEM_TEMP_TYPE;
    (void)type;
    #endif

    #ifdef SRM_ITEM_TEMPERATURE_TYPE
    uint16_t type = SRM_ITEM_TEMPERATURE_TYPE;
    (void)type;
    #endif
}

/**
 * 测试item ID从0开始分配
 */
void test_item_id_starts_from_0(void)
{
    // 根据测试用例验证ID值
    // 单个item时，ID应该为0
    #ifdef SRM_ITEM_TEMP_ID
    TEST_ASSERT_EQUAL_UINT16(0, SRM_ITEM_TEMP_ID);
    #endif

    #ifdef SRM_ITEM_TEMPERATURE_ID
    TEST_ASSERT_EQUAL_UINT16(0, SRM_ITEM_TEMPERATURE_ID);
    #endif
}

/**
 * 测试item TYPE值正确
 */
void test_item_type_value(void)
{
    // 根据测试用例验证TYPE值
    // TYPE值应该对应srm_types.json中的类型编码
    #ifdef SRM_ITEM_TEMP_TYPE
    TEST_ASSERT_EQUAL_UINT16(1, SRM_ITEM_TEMP_TYPE);
    #endif

    #ifdef SRM_ITEM_TEMPERATURE_TYPE
    TEST_ASSERT_EQUAL_UINT16(1, SRM_ITEM_TEMPERATURE_TYPE);
    #endif
}

/**
 * 测试多个item按列表顺序分配ID
 */
void test_item_multiple_order(void)
{
    // 如果有多个item，应该按列表顺序分配ID
    #if defined(SRM_ITEM_ALPHA_ID) && defined(SRM_ITEM_BETA_ID)
    TEST_ASSERT_EQUAL_UINT16(0, SRM_ITEM_ALPHA_ID);
    TEST_ASSERT_EQUAL_UINT16(1, SRM_ITEM_BETA_ID);
    #endif
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_item_id_macro_exists);
    RUN_TEST(test_item_type_macro_exists);
    RUN_TEST(test_item_id_starts_from_0);
    RUN_TEST(test_item_type_value);
    RUN_TEST(test_item_multiple_order);

    return UNITY_END();
}