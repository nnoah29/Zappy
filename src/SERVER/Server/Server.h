/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Server.h
*/


#ifndef SERVER_H
#define SERVER_H

#include <poll.h>
#include <netinet/in.h>
#include <poll.h>
#include "../Clock/Clock.h"
#include "../SessionClients/SessionClient.h"
#define MAX_TEAMS 10
#define MAX_CLIENTS 1000

typedef struct Teams
{
    char *name;
    int nbPlayers;
    int nbMaxPlayers;
    SessionClient *players[MAX_CLIENTS];
    int nbEggs;
} Teams;

typedef struct configServer {
    int port;
    int map_w;
    int map_h;
    char *names[MAX_TEAMS];
    int nbClients;
    int nb_teams;
    int freq;
} ConfigServer;

typedef struct Server {
    int port;
    int server_fd;
    struct sockaddr_in server_addr;
    struct pollfd fds[MAX_CLIENTS];
    SessionClient clients[MAX_CLIENTS];
    Teams teams[MAX_TEAMS];
    Clock *clock;
    int idsGui[MAX_CLIENTS];
    ConfigServer *config;
    int nfds;
} Server;


typedef struct {
    const char *name;
    int units;
} CommandInfo;

static const CommandInfo command_table[] = {
    {"Forward", 7},
    {"Right", 7},
    {"Left", 7},
    {"Look", 7},
    {"Inventory", 1},
    {"Broadcast", 7},
    {"Connect_nbr", 0},
    {"Fork", 42},
    {"Eject", 7},
    {"Take", 7},
    {"Set", 7},
    {"Incantation", 300},
};


void runServer(Server *server);
void handle_signal(int signal);
Server *initServer(ConfigServer *config);
void closeServer(Server *server);

#endif //SERVER_H
