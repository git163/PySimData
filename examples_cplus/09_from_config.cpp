#include "pysimdata_cplus/pysimdata_cplus.h"

#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <config.json> <output_dir>\n";
        return 1;
    }

    std::string config_path = argv[1];
    std::string output_dir = argv[2];

    auto gen = pysimdata_cplus::Generator::from_config_file(config_path);
    gen->generate();
    gen->save(output_dir, "data", false);

    std::cout << "Generated: " << output_dir << std::endl;
    return 0;
}
