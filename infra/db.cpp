#include "builder_impl.hpp"
#include "loader.hpp"
#include "query_impl.hpp"

#include <filesystem>
#include <iostream>
#include <string>

static std::string norm(std::string s) { if (!s.empty() && s.back() != '/') s += '/'; return s; }

int main(int argc, char** argv) {
    std::string mode = argc > 1 ? argv[1] : "";

    if (mode == "--load" && argc == 4) {
        std::string dir = norm(argv[2]), out = norm(argv[3]);
        int n = std::distance(std::filesystem::directory_iterator(dir), std::filesystem::directory_iterator());
        #pragma omp parallel for schedule(dynamic) num_threads(50)
        for (int i = 0; i < n; ++i) { ParquetTables t = load_one(dir, i); Database* db = build(&t); dump_db(db, out, i); delete db; }
    } else if (mode == "--run" && argc == 3) {
        std::string dir = norm(argv[2]);
        std::vector<QueryRequest> requests = read_requests();
        results(dir, requests);
    } else if (mode == "--restore" && argc == 4) {
        restore_db(norm(argv[2]), norm(argv[3]));
    } else {
        std::cerr << "Usage: " << argv[0] << " --load <PARQUET_DIR> <OUTPUT_DIR> | --run <DUMP_DIR> | --restore <DUMP_DIR> <RESTORE_DIR>\n";
        return 1;
    }
    return 0;
}
