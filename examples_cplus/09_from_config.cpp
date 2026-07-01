#include "pysimdata_cplus/pysimdata_cplus.h"

#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0]
                  << " <config.json> <output_dir> [format]\n";
        return 1;
    }

    std::string config_path = argv[1];
    std::string output_dir = argv[2];
    std::string fmt = (argc >= 4) ? argv[3] : "";  // 可选：显式数据格式(csv/png/tiff)

    auto gen = pysimdata_cplus::Generator::from_config_file(config_path);
    gen->generate();
    // fmt 为空时按类型选默认格式（图像 tiff/曲线 csv），与 Python 一致
    gen->save_all(output_dir, "data", false, fmt);

    std::cout << "Generated: " << output_dir << std::endl;
    return 0;
}
