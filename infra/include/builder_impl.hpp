#pragma once

#include "loader.hpp"

struct Database {
    // TODO: Data structures to hold the in-memory representation of the data
};


Database* build(ParquetTables*);
void dump_db(Database*, const std::string& dump_dir, int i);
Database* load_db(const std::string& dump_dir, int i);
void restore_db(const std::string& dump_dir, const std::string& restore_dir);
