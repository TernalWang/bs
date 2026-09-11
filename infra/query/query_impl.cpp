#include "query_impl.hpp"

// QN_INCLUDES

#include <chrono>
#include <cstdio>
#include <iostream>
#include <sstream>
#include <string>
#include <type_traits>

#include "args_parser.hpp"


static std::chrono::steady_clock::time_point now() { return std::chrono::steady_clock::now(); }
static double ms(std::chrono::steady_clock::duration d) { return std::chrono::duration<double, std::milli>(d).count(); }

template <typename F>
static std::vector<std::invoke_result_t<F, Database*>> parallel_map(const std::vector<Database*>& dbs, F&& f) {
    std::vector<std::invoke_result_t<F, Database*>> out(dbs.size());
    #pragma omp parallel for schedule(dynamic) num_threads(50)
    for (int i = 0; i < (int)dbs.size(); ++i) out[i] = f(dbs[i]);
    return out;
}


template <typename Mid, typename Args>
static void run_query(int qid, const std::vector<Database*>& dbs, const Args& args, int run_nr,
                      Mid* (*mid)(Database*, const Args&),
                      void (*fin)(std::vector<Mid*>&, const Args&, int)) {
    const auto t0 = now();
    std::vector<Mid*> mids = parallel_map(dbs, [&](Database* db) { return mid(db, args); });
    const auto t1 = now();
    fin(mids, args, run_nr);
    const double p1 = ms(t1 - t0), p2 = ms(now() - t1);
    fprintf(stderr, "[Q%d run%d] phase1=%.3f ms phase2=%.3f ms total=%.3f ms\n", qid, run_nr, p1, p2, p1 + p2);
}


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


void results(const std::vector<Database*>& dbs, const std::vector<QueryRequest>& requests) {
    int run_nr = 0;
    for (const auto& request : requests) {
        ++run_nr;
        try {
            switch (std::stoi(request.id)) {
// QUERY_CASES
                default:
                    fprintf(stderr, "unknown query id %s\n", request.id.c_str());
            }
        } catch (const std::exception& e) {
            fprintf(stderr, "[Q%s] ERROR: %s\n", request.id.c_str(), e.what());
        }
    }
}
