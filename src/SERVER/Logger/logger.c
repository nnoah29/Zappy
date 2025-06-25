/*
** EPITECH PROJECT, 2024
** my_project_name
** File description:
** logger.c
*/

#include <stdio.h>
#include <time.h>
#include <string.h>
#include <unistd.h>
#include "logger.h"

const char *G_LEVEL_STRINGS[] = {"DEBUG", "INFO ", "WARN ", "ERROR"};
const char *G_LEVEL_COLORS[] = {
    "\x1b[94m", "\x1b[32m", "\x1b[33m", "\x1b[31m"
};

static logger_config_t *get_logger_config(void)
{
    static logger_config_t config = {LOG_DEBUG};

    return &config;
}

static void get_formatted_time(char *buffer, size_t buffer_size)
{
    struct timespec spec;
    struct tm *time_info;
    long ms;

    clock_gettime(CLOCK_REALTIME, &spec);
    time_info = localtime(&spec.tv_sec);
    ms = spec.tv_nsec / 1000000;
    strftime(buffer, buffer_size, "%Y-%m-%d %H:%M:%S", time_info);
    sprintf(buffer + strlen(buffer), ".%03ld", ms);
}

static void print_colored_prefix(log_level_t level, const char *basename,
    int line, const char *time_buf)
{
    fprintf(stderr, COLOR_META "%s " COLOR_RESET "%s[%s]" COLOR_RESET
        COLOR_META " (%s:%d): " COLOR_RESET,
        time_buf,
        G_LEVEL_COLORS[level],
        G_LEVEL_STRINGS[level],
        basename,
        line);
}

static void print_log_prefix(log_level_t level, const char *file, int line)
{
    char time_buffer[30];
    const char *basename;

    get_formatted_time(time_buffer, sizeof(time_buffer));
    basename = strrchr(file, '/');
    basename = (basename == NULL) ? file : basename + 1;
    if (isatty(fileno(stderr))) {
        print_colored_prefix(level, basename, line, time_buffer);
    } else {
        fprintf(stderr, "%s [%s] (%s:%d): ", time_buffer,
            G_LEVEL_STRINGS[level], basename, line);
    }
}

static void print_sanitized_string(const char *str)
{
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] == '\n') {
            fputc('\\', stderr);
            fputc('n', stderr);
        } else {
            fputc(str[i], stderr);
        }
    }
}

int log_set_level(log_level_t level)
{
    logger_config_t *config = get_logger_config();

    config->level = level;
    return 0;
}

void doc(log_level_t level, m_t meta,
    const char *format, ...)
{
    const logger_config_t *config = get_logger_config();
    char buffer[2048];
    va_list args;

    if (level < config->level)
        return;
    print_log_prefix(level, meta.file, meta.line);
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    print_sanitized_string(buffer);
    fprintf(stderr, "\n");
}
