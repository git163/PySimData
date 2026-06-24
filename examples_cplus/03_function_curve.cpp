#include "pysimdata_cplus/pysimdata_cplus.h"

#include <iostream>

int main() {
    pysimdata_cplus::FunctionCurve gen(pysimdata_cplus::FunctionCurve::NameToFunc("sin"));
    gen.generate();
    std::string dir = gen.save("output/function_curve", "data", false);
    std::cout << "Saved to: " << dir << std::endl;
    return 0;
}
