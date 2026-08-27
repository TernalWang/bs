#pragma once

#include <arrow/table.h>
#include <memory>
#include <string>

struct ParquetTables {
    using ArrowTable = std::shared_ptr<arrow::Table>;
// TABLES_FIELD
};

ParquetTables* load(const std::string& parquet_dir);
