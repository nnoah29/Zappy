/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_2.c
*/
#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

void acceptClient(server_t *server)
{
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);
    const int client_fd = accept(server->server_fd,
        (struct sockaddr*)&client_addr, &addr_len);

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
    server->clients[server->nfds].last_food_tick =
        get_elapsed_ticks(server->clock);
    send(client_fd, "WELCOME\n", 8, 0);
    server->nfds++;
}

void removeClient(server_t *server, int i)
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
    char *cmd_cpy = NULL;
    char *token = NULL;

    if (!cmd)
        return -1.0;
    cmd_cpy = strdup(cmd);
    token = strtok(cmd_cpy, " \t\n\r");
    free(cmd_cpy);
    if (!token)
        return -1.0;
    for (size_t i = 0; i < sizeof(command_table) /
        sizeof(command_info_t); i++) {
        if (strcmp(token, command_table[i].name) == 0) {
            return (double)command_table[i].units / freq;
        }
    }
    return 0.0;
}

void stockCmd(char *cmd, const session_client_t *client, int freq)
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

void handleClient(server_t *server, int i)
{
    char buffer[1024];
    const long int len = recv(server->fds[i].fd,
        buffer, sizeof(buffer) - 1, 0);
    const session_client_t *client = &server->clients[i];

    if (len <= 0) {
        removeClient(server, i);
        return;
    }
    buffer[len] = '\0';
    stockCmd(buffer, client, server->config->freq);
}
