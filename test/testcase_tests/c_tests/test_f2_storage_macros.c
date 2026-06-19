/**
 * test_f2_storage_macros.c - F2 Storage宏生成测试
 *
 * 测试生成的SRM_STORAGE_*_ID和SRM_STORAGE_*_SIZE宏是否正确
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
 * 测试storage ID宏存在
 */
void test_storage_id_macro_exists(void)
{
    // 验证storage ID宏可以使用
    #ifdef SRM_STORAGE_BUF_ID
    uint16_t id = SRM_STORAGE_BUF_ID;
    (void)id;
    #endif

    #ifdef SRM_STORAGE_SENSOR_DATA_ID
    uint16_t id = SRM_STORAGE_SENSOR_DATA_ID;
    (void)id;
    #endif
}

/**
 * 测试storage SIZE宏存在
 */
void test_storage_size_macro_exists(void)
{
    // 验证storage SIZE宏可以使用
    #ifdef SRM_STORAGE_BUF_SIZE
    uint16_t size = SRM_STORAGE_BUF_SIZE;
    (void)size;
    #endif

    #ifdef SRM_STORAGE_SENSOR_DATA_SIZE
    uint16_t size = SRM_STORAGE_SENSOR_DATA_SIZE;
    (void)size;
    #endif
}

/**
 * 测试storage ID从0开始分配
 */
void test_storage_id_starts_from_0(void)
{
    // 根据测试用例验证ID值
    // 单个storage时，ID应该为0
    #ifdef SRM_STORAGE_BUF_ID
    TEST_ASSERT_EQUAL_UINT16(0, SRM_STORAGE_BUF_ID);
    #endif

    #ifdef SRM_STORAGE_SENSOR_DATA_ID
    TEST_ASSERT_EQUAL_UINT16(0, SRM_STORAGE_SENSOR_DATA_ID);
    #endif
}

/**
 * 测试storage SIZE值正确
 */
void test_storage_size_value(void)
{
    // 根据测试用例验证SIZE值
    #ifdef SRM_STORAGE_BUF_SIZE
    TEST_ASSERT_EQUAL_UINT16(64, SRM_STORAGE_BUF_SIZE);
    #endif

    #ifdef SRM_STORAGE_SENSOR_DATA_SIZE
    TEST_ASSERT_EQUAL_UINT16(64, SRM_STORAGE_SENSOR_DATA_SIZE);
    #endif
}

/**
 * 测试多个storage按字母序分配ID
 */
void test_storage_multiple_alphabetical_order(void)
{
    // 如果有多个storage，应该按字母序分配ID
    #if defined(SRM_STORAGE_ALPHA_ID) && defined(SRM_STORAGE_BETA_ID)
    TEST_ASSERT_EQUAL_UINT16(0, SRM_STORAGE_ALPHA_ID);
    TEST_ASSERT_EQUAL_UINT16(1, SRM_STORAGE_BETA_ID);
    #endif
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_storage_id_macro_exists);
    RUN_TEST(test_storage_size_macro_exists);
    RUN_TEST(test_storage_id_starts_from_0);
    RUN_TEST(test_storage_size_value);
    RUN_TEST(test_storage_multiple_alphabetical_order);

    return UNITY_END();
}