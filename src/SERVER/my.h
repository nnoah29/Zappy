/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** my.h
*/

#ifndef MY_H
    #define MY_H

    #include <unistd.h>
    #include "Server/server.h"


void exit_error(char *error, int degree);
void re_spawn_ressources_duration(server_t *server);
void get_next_food_consumption(session_client_t *client, server_t *server);
int calculate_next_event_timeout(server_t *server);
int find_client_by_fd(server_t *server, int fd);

#endif //MY_H
