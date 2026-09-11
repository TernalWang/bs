#pragma once

#include "args_parser.hpp"
#include "builder_impl.hpp"

#include <vector>


std::vector<QueryRequest> read_requests();
void results(const std::vector<Database*>& dbs, const std::vector<QueryRequest>& requests);
