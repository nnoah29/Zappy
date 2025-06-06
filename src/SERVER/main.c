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


#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "my.h"
#include "Server/Server.h"

static OptionParser parsers[] = {
    {"-p", parse_port},
    {"-x", parse_width},
    {"-y", parse_height},
    {"-n", parse_names},
    {"-c", parse_clients},
    {"-f", parse_freq},
    {NULL, NULL}
};

void recursive_parse(ConfigServer *conf, char **argv, int i, int argc)
{
    if (i >= argc)
        return;
    for (int j = 0; parsers[j].key; ++j) {
        if (strcmp(argv[i], parsers[j].key) == 0) {
            parsers[j].func(conf, argv, &i);
            break;
        }
    }
    recursive_parse(conf, argv, i + 1, argc);
}

void print_config(ConfigServer *server)
{
    printf("Port: %d\n", server->port);
    printf("Map size: %d x %d\n", server->map_w, server->map_h);
    printf("Teams (%d): ", server->nb_teams);
    for (int i = 0; i < server->nb_teams; i++)
        printf("%s ", server->names[i]);
    printf("\nClients per team: %d\n", server->nbClients);
    printf("Frequency: %d\n", server->freq);
}

ConfigServer *parse_args(int argc, char **argv)
{
    ConfigServer *conf = malloc(sizeof(ConfigServer));

    recursive_parse(conf, argv, 1, argc);
    if (conf->port <= 0 || conf->map_w <= 0 || conf->map_h <= 0 ||
        conf->nbClients <= 0 || conf->freq <= 0 || conf->nb_teams == 0) {
        printf("Invalid configuration values\n");
        free(conf);
        return NULL;
    }
    return conf;
}


int main(int ac, char *av[])
{
    ConfigServer* conf = parse_args(ac, av);
    //print_config(conf);
    Server* server = initServer(conf);

    runServer(server);
    closeServer(server);
    for (int i = 0; i < conf->nb_teams; i++)
        free(conf->names[i]);
    free(conf);
    return 0;
}