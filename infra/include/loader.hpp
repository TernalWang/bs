#pragma once

#include <arrow/table.h>
#include <memory>
#include <string>
#include <vector>

struct ParquetTables {
    using ArrowTable = std::shared_ptr<arrow::Table>;
// TABLES_FIELD
};

std::vector<ParquetTables> load(const std::string& parquet_dir);
