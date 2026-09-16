#pragma once

#include <arrow/table.h>
#include <filesystem>
#include <memory>
#include <string>

inline int count_files(const std::string& dir) {
    return (int)std::distance(std::filesystem::directory_iterator(dir), std::filesystem::directory_iterator());
}

struct ParquetTables {
    using ArrowTable = std::shared_ptr<arrow::Table>;
// TABLES_FIELD
};

ParquetTables load_one(const std::string& parquet_dir, int i);
