/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Utilitaires.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

void exit_error(char *error, int degree)
{
    (void)degree;
    printf("[ERROR] : %s\n", error);
    exit(84);
}

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

void parse_clients(config_server_t *conf, char **argv, int *i)
{
    (*i)++;
    conf->nbClients = atoi(argv[*i]);
}
