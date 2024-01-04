#pragma once

#include "wglog.h"
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>


#ifdef _DEBUG
    auto logger = spdlog::stdout_color_mt("log") ;
#else
    auto logger = spdlog::basic_logger_mt("log", "basic-log.txt");
#endif