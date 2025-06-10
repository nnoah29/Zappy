/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** my.h
*/

#ifndef MY_H
    #define MY_H

    #include <unistd.h>
    #include "Server/Server.h"

typedef void (*parser_func)(ConfigServer *conf, char **argv, int *i);
typedef struct {
    const char *key;
    parser_func func;
}OptionParser;

void exit_error(char *error, int degree);
void parse_port(ConfigServer *conf, char **argv, int *i);
void parse_width(ConfigServer *conf, char **argv, int *i);
void parse_height(ConfigServer *conf, char **argv, int *i);
void parse_clients(ConfigServer *conf, char **argv, int *i);
void parse_freq(ConfigServer *conf, char **argv, int *i);
void parse_names(ConfigServer *conf, char **argv, int *i);

#endif //MY_H
