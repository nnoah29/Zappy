/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** dynamic_buffer.h
*/

#include "dynamic_buffer.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void buffer_init(dynamic_buffer_t *db, size_t initial_capacity)
{
    db->buffer = malloc(initial_capacity);
    if (!db->buffer) {
        perror("malloc dynamic buffer");
        exit(84);
    }
    db->buffer[0] = '\0';
    db->len = 0;
    db->capacity = initial_capacity;
}

void buffer_free(dynamic_buffer_t *db)
{
    if (db->buffer) {
        free(db->buffer);
    }
    db->buffer = NULL;
    db->len = 0;
    db->capacity = 0;
}

void buffer_append(dynamic_buffer_t *db, const char *str)
{
    const size_t str_len = strlen(str);
    size_t new_capacity = db->capacity;
    char *new_buffer = NULL;

    while (db->len + str_len + 1 > db->capacity) {
        new_capacity *= 2;
        new_buffer = realloc(db->buffer, new_capacity);
        if (!new_buffer) {
            perror("realloc dynamic buffer");
            buffer_free(db);
            exit(84);
        }
        db->buffer = new_buffer;
        db->capacity = new_capacity;
    }
    strcat(db->buffer, str);
    db->len += str_len;
}
