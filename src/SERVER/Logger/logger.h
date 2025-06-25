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

/**
 * C-H3: La macro est sur une seule ligne et représente une seule instruction.
 *
 * @example LOG(LOG_INFO, "Serveur démarré sur le port %d.", port);
 */
#define LOG(l, f, ...) log_message(l, __FILE__, __LINE__, f, ##__VA_ARGS__)

int log_set_level(log_level_t level);

void log_message(log_level_t level, const char *file, int line,
    const char *format, ...);

#endif /* !LOGGER_H_ */