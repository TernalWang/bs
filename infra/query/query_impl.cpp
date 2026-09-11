#include "query_impl.hpp"

#include <iostream>
#include <sstream>
#include <string>

#include "args_parser.hpp"


std::vector<QueryRequest> read_requests() {
    std::vector<QueryRequest> requests;
    std::string line;
    while (std::getline(std::cin, line)) {
        // empty line signals end of input - stop query input loop (terminate execution)
        if (line.empty()) {
            break;
        }
        std::istringstream iss(line);
        std::string query_id =  "0";
        iss >> query_id;
        if (!iss) {
            continue;
        }
        requests.push_back(QueryRequest{query_id, line});
    }
    return requests;
}


MidResult* midresult(Database*, const QueryRequest& request) {
    // TODO: implement the query execution logic on the Database producing this partition's MidResult - use arg parser example code below
    std::cout << "Parsed: Q" << request.id << " args=" << request.line << "\n";

    return new MidResult{};
}


// Example code for how to use the parse functions together:
//for (const auto& req : requests) {
//    switch (req.id) {
//        case 1: {
//            Q1Args args = parse_q1(req);
//            run_q1(db, args);
//            break;
//        }
//        case 2: {
//            Q2Args args = parse_q2(req);
//            run_q2(db, args);
//            break;
//        }
//        ...
//        case 22: {
//            Q22Args args = parse_q22(req);
//            run_q22(db, args);
//            break;
//        }
//    }
//}
