#include "pysimdata_cplus/pysimdata_cplus.h"
#include <gtest/gtest.h>

TEST(GeneratorBase, RequiresGenerateBeforeData) {
    pysimdata_cplus::GaussianBeam gen;
    EXPECT_THROW(gen.data(), std::runtime_error);
}

TEST(GeneratorBase, DataAfterGenerate) {
    pysimdata_cplus::GaussianBeam gen(4, 4, 1.0, 1.0, 2, 2);
    gen.generate();
    EXPECT_EQ(gen.data().rows(), 4);
    EXPECT_EQ(gen.data().cols(), 4);
    EXPECT_DOUBLE_EQ(gen.data()(2, 2), 1.0);
}

TEST(GeneratorBase, SaveWithoutGenerateThrows) {
    pysimdata_cplus::GaussianBeam gen;
    EXPECT_THROW(gen.save("output/test", "data", false), std::runtime_error);
}

TEST(GeneratorBase, GenerateReturnsData) {
    pysimdata_cplus::GaussianBeam gen(8, 8, 2.0, 10.0, 4, 4);
    auto data = gen.generate();
    EXPECT_EQ(data.rows(), 8);
    EXPECT_EQ(data.cols(), 8);
    EXPECT_DOUBLE_EQ(data(4, 4), 10.0);
}

TEST(GeneratorBase, FromConfigUnknownTypeThrows) {
    pysimdata_cplus::json config = {
        {"type", "UnknownType"},
        {"params", {}}
    };
    EXPECT_THROW(pysimdata_cplus::Generator::from_config(config), std::runtime_error);
}

TEST(GeneratorBase, FromConfigMissingTypeThrows) {
    pysimdata_cplus::json config = {{"params", {}}};
    EXPECT_THROW(pysimdata_cplus::Generator::from_config(config), std::runtime_error);
}
