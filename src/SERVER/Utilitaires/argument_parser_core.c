/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** argument_parser_core.c
*/

#include <stdlib.h>
#include "../my.h"

void parse_port(config_server_t *conf, char **argv, int *i)
{
    (*i)++;
    conf->port = atoi(argv[*i]);
}

void parse_width(config_server_t *conf, char **argv, int *i)
{
    (*i)++;
    conf->map_w = atoi(argv[*i]);
}

void parse_height(config_server_t *conf, char **argv, int *i)
{
    (*i)++;
    conf->map_h = atoi(argv[*i]);
}

void parse_freq(config_server_t *conf, char **argv, int *i)
{
    (*i)++;
    conf->freq = atoi(argv[*i]);
}