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

Server *initServer(configServer *config)
{
    Server *server = malloc(sizeof(Server));

    memset(server, 0, sizeof(Server));
    server->config = config;
    server->port = config->port;
    server->nfds = 0;
    for (int i = 0; i < MAX_CLIENTS; ++i) {
        server->fds[i].fd = -1;
        server->clients[i].fd = -1;
        server->clients[i].active = 0;
    }
    putOnline(server);
    server->clock = initClock(config->freq);
    signal(SIGINT, handle_signal);
    printf("Serveur en attente de connexions sur le port %d\n", server->port);
    s = server;
    return server;
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
    if (server->nfds >= MAX_CLIENTS) {
        fprintf(stderr, "Trop de clients connectés\n");
        close(client_fd);
        return;
    }
    server->fds[server->nfds].fd = client_fd;
    server->fds[server->nfds].events = POLLIN;
    server->clients[server->nfds].fd = client_fd;
    // server->clients[server->nfds].active = 0;
    send(client_fd, "WELCOME\n", 8, 0);
    server->nfds++;
}

/*
 void acceptClient(Server *server) {
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);
    int client_fd = accept(server->server_fd, (struct sockaddr*)&client_addr, &addr_len);

    if (client_fd < 0)
        exit_error("accept", 0);

    if (server->nfds >= MAX_CLIENTS) {
        fprintf(stderr, "Trop de clients connectés\n");
        close(client_fd);
        return;
    }

    // Étape 1 : Envoi du WELCOME
    send(client_fd, "WELCOME\n", 8, 0);

    // Étape 2 : Lire la ligne "TEAM <name>\n"
    char buffer[1024] = {0};
    int n = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
    if (n <= 0) {
        close(client_fd);
        return;
    }

    // Étape 3 : Extraction du nom d’équipe
    char *team_name = NULL;
    if (strncmp(buffer, "TEAM ", 5) == 0) {
        team_name = strdup(buffer + 5);
        team_name[strcspn(team_name, "\r\n")] = 0; // retirer \n éventuel
    } else {
        fprintf(stderr, "Protocole invalide : %s\n", buffer);
        close(client_fd);
        return;
    }

    // Étape 4 : Vérifier si c’est un client graphique
    if (strcmp(team_name, "GRAPHIC") == 0) {
        // enregistrer comme client graphique
        init_graphic_client(server, client_fd);
        free(team_name);
        return;
    }

    // Étape 5 : Vérifier que le nom d’équipe existe et qu’il reste des slots
    Team *team = get_team_by_name(server, team_name);
    if (!team || team->available_slots <= 0) {
        send(client_fd, "ko\n", 3, 0);
        close(client_fd);
        free(team_name);
        return;
    }

    // Étape 6 : Affecter le joueur à une position aléatoire
    int x = rand() % server->map_width;
    int y = rand() % server->map_height;

    // Étape 7 : Répondre CLIENT <slots>\n X Y\n
    char response[128];
    snprintf(response, sizeof(response), "CLIENT %d\n%d %d\n", team->available_slots - 1, x, y);
    send(client_fd, response, strlen(response), 0);

    // Étape 8 : Initialisation du client
    SessionClient *client = &server->clients[server->nfds];
    client->fd = client_fd;
    client->active = 1;
    client->team_name = team_name;
    client->x = x;
    client->y = y;
    client->level = 1;
    client->orientation = rand() % 4;
    client->is_gui = false;
    init_command_queue(&client->commands); // FIFO
    init_inventory(&client->inventory); // avec 10 food ?

    team->available_slots--;

    server->fds[server->nfds].fd = client_fd;
    server->fds[server->nfds].events = POLLIN;
    server->nfds++;
}

 */

void removeClient(Server *server, int i)
{
    if (server->fds[i].fd != -1)
        close(server->fds[i].fd);
    server->fds[i].fd = -1;
    server->clients[i].fd = -1;
    server->clients[i].active = 0;
    printf("Client %d supprimé\n", i);
}

double get_exec_duration(const char *cmd)
{
    return 1.0; 
}

void stockCmd(char *cmd, const SessionClient *client)
{
    const char *line = strtok(cmd, "\n");
    struct timespec now;
    double exec_duration = 1.0;

    while (line) {
        get_current_time(&now);
        exec_duration = get_exec_duration(line);
        if (!enqueue_command(client->queue, line, exec_duration, now))
            send(client->fd, "ko\n", 3, 0);
        line = strtok(NULL, "\n");
    }
}

void handleClient(Server *server, int i) {
    char buffer[1024];
    const long int len = recv(server->fds[i].fd, buffer, sizeof(buffer) - 1, 0);
    const SessionClient *client = &server->clients[i];

    if (len <= 0) {
        removeClient(server, i);
        return;
    }
    buffer[len] = '\0';
    stockCmd(buffer, client);
    //printf("Client %d: %s", i, buffer);
    //send(server->fds[i].fd, "200 OK\r\n", 8, 0);
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

void execCmd(Server *server, int i)
{

}

void runServer(Server *server)
{
    int ready = 0;

    while (running) {
        ready = poll(server->fds, server->nfds, -1);
        if (ready < 0)
            exit_error("poll", 0);
        for (int i = 0; i < server->nfds; ++i) {
            if (server->fds[i].fd < 0)
                continue;
            handleEntry(server, i);
            execCmd(server, i);
        }
    }
}