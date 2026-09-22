#pragma once

#include <arrow/table.h>
#include <filesystem>
#include <memory>
#include <string>

inline int count_parquets(const std::string& dir) {
    int n = 0;
    for (const auto& entry : std::filesystem::directory_iterator(dir))
        if (entry.path().extension() == ".parquet") ++n;
    return n;
}

struct ParquetTables {
    using ArrowTable = std::shared_ptr<arrow::Table>;
// TABLES_FIELD
};

ParquetTables load_one(const std::string& parquet_dir, int i);
