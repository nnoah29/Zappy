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

#include "Server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"
static int running = 1;
static Server *s;

void putOnline(Server *server)
{
    server->server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->server_fd == -1)
        exit_error("socket", 0);
    memset(&server->server_addr, 0, sizeof(server->server_addr));
    server->server_addr.sin_family = AF_INET;
    server->server_addr.sin_addr.s_addr = INADDR_ANY;
    server->server_addr.sin_port = htons(server->port);
    if (bind(server->server_fd, (struct sockaddr *)&server->server_addr, sizeof(server->server_addr)) < 0)
        exit_error("bind", 0);
    if (listen(server->server_fd, 5) < 0)
        exit_error("listen", 0);
}

void initClients(Server *server)
{
    for (int i = 0; i < MAX_CLIENTS; ++i) {
        server->fds[i].fd = -1;
        server->clients[i].fd = -1;
        server->clients[i].active = 0;
    }
}

void initTeams(Server *server)
{
    char **names = server->config->names;

    for (int i = 0; names[i] != NULL; ++i) {
        server->teams[i].name = strdup(names[i]);
        server->teams[i].nbPlayers = 0;
        server->teams[i].nbMaxPlayers = server->config->nbClients;
        server->teams[i].nbEggs = server->config->nbClients * 2/3;
    }
}

Server *initServer(ConfigServer *config)
{
    Server *server = malloc(sizeof(Server));

    memset(server, 0, sizeof(Server));
    server->config = config;
    server->port = config->port;
    server->nfds = 0;
    initClients(server);
    initTeams(server);
    putOnline(server);
    server->clock = initClock(config->freq);
    signal(SIGINT, handle_signal);
    printf("Serveur en attente de connexions sur le port %d\n", server->port);
    s = server;
    return server;
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

void acceptClient(Server *server)
{
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);
    const int client_fd = accept(server->server_fd, (struct sockaddr*)&client_addr, &addr_len);

    if (client_fd < 0)
        exit_error("accept", 0);
    if (server->nfds >= MAX_CLIENTS) {
        fprintf(stderr, "Trop de clients connectés\n");
        close(client_fd);
        return;
    }
    server->fds[server->nfds].fd = client_fd;
    server->fds[server->nfds].events = POLLIN;
    server->clients[server->nfds].fd = client_fd;
    server->clients[server->nfds].last_food_tick = get_elapsed_ticks(server->clock);
    // server->clients[server->nfds].active = 0;
    send(client_fd, "WELCOME\n", 8, 0);
    server->nfds++;
}

void removeClient(Server *server, int i)
{
    if (server->fds[i].fd != -1)
        close(server->fds[i].fd);
    server->fds[i].fd = -1;
    server->clients[i].fd = -1;
    server->clients[i].active = 0;
    printf("Client %d supprimé\n", i);
}

double get_exec_duration(const char *cmd, int freq)
{
    char cmd_cpy[256];
    char *token;

    if (!cmd)
        return -1.0;
    strncpy(cmd_cpy, cmd, sizeof(cmd_cpy) - 1);
    cmd_cpy[sizeof(cmd_cpy) - 1] = '\0';
    token = strtok(cmd_cpy, " \t\n\r");
    if (!token)
        return -1.0;
    for (size_t i = 0; i < sizeof(command_table) / sizeof(CommandInfo); i++) {
        if (strcmp(token, command_table[i].name) == 0)
            return (double)command_table[i].units/ freq;
    }
    return -1.0;
}

void stockCmd(char *cmd, const SessionClient *client, int freq)
{
    const char *line = strtok(cmd, "\n");
    struct timespec now;
    double exec_duration = 1.0;

    while (line) {
        get_current_time(&now);
        exec_duration = get_exec_duration(line, freq);
        if (!enqueue_command(client->queue, line, exec_duration, now))
            send(client->fd, "ko\n", 3, 0);
        line = strtok(NULL, "\n");
    }
}


void handleClient(Server *server, int i)
{
    char buffer[1024];
    const long int len = recv(server->fds[i].fd, buffer, sizeof(buffer) - 1, 0);
    const SessionClient *client = &server->clients[i];

    if (len <= 0) {
        removeClient(server, i);
        return;
    }
    buffer[len] = '\0';
    stockCmd(buffer, client, server->config->freq);
}

void handle_signal(int signal)
{
    (void)signal;
    running = 0;
}

void handleEntry(Server *server, int i)
{
    if (server->fds[i].revents & POLLIN) {
        if (server->fds[i].fd == server->server_fd)
            acceptClient(server);
        else
            handleClient(server, i);
    }
}

void assignTeam(Server *server, int i, char *team)
{
    int nb = 0;

    if (strcmp(team, "GRAPHIC") == 0) {
        server->clients[i].team_idx = -1;
        server->clients[i].is_egg = false;
        server->clients[i].is_gui = true;
        server->clients[i].active = true;
        return;
    }
    for (int j = 0; j < server->config->nb_teams; j++) {
        if (strcmp(team, server->teams[j].name) == 0 && server->teams[j].nbEggs > 0 && server->teams[j].nbMaxPlayers > 0 ) {
            nb = server->teams[j].nbPlayers;
            server->teams[j].players[nb] = &server->clients[i];
            server->teams[j].nbPlayers++;
            server->teams[j].nbEggs--;
            server->teams[j].nbMaxPlayers--;
            server->clients[i].team_idx = j;
            server->clients[i].is_egg = false;
            server->clients[i].is_gui = false;
            return;
        }
    }
    send(server->clients[i].fd, "Team does not exit\n", 19, 0);
    removeClient(server, i);
}


void connec_t(Server *server, SessionClient *client, char *cmd)
{

}

void handleCommandGui(Server *server, SessionClient *client, char *cmd)
{

}

void handleCommand(Server *server, SessionClient *client, char *cmd)
{
    if (!client->active) {
        connec_t(server, client, cmd);
        return;
    }
    if (client->is_gui) {
        handleCommandGui(server, client, cmd);
        return;
    }
}

void execCmd(Server *server, int i)
{
    SessionClient *client = &server->clients[i];
    struct timespec now;
    get_current_time(&now);
    Command *cmd = peek_command(client->queue);

    if (is_command_ready(cmd, now)) {
        handleCommand(server, client, cmd->raw_cmd);
        dequeue_command(client->queue);
    }
}

void checkLife(Server *server, int i)
{
    SessionClient *client = &server->clients[i];
    const long now_tick = get_elapsed_ticks(server->clock);

    if (now_tick - client->last_food_tick >= 126) {
        client->inventory[FOOD] -= 1;
        client->last_food_tick = now_tick;
        if (client->inventory[FOOD] < 0)
            removeClient(server, i);
    }
}

void spawnRessources(Server *server)
{

}

void runServer(Server *server)
{
    int ready = 0;

    while (running) {
        ready = poll(server->fds, server->nfds, -1);
        if (ready < 0)
            continue;
        for (int i = 0; i < server->nfds; ++i) {
            if (server->fds[i].fd < 0 || server->clients[i].is_egg)
                continue;
            handleEntry(server, i);
            execCmd(server, i);
            checkLife(server, i);
        }
        spawnRessources(server);
    }
}