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

void setup_client(server_t *server, int idx, int fd)
{
    server->fds[server->nfds].fd = fd;
    server->fds[server->nfds].events = POLLIN;
    server->clients[idx].fd = fd;
    server->clients[idx].idx = idx;
    server->clients[idx].queue = calloc(1, sizeof(command_queue_t));
    init_command_queue(server->clients[idx].queue);
    send(fd, "WELCOME\n", 8, 0);
    server->nfds++;
}

void accept_client_connection(server_t *server)
{
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);
    const int client_fd = accept(server->server_fd,
        (struct sockaddr*)&client_addr, &addr_len);
    const int new_idx = find_free_client_slot(server);

    if (client_fd < 0)
        exit_error("accept", 0);
    if (new_idx == -1) {
        fprintf(stderr, "Trop de clients connectés\n");
        close(client_fd);
        return;
    }
    setup_client(server, new_idx, client_fd);
}

void close_client_connection(server_t *server, int client_idx)
{
    int poll_idx = -1;

    for (int i = 0; i < server->nfds; i++) {
        if (server->fds[i].fd == server->clients[client_idx].fd) {
            poll_idx = i;
            break;
        }
    }
    if (server->clients[client_idx].fd != -1)
        close(server->clients[client_idx].fd);
    memset(&server->clients[client_idx], 0, sizeof(session_client_t));
    server->clients[client_idx].fd = -1;
    server->clients[client_idx].idx = -1;
    if (poll_idx != -1) {
        server->fds[poll_idx] = server->fds[server->nfds - 1];
        server->nfds--;
    }
    printf("Client %d supprimé et slot compacté.\n", client_idx);
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

void process_command(char *cmd, const session_client_t *client, int freq)
{
    const char *line = strtok(cmd, "\n");
    struct timespec now;
    double exec_duration = 1.0;

    while (line) {
        get_current_time(&now);
        exec_duration = get_exec_duration(line, freq);
        if (!enqueue_command(client->queue, line, exec_duration, &now))
            send(client->fd, "ko\n", 3, 0);
        line = strtok(NULL, "\n");
    }
}

void receive_client_data(server_t *server, int i)
{
    char buffer[1024];
    const long int len = recv(server->fds[i].fd,
        buffer, sizeof(buffer) - 1, 0);
    const session_client_t *client = &server->clients[i];

    if (len <= 0) {
        close_client_connection(server, i);
        return;
    }
    buffer[len] = '\0';
    process_command(buffer, client, server->config->freq);
}
