/**
 * test_f10_srm_interface.c - F10 SRM接口分离测试
 *
 * 测试 target_link_srm_library + target_link_srm_interface 的两层接口：
 * 1. 项目级：使用 target_link_srm_library 创建实现库
 * 2. 组件级：使用 target_link_srm_interface 仅获取头文件接口
 *
 * 验证组件可以仅通过头文件接口调用SRM函数，而实现由项目级库提供。
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
 * 测试通过接口调用srm_get_offset
 * 此测试验证组件仅通过头文件接口即可调用SRM函数
 */
void test_interface_get_offset(void)
{
    // C-TC-F4-01 配置：storage "buf" (size=64), item "temp" (type=measure, length=8)
    // item "temp" 在 storage "buf" 中的偏移量应为 0
    #if defined(SRM_STORAGE_BUF_ID) && defined(SRM_ITEM_TEMP_ID)
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_offset(SRM_STORAGE_BUF_ID, SRM_ITEM_TEMP_ID));
    #endif
}

/**
 * 测试通过接口调用srm_get_storage_size
 */
void test_interface_get_storage_size(void)
{
    // C-TC-F4-01 配置：storage "buf" (size=64)
    #if defined(SRM_STORAGE_BUF_ID)
    TEST_ASSERT_EQUAL_UINT16(64, srm_get_storage_size(SRM_STORAGE_BUF_ID));
    #endif
}

/**
 * 测试通过接口调用srm_get_item_size
 */
void test_interface_get_item_size(void)
{
    // C-TC-F4-01 配置：item "temp" (type=measure, length=8)
    #if defined(SRM_ITEM_TEMP_ID)
    TEST_ASSERT_EQUAL_UINT16(8, srm_get_item_size(SRM_ITEM_TEMP_ID));
    #endif
}

/**
 * 测试无效查询的返回值
 */
void test_interface_invalid_queries(void)
{
    // 无效storage ID应返回0
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_storage_size(99));

    // 无效item ID应返回0
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_item_size(99));

    // 无效组合应返回0xFFFF
    #if defined(SRM_STORAGE_BUF_ID)
    TEST_ASSERT_EQUAL_UINT16(0xFFFF, srm_get_offset(SRM_STORAGE_BUF_ID, 99));
    #endif
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_interface_get_offset);
    RUN_TEST(test_interface_get_storage_size);
    RUN_TEST(test_interface_get_item_size);
    RUN_TEST(test_interface_invalid_queries);

    return UNITY_END();
}
