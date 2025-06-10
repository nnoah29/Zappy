/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Utilitaires_2.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

void parse_freq(config_server_t *conf, char **argv, int *i)
{
    (*i)++;
    conf->freq = atoi(argv[*i]);
}

void parse_names(config_server_t *conf, char **argv, int *i)
{
    int j = 0;

    (*i)++;
    while (argv[*i] && argv[*i][0] != '-' && j < MAX_TEAMS) {
        conf->names[j] = strdup(argv[*i]);
        conf->names[j + 1] = NULL;
        j++;
        (*i)++;
    }
    conf->nb_teams = j;
    (*i)--;
}
