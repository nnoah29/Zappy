/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 07/07/25.                                          
**         |___/ 
*/


#include "Logger.hpp"

#include <iostream>
#include <vector>
#include <chrono>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <mutex>
#include <unistd.h>

Logger::LogLevel Logger::s_level = Logger::LogLevel::DEBUG;
std::mutex Logger::s_log_mutex;

const std::vector<std::string_view> G_LEVEL_STRINGS = {"DEBUG", "INFO ", "WARN ", "ERROR"};
const std::vector<std::string_view> G_LEVEL_COLORS = {"\x1b[94m", "\x1b[32m", "\x1b[33m", "\x1b[31m"};
const std::string_view COLOR_RESET = "\x1b[0m";
const std::string_view COLOR_META = "\x1b[90m";

const char *to_str(const std::string& msg)
{
    return msg.c_str();
}

void Logger::setLevel(LogLevel level)
{
    std::lock_guard<std::mutex> lock(s_log_mutex);
    s_level = level;
}

std::string Logger::get_formatted_time()
{
    const auto now = std::chrono::system_clock::now();
    const auto time_t_now = std::chrono::system_clock::to_time_t(now);
    const auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;

    char time_buffer[100];
    strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%d %H:%M:%S", localtime(&time_t_now));
    snprintf(time_buffer + strlen(time_buffer), sizeof(time_buffer) - strlen(time_buffer), ".%03ld", ms.count());

    return time_buffer;
}

void Logger::print_sanitized(const char* str)
{
    for (int i = 0; str[i] != '\0'; ++i) {
        if (str[i] == '\n') {
            std::cerr << "\\n";
        } else {
            std::cerr << str[i];
        }
    }
}

void Logger::log(LogLevel level, const char* file, int line, const char* format, ...)
{
    if (level < s_level) {
        return;
    }
    std::lock_guard<std::mutex> lock(s_log_mutex);

    const std::string time_str = get_formatted_time();
    const char* basename = strrchr(file, '/');
    basename = (basename == nullptr) ? file : basename + 1;

    const auto level_idx = static_cast<size_t>(level);

    if (isatty(fileno(stderr))) {
        std::cerr << COLOR_META << time_str << " " << COLOR_RESET
                  << G_LEVEL_COLORS[level_idx] << "[" << G_LEVEL_STRINGS[level_idx] << "]" << COLOR_RESET
                  << COLOR_META << " (" << basename << ":" << line << "): " << COLOR_RESET;
    } else {
        std::cerr << time_str << " [" << G_LEVEL_STRINGS[level_idx] << "] "
                  << "(" << basename << ":" << line << "): ";
    }

    char message_buffer[2048];
    va_list args;
    va_start(args, format);
    vsnprintf(message_buffer, sizeof(message_buffer), format, args);
    va_end(args);

    print_sanitized(message_buffer);
    std::cerr << std::endl;
}