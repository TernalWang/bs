#include "builder_impl.hpp"
#include "loader.hpp"
#include "query_impl.hpp"

#include <filesystem>
#include <iostream>
#include <string>

static std::string norm(std::string s) { if (!s.empty() && s.back() != '/') s += '/'; return s; }

int main(int argc, char** argv) {
    std::filesystem::path root = std::filesystem::current_path();
    if (!std::filesystem::exists(root / "infra")) { std::cerr << "run from workspace root\n"; return 1; }
    const std::string dump_dir = (root / "parquets/final/final_dump").string() + "/";
    const std::string restore_dir = (root / "parquets/final/final_restore").string() + "/";
    std::string mode = argc > 1 ? argv[1] : "";

    if (mode == "--load" && argc == 3) {
        std::string dir = norm(argv[2]);
        int n = count_files(dir);
        #pragma omp parallel for schedule(dynamic) num_threads(10)
        for (int i = 0; i < n; ++i) { ParquetTables t = load_one(dir, i); Database* db = build(&t); dump_db(db, dump_dir, i); delete db; }
    } else if (mode == "--run" && argc == 2) {
        std::vector<QueryRequest> requests = read_requests();
        results(dump_dir, requests);
    } else if (mode == "--restore" && argc == 2) {
        restore_db(dump_dir, restore_dir);
    } else {
        std::cerr << "Usage: " << argv[0] << " --load <PARQUET_DIR> | --run | --restore\n";
        return 1;
    }
    return 0;
}
