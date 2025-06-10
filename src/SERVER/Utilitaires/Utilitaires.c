/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 02/06/25.                                          
**         |___/ 
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


void parse_port(ConfigServer *conf, char **argv, int *i)
{
    (*i)++;
    conf->port = atoi(argv[*i]);
}

void parse_width(ConfigServer *conf, char **argv, int *i)
{
    (*i)++;
    conf->map_w = atoi(argv[*i]);
}

void parse_height(ConfigServer *conf, char **argv, int *i)
{
    (*i)++;
    conf->map_h = atoi(argv[*i]);
}

void parse_clients(ConfigServer *conf, char **argv, int *i)
{
    (*i)++;
    conf->nbClients = atoi(argv[*i]);
}

void parse_freq(ConfigServer *conf, char **argv, int *i)
{
    (*i)++;
    conf->freq = atoi(argv[*i]);
}

void parse_names(ConfigServer *conf, char **argv, int *i) {
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