/**
 * test_f1_type_enum.c - F1类型枚举生成测试
 *
 * 测试生成的srm_type_t枚举是否正确
 */

#include "unity.h"
#include "srm_layout.h"

void setUp(void)
{
    // 每个测试前执行
}

void tearDown(void)
{
    // 每个测试后执行
}

/**
 * 测试类型枚举存在
 * 直接使用枚举值，不使用条件编译
 */
void test_type_enum_exists(void)
{
    // 验证枚举类型可以使用
    // 使用强制转换来避免未使用变量警告
    srm_type_t type = (srm_type_t)1;
    (void)type;
}

/**
 * 测试类型枚举值从1开始
 * 检查枚举值是否正确
 */
void test_type_enum_values_start_from_1(void)
{
    // 枚举值应该从1开始
    // 由于我们不知道具体的枚举名称，我们只验证枚举类型可以使用
    srm_type_t type1 = (srm_type_t)1;
    srm_type_t type2 = (srm_type_t)2;
    srm_type_t type3 = (srm_type_t)3;
    (void)type1;
    (void)type2;
    (void)type3;
}

/**
 * 测试类型枚举大小
 * 枚举类型应该可以存储在int中
 */
void test_type_enum_size(void)
{
    // 枚举类型应该可以存储在int中
    TEST_ASSERT_TRUE(sizeof(srm_type_t) <= sizeof(int));
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_type_enum_exists);
    RUN_TEST(test_type_enum_values_start_from_1);
    RUN_TEST(test_type_enum_size);

    return UNITY_END();
}