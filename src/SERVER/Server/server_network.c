/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_network.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "server.h"
#include "../my.h"

static int find_free_client_slot(server_t *server)
{
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->clients[i].fd == -1) {
            return i;
        }
    }
    return -1;
}

static void process_client_activity(server_t *server, int i)
{
    int client_idx = -1;

    if (server->fds[i].fd == server->server_fd) {
        accept_client_connection(server);
    } else {
        client_idx = find_client_by_fd(server, server->fds[i].fd);
        if (client_idx != -1)
            receive_client_data(server, client_idx);
    }
}

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
    if (new_idx == -1 || server->nfds >= MAX_CLIENTS) {
        fprintf(stderr, "Trop de clients connectés\n");
        close(client_fd);
        return;
    }
    setup_client(server, new_idx, client_fd);
    printf("Nouveau client connecté avec fd %d, assigné à l'index %d.\n",
        client_fd, new_idx);
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
    free(server->clients[client_idx].queue);
    memset(&server->clients[client_idx], 0, sizeof(session_client_t));
    server->clients[client_idx].fd = -1;
    server->clients[client_idx].idx = -1;
    if (poll_idx != -1) {
        server->fds[poll_idx] = server->fds[server->nfds - 1];
        server->nfds--;
    }
    printf("Client %d supprimé et slot compacté.\n", client_idx);
}

void handle_network_events(server_t *server)
{
    for (int i = 0; i < server->nfds; i++) {
        if (server->fds[i].revents & POLLIN) {
            process_client_activity(server, i);
        }
    }
}
