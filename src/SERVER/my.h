/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** my.h
*/

#ifndef MY_H
    #define MY_H

    #include <unistd.h>
    #include "Server/server.h"

typedef struct {
    int x;
    int y;
} int_pair_t;

void exit_error(char *error, int degree);
int fail_cmd(int fd);
resource_t string_to_resource(const char *str);
void re_spawn_ressources_duration(server_t *server);
void get_next_food_consumption(session_client_t *client, server_t *server);
int calculate_next_event_timeout(server_t *server);
int find_client_by_fd(server_t *server, int fd);
void add_space(char *buffer, bool need_space);
void add_semicolon(char *response, int side, int forward);
const char *resource_to_string(resource_t res);
void append_tile_content(char *buffer, const tile_t *tile);
void calculate_direction_offset(int orientation, int *dx, int *dy,
    int_pair_t rel);
void get_absolute_position(server_t *s, session_client_t *c,
    int_pair_t rel, int_pair_t *pos);
void get_tile_content(server_t *server, session_client_t *client,
    int_pair_t rel, char *tile_buffer);
void error_msg_eggs_init(server_t *s, int eggs_created, int team_idx);
#endif //MY_H
