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
typedef struct {
    const char *key;
    parser_func_t func;
}option_parser_t;

void exit_error(char *error, int degree);
void parse_port(config_server_t *conf, char **argv, int *i);
void parse_width(config_server_t *conf, char **argv, int *i);
void parse_height(config_server_t *conf, char **argv, int *i);
void parse_clients(config_server_t *conf, char **argv, int *i);
void parse_freq(config_server_t *conf, char **argv, int *i);
void parse_names(config_server_t *conf, char **argv, int *i);

#endif //MY_H
