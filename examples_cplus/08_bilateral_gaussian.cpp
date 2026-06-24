#include "pysimdata_cplus/pysimdata_cplus.h"

#include <iostream>

int main() {
    pysimdata_cplus::BilateralGaussian gen;
    gen.generate();
    std::string dir = gen.save("output/bilateral_gaussian", "data", false);
    std::cout << "Saved to: " << dir << std::endl;
    return 0;
}
