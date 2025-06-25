/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** dynamic_buffer.h
*/

#ifndef DYNAMIC_BUFFER_H
    #define DYNAMIC_BUFFER_H

    #include <stddef.h>

typedef struct {
    char *buffer;
    size_t len;
    size_t capacity;
} dynamic_buffer_t;

void buffer_init(dynamic_buffer_t *db, size_t initial_capacity);
void buffer_append(dynamic_buffer_t *db, const char *str);
void buffer_free(dynamic_buffer_t *db);

#endif //DYNAMIC_BUFFER_H
