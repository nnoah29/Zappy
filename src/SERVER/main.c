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
#include <bits/signum-generic.h>

#include "my.h"
#include "Server/Server.h"

int help(int ac, char **av) {
    if (ac == 2 && strcmp(av[1], "-help") == 0) {
        printf("USAGE:  ./myftp port path\n");
        printf("\tport is the port number on which the server socket listens\n");
        printf("\tpath is the path to the home directory for the Anonymous user\n");
        return 0;
    }
    fprintf(stderr, "[Error] Invalid argument\n");
    return 84;
}

ConfigServer *parsing(int ac, char **av)
{
    ConfigServer *server = malloc(sizeof(ConfigServer));

    if (ac < 13) {
        printf("Not enough arg\n");
        return NULL;
    }
    if (!server) {
        perror("malloc");
        return NULL;
    }
    memset(server, 0, sizeof(ConfigServer));
    for (int i = 1; i < ac; i++) {
        if (strcmp(av[i], "-p") == 0 && i + 1 < ac) {
            i++;
            server->port = atoi(av[i]);
        }
        else if (strcmp(av[i], "-x") == 0 && i + 1 < ac) {
            i++;
            server->map_w = atoi(av[i]);
        }
        else if (strcmp(av[i], "-y") == 0 && i + 1 < ac) {
            i++;
            server->map_h = atoi(av[i]);
        }
        else if (strcmp(av[i], "-c") == 0 && i + 1 < ac) {
            i++;
            server->nbClients = atoi(av[i]);
        }
        else if (strcmp(av[i], "-f") == 0 && i + 1 < ac) {
            i++;
            server->freq = atoi(av[i]);
        }
        else if (strcmp(av[i], "-n") == 0) {
            i++;
            server->nb_teams = 0;
            while (i < ac && av[i][0] != '-') {
                if (server->nb_teams >= MAX_TEAMS) {
                    printf("Too many teams (max = %d)\n", MAX_TEAMS);
                    free(server);
                    return NULL;
                }
                server->names[server->nb_teams++] = strdup(av[i]);
                i++;
            }
            i--;
        }
        else {
            printf("Unknown or invalid argument: %s\n", av[i]);
            free(server);
            return NULL;
        }
    }
    if (server->port <= 0 || server->map_w <= 0 || server->map_h <= 0 ||
        server->nbClients <= 0 || server->freq <= 0 || server->nb_teams == 0) {
        printf("Invalid configuration values\n");
        free(server);
        return NULL;
    }

    return server;
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

void closeServer(Server *server)
{
    if (server->server_fd != -1)
        close(server->server_fd);
    for (int i = 0; i < server->nfds; i++) {
        if (server->fds[i].fd >= 0)
            close(server->fds[i].fd);
    }
    if (server->clock)
        free(server->clock);
    if (server->config) {
        for (int i = 0; i < server->config->nb_teams; i++)
            free(server->config->names[i]);
        free(server->config);
    }
    free(server);
}

int main(int ac, char *av[])
{
    ConfigServer *conf;
    Server *server;

    if (ac == 2 && av[1] == "-h")
        return help(ac, av);
    conf = parsing(ac, av);
    print_config(conf);
    server = initServer(conf);
    runServer(server);
    closeServer(server);
    for (int i = 0; i < conf->nb_teams; i++)
        free(conf->names[i]);
    free(conf);
    return 0;
}
