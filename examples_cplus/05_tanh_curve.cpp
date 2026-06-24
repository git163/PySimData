#include "pysimdata_cplus/pysimdata_cplus.h"

#include <iostream>

int main() {
    pysimdata_cplus::TanhCurve gen;
    gen.generate();
    std::string dir = gen.save("output/tanh_curve", "data", false);
    std::cout << "Saved to: " << dir << std::endl;
    return 0;
}
