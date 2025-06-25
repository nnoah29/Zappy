/*
** EPITECH PROJECT, 2024
** my_project_name
** File description:
** logger.h
*/

#ifndef LOGGER_H_
    #define LOGGER_H_

    #include <stdarg.h>

typedef enum log_level_s {
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR
} log_level_t;


typedef struct logger_config_s {
    log_level_t level;
} logger_config_t;

typedef struct log_meta_s {
    const char *file;
    int line;
} m_t;

/**
 * @example LOG(LOG_INFO, "Serveur démarré sur le port %d.", port);
 */
    #define LOG(l, f, ...) doc(l, (m_t){__FILE__, __LINE__}, f, ##__VA_ARGS__)
    #define COLOR_RESET "\x1b[0m"
    #define COLOR_META "\x1b[90m"

int log_set_level(log_level_t level);

void doc(log_level_t level, m_t meta,
    const char *format, ...);

#endif /* !LOGGER_H_ */
