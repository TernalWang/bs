#include "builder_impl.hpp"
#include "loader.hpp"
#include "query_impl.hpp"

#include <filesystem>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <PARQUET_DIR>\n";
        return 1;
    }
    std::string dir = argv[1];
    if (!dir.empty() && dir.back() != '/') dir += '/';
// BUILDER_BUILD

    return 0;
}
