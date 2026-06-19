/**
 * test_f6_storage_size.c - F6 srm_get_storage_size测试
 *
 * 测试srm_get_storage_size函数返回正确的size
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
 * 测试有效storage返回正确size
 */
void test_valid_storage_size(void)
{
    // 当storage_id有效时，应该返回正确的size
    #ifdef SRM_STORAGE_BUF_ID
    TEST_ASSERT_EQUAL_UINT16(64, srm_get_storage_size(SRM_STORAGE_BUF_ID));
    #endif

    #ifdef SRM_STORAGE_SENSOR_DATA_ID
    TEST_ASSERT_EQUAL_UINT16(64, srm_get_storage_size(SRM_STORAGE_SENSOR_DATA_ID));
    #endif
}

/**
 * 测试无size字段的storage返回0
 */
void test_storage_no_size_field(void)
{
    // 当storage没有size字段时，应该返回0
    #ifdef SRM_STORAGE_UNLIMITED_ID
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_storage_size(SRM_STORAGE_UNLIMITED_ID));
    #endif
}

/**
 * 测试无效storage ID返回0
 */
void test_invalid_storage_id_returns_zero(void)
{
    // 当storage_id无效时，应该返回0
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_storage_size(99));
    TEST_ASSERT_EQUAL_UINT16(0, srm_get_storage_size(0xFF));
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_valid_storage_size);
    RUN_TEST(test_storage_no_size_field);
    RUN_TEST(test_invalid_storage_id_returns_zero);

    return UNITY_END();
}