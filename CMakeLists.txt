cmake_minimum_required(VERSION 3.16)
project(pysimdata_cplus VERSION 0.1.0 LANGUAGES CXX)

# C++17 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 默认 ReleaseWithDebInfo，保留调试信息
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE RelWithDebInfo)
endif()

# 本地第三方库路径
set(THIRD_PARTY_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party)

# Eigen
set(EIGEN3_INCLUDE_DIR ${THIRD_PARTY_DIR}/eigen)
if(NOT EXISTS ${EIGEN3_INCLUDE_DIR}/Eigen/Core)
    message(FATAL_ERROR "Eigen not found. Please run: bash scripts/fetch_deps.sh")
endif()

# nlohmann/json
set(NLOHMANN_JSON_INCLUDE_DIR ${THIRD_PARTY_DIR}/json/single_include)
if(NOT EXISTS ${NLOHMANN_JSON_INCLUDE_DIR}/nlohmann/json.hpp)
    message(FATAL_ERROR "nlohmann/json not found. Please run: bash scripts/fetch_deps.sh")
endif()

# GoogleTest
set(GTEST_ROOT ${THIRD_PARTY_DIR}/googletest)
if(NOT EXISTS ${GTEST_ROOT}/CMakeLists.txt)
    message(FATAL_ERROR "GoogleTest not found. Please run: bash scripts/fetch_deps.sh")
endif()

# OpenCV
find_package(OpenCV REQUIRED)

# 公共头文件路径
set(PUBLIC_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include)

# 核心库
add_library(pysimdata_cplus STATIC)

target_sources(pysimdata_cplus
    PRIVATE
        src/pysimdata_cplus/core/generator.cpp
        src/pysimdata_cplus/core/config.cpp
        src/pysimdata_cplus/io/csv_io.cpp
        src/pysimdata_cplus/io/image_io.cpp
        src/pysimdata_cplus/generators/gaussian_beam.cpp
        src/pysimdata_cplus/generators/bilateral_gaussian.cpp
        src/pysimdata_cplus/generators/exponential_decay.cpp
        src/pysimdata_cplus/generators/gaussian_grid.cpp
        src/pysimdata_cplus/generators/function_curve.cpp
        src/pysimdata_cplus/generators/erf_curve.cpp
        src/pysimdata_cplus/generators/tanh_curve.cpp
        src/pysimdata_cplus/generators/cosh_curve.cpp
)

target_include_directories(pysimdata_cplus
    PUBLIC
        ${PUBLIC_INCLUDE_DIR}
        ${EIGEN3_INCLUDE_DIR}
        ${NLOHMANN_JSON_INCLUDE_DIR}
    PRIVATE
        ${OpenCV_INCLUDE_DIRS}
)

target_link_libraries(pysimdata_cplus
    PUBLIC
        ${OpenCV_LIBS}
)

# 示例
add_subdirectory(examples_cplus)

# 测试
enable_testing()
add_subdirectory(${GTEST_ROOT})
add_subdirectory(tests_pysimdata_cplus)
