#!/usr/bin/env bash
# 编译+链接 → build/db。要清理时手动:rm -rf build
set -e
cd "$(dirname "$0")"

SRC="db.cpp loader/loader.cpp loader/loader_utils.cpp builder/builder_impl.cpp query/query_impl.cpp"

mkdir -p build
g++ -std=c++20 -O2 -Iinclude -Ibuilder -Iquery $(pkg-config --cflags arrow parquet) \
    $SRC -o build/db $(pkg-config --libs arrow parquet)

echo "✅ build/db"
