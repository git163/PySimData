#include "pysimdata_cplus/pysimdata_cplus.h"

#include <iostream>

int main() {
    pysimdata_cplus::ExponentialDecay gen;
    gen.generate();
    std::string dir = gen.save("output/exponential_decay", "data", false);
    std::cout << "Saved to: " << dir << std::endl;
    return 0;
}
