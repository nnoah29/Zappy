/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** main.c
*/

#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "my.h"
#include "Server/server.h"
#include "Logger/logger.h"
const server_t *server_ptr = NULL;

static const option_parser_t parsers[] = {
    {"-p", parse_port},
    {"-x", parse_width},
    {"-y", parse_height},
    {"-n", parse_names},
    {"-c", parse_clients},
    {"-f", parse_freq},
    {NULL, NULL}
};

void recursive_parse(config_server_t *conf, char **argv, int i, int argc)
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

// fonction utlie pour le debogage
void print_config(config_server_t *server)
{
    printf("Port: %d\n", server->port);
    printf("Map size: %d x %d\n", server->map_w, server->map_h);
    printf("Teams (%d): ", server->nb_teams);
    for (int i = 0; i < server->nb_teams; i++)
        printf("%s ", server->names[i]);
    printf("\nClients per team: %d\n", server->nbClients);
    printf("Frequency: %d\n", server->freq);
}

void check_config(config_server_t *conf)
{
    if (conf->port <= 0 || conf->map_w <= 0 || conf->map_h <= 0 ||
        conf->nbClients <= 0 || conf->freq <= 0 || conf->nb_teams == 0)
        exit_error("Invalid configuration values", 84);
}

config_server_t *parse_args(int argc, char **argv)
{
    config_server_t *conf = malloc(sizeof(config_server_t));

    conf->port = 8500;
    conf->map_w = 25;
    conf->map_h = 25;
    conf->nbClients = 10;
    conf->names[0] = strdup("team1");
    conf->names[1] = strdup("team2");
    conf->nb_teams = 2;
    conf->freq = 1;
    LOG(LOG_INFO, "Analyse des arguments en cours...");
    recursive_parse(conf, argv, 1, argc);
    check_config(conf);
    return conf;
}

int main(int ac, char *av[])
{
    const int a = log_set_level(LOG_DEBUG);
    config_server_t *conf = parse_args(ac, av);
    server_t *server = setup_server(conf);

    server_ptr = server;
    run_server(server);
    cleanup_server(server);
    (void)a;
    return 0;
}
