include_directories(${gtest_SOURCE_DIR}/include ${gtest_SOURCE_DIR})

add_executable(pysimdata_cplus_tests
    test_generator.cpp
    test_config.cpp
    test_gaussian.cpp
    test_function.cpp
    test_io.cpp
    test_save_load.cpp
)

target_link_libraries(pysimdata_cplus_tests
    PRIVATE
        pysimdata_cplus
        gtest
        gtest_main
)

include(GoogleTest)
gtest_discover_tests(pysimdata_cplus_tests)
