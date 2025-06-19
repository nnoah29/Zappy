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
    #include <stdbool.h>
    #include "../Clock/clock.h"
    #include "../Commandes/commandes.h"
    #include "../Map/map.h"

typedef enum {
    NORTH,
    EAST,
    SOUTH,
    WEST
} orientation_t;

typedef struct session_client_s {
    int x;
    int y;
    int fd;
    int id;
    int idx;
    int level;
    bool active;
    bool is_gui;
    bool is_egg;
    int team_idx;
    int orientation;
    bool is_elevating;
    command_queue_t *queue;
    resource_t inventory[7];
    struct timespec next_food_time;
} session_client_t;


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
    my_clock_t *clock;
    int idsGui[MAX_CLIENTS];
    config_server_t *config;
    struct timespec next_respawn_time;
    int nfds;
    tile_t **map;
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

void run_server(server_t *server);
void handle_signal(int signal);
server_t *setup_server(config_server_t *config);
void cleanup_server(server_t *server);
void put_online(server_t *server);
void init_clients(server_t *server);
void initialize_teams(server_t *server);
server_t *setup_server(config_server_t *config);
void cleanup_server(server_t *server);
void accept_client_connection(server_t *server);
void close_client_connection(server_t *server, int client_idx);
double get_exec_duration(const char *cmd, int freq);
void process_command(char *cmd, const session_client_t *client, int freq);
void receive_client_data(server_t *server, int i);
void handle_signal(int signal);
void handle_network(server_t *server, int i);
void assign_team(server_t *server, int i, const char* team);
void handle_command(server_t *server, session_client_t *client, const command_t *cmd);
void run_server(server_t *server);
void connec_t(server_t *server, session_client_t *client, const command_t *cmd);
void handle_command_gui(server_t *server, session_client_t *client, const command_t *cmd);
void spawn_ressources(server_t *server);
void exec_cmd(server_t *server, int i);
void check_life(server_t *server, int i);
void handle_server(server_t *server);
void handle_command_ai(server_t *server, session_client_t *client, const command_t *cmd);
void handle_network_events(server_t *server);

#endif //SERVER_H
