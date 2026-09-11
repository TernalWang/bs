#pragma once

#include "args_parser.hpp"
#include "builder_impl.hpp"

#include <vector>


struct MidResult {
    // TODO: Data structures to hold the intermediate results of one partition
};

std::vector<QueryRequest> read_requests();
MidResult* midresult(Database*, const QueryRequest& request);
void results(const std::vector<Database*>& dbs, const std::vector<QueryRequest>& requests);
