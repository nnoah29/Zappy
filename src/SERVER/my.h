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

typedef void (*parser_func_t)(config_server_t *conf, char **argv, int *i);
typedef void (*cmd_func_t)(server_t *server, session_client_t *client, const command_t *cmd);


typedef struct {
    const char *key;
    parser_func_t func;
}option_parser_t;

typedef struct {
    const char *cmd;
    cmd_func_t func;
} option_cmd_t;

void exit_error(char *error, int degree);
void parse_port(config_server_t *conf, char **argv, int *i);
void parse_width(config_server_t *conf, char **argv, int *i);
void parse_height(config_server_t *conf, char **argv, int *i);
void parse_clients(config_server_t *conf, char **argv, int *i);
void parse_freq(config_server_t *conf, char **argv, int *i);
void parse_names(config_server_t *conf, char **argv, int *i);
void re_spawn_ressources_duration(server_t *server);
void get_next_food_consumption(session_client_t *client, server_t *server);
int calculate_next_event_timeout(server_t *server);
int find_free_client_slot(server_t *server);
int find_client_by_fd(server_t *server, int fd);

#endif //MY_H
