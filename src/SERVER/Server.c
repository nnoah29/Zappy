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
#include "my.h"
static int running;
static Server *s;

void initServer(Server *server, int port)
{
    server->port = port;
    server->server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->server_fd == -1)
        exit_error("socket", 1);
    memset(&server->server_addr, 0, sizeof(server->server_addr));
    server->server_addr.sin_family = AF_INET;
    server->server_addr.sin_addr.s_addr = INADDR_ANY;
    server->server_addr.sin_port = htons(port);
    if (bind(server->server_fd, (struct sockaddr *)&server->server_addr, sizeof(server->server_addr)) < 0)
        exit_error("bind", 0);
    if (listen(server->server_fd, 5) < 0)
        exit_error("listen", 0);
    for (int i = 0; i < MAX_CLIENTS; i++)
        server->clients[i].fd = -1;
    printf("Serveur en attente de connexions sur le port %d\n", port);
    s = server;
}

void closeServer(Server *server)
{
    close(server->server_fd);
}

void acceptClient(Server *server)
{
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);
    const int client_fd = accept(server->server_fd, (struct sockaddr*)&client_addr, &addr_len);

    if (client_fd < 0)
        exit_error("accept", 0);
    server->fds[server->nfds].fd = client_fd;
    server->fds[server->nfds].events = POLLIN;
    server->clients[server->nfds].fd = client_fd;
    server->clients[server->nfds].active = 1;
    write(client_fd, "220 Welcome to TRANTOR\r\n", 23);
    server->nfds++;
}

void removeClient(Server *server, int i)
{
    close(server->fds[i].fd);
    server->fds[i].fd = -1;
    server->clients[i].fd = -1;
    server->clients[i].active = 0;
    printf("Client %d supprimé\n", i);
}

void handleClient(Server *server, int i) {
    char buffer[1024];
    const int len = read(server->fds[i].fd, buffer, sizeof(buffer) - 1);

    if (len <= 0) {
        removeClient(server, i);
        return;
    }
    buffer[len] = '\0';
    printf("Client %d: %s", i, buffer);
    write(server->fds[i].fd, "200 OK\r\n", 8);
}

void handle_signal(int signal)
{
    (void)signal;
    closeServer(s);
    running = 0;
    exit(0);
}

void runServer(Server *server)
{
    int ready = 0;

    signal(SIGINT, handle_signal);
    while (running) {
        ready = poll(server->fds, MAX_CLIENTS, -1);
        if (ready < 0)
            exit_error("poll", 0);
        for (int i = 0; i < MAX_CLIENTS; ++i) {
            if (server->fds[i].fd < 0)
                continue;
            if (server->fds[i].revents & POLLIN) {
                if (server->fds[i].fd == server->server_fd)
                    acceptClient(server);
                else
                    handleClient(server, i);
            }
        }
    }
}