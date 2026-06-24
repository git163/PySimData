#include "pysimdata_cplus/pysimdata_cplus.h"

#include <iostream>

int main() {
    pysimdata_cplus::GaussianBeam gen;
    gen.generate();
    std::string dir = gen.save("output/gaussian_beam", "data", false);
    std::cout << "Saved to: " << dir << std::endl;
    return 0;
}
