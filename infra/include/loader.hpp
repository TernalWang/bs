#pragma once

#include <arrow/table.h>
#include <memory>
#include <string>

struct ParquetTables {
    using ArrowTable = std::shared_ptr<arrow::Table>;
    ArrowTable customer;
    ArrowTable lineitem;
    ArrowTable nation;
    ArrowTable orders;
    ArrowTable part;
    ArrowTable partsupp;
    ArrowTable region;
    ArrowTable supplier;
};

ParquetTables* load(const std::string& parquet_dir);
