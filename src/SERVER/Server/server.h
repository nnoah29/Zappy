/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Server.h
*/

#ifndef SERVER_H
    #define SERVER_H
    #define MAX_TEAMS 10
    #define MAX_CLIENTS 1000
    #include <poll.h>
    #include <netinet/in.h>
    #include <poll.h>
    #include "../Clock/Clock.h"
    #include "../SessionClients/sessionClient.h"

typedef struct Teams {
    char *name;
    int nbPlayers;
    int nbMaxPlayers;
    session_client_t *players[MAX_CLIENTS];
    int nbEggs;
} teams_t;

typedef struct configServer {
    int port;
    int map_w;
    int map_h;
    char *names[MAX_TEAMS];
    int nbClients;
    int nb_teams;
    int freq;
} config_server_t;

typedef struct server {
    int port;
    int server_fd;
    struct sockaddr_in server_addr;
    struct pollfd fds[MAX_CLIENTS];
    session_client_t clients[MAX_CLIENTS];
    teams_t teams[MAX_TEAMS];
    Clock *clock;
    int idsGui[MAX_CLIENTS];
    config_server_t *config;
    int nfds;
} server_t;


typedef struct {
    const char *name;
    int units;
} command_info_t;

static const command_info_t command_table[] = {
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


void runServer(server_t *server);
void handle_signal(int signal);
server_t *initServer(config_server_t *config);
void closeServer(server_t *server);
void putOnline(server_t *server);
void initClients(server_t *server);
void initTeams(server_t *server);
server_t *initServer(config_server_t *config);
void closeServer(server_t *server);
void acceptClient(server_t *server);
void removeClient(server_t *server, int i);
double get_exec_duration(const char *cmd, int freq);
void stockCmd(char *cmd, const session_client_t *client, int freq);
void handleClient(server_t *server, int i);
void handle_signal(int signal);
void handleEntry(server_t *server, int i);
void assignTeam(server_t *server, int i, char *team);
void handleCommand(server_t *server, session_client_t *client, char *cmd);
void runServer(server_t *server);
void connec_t(server_t *server, session_client_t *client, char *cmd);
void handleCommandGui(server_t *server, session_client_t *client, char *cmd);
void spawnRessources(server_t *server);
void execCmd(server_t *server, int i);
void checkLife(server_t *server, int i);
void handle_server(server_t *server);

#endif //SERVER_H
