#include "builder_impl.hpp"


Database* build(ParquetTables*) {
    // TODO: implement the build logic to convert ParquetTables into an efficient in-memory data structure
    return new Database{};
}

void dump_db(Database*, const std::string& dump_dir, int i) {
    // TODO: dump the generated Database of partition i to dump_dir
}

Database* load_db(const std::string& dump_dir, int i) {
    // TODO: load the dumped Database of partition i from dump_dir
    return nullptr;
}

void restore_db(const std::string& dump_dir, const std::string& restore_dir) {
    // TODO: rebuild the original data losslessly from dump_dir into restore_dir
}
