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


#pragma once

#include <mutex>
#include <string_view>

class Logger {
public:
    enum class LogLevel {
        DEBUG,
        INFO,
        WARN,
        ERROR
    };

    Logger() = delete;
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    static void setLevel(LogLevel level);
    static void log(LogLevel level, const char* file, int line, const char* format, ...);

private:
    static LogLevel s_level;
    static std::mutex s_log_mutex;

    static std::string get_formatted_time();
    static void print_sanitized(const char* str);
};
const char *to_str(const std::string& msg);
#define LOG(level, format, ...) \
    Logger::log(level, __FILE__, __LINE__, format, ##__VA_ARGS__)
