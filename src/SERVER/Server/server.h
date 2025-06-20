/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server.h
*/

#ifndef SERVER_H
    #define SERVER_H

    #include <poll.h>
    #include <netinet/in.h>
    #include <stdbool.h>
    #include "../Clock/clock.h"
    #include "../Commandes/command.h"
    #include "../Map/map.h"
    #include "../SessionClients/session_client.h"

    #define MAX_TEAMS 10
    #define MAX_CLIENTS 1000

// Structures (inchangées)
typedef enum {
    NORTH,
    EAST,
    SOUTH,
    WEST
} orientation_t;

typedef struct session_client_s {
    int x, y;
    int fd, idx, level;
    bool active, is_gui, is_egg;
    int team_idx, parent_idx;
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
    int port, map_w, map_h;
    char *names[MAX_TEAMS];
    int nbClients, nb_teams, freq;
} config_server_t;

typedef struct server {
    int port, server_fd, nfds;
    struct sockaddr_in server_addr;
    struct pollfd fds[MAX_CLIENTS + 1]; // +1 pour le socket serveur
    session_client_t clients[MAX_CLIENTS];
    teams_t teams[MAX_TEAMS];
    config_server_t *config;
    struct timespec next_respawn_time;
    tile_t **map;
} server_t;

typedef struct {
    const char *name;
    int units;
} command_info_t;

typedef void (*parser_func_t)(config_server_t *conf, char **argv, int *i);
typedef void (*cmd_func_t)(server_t *server, session_client_t *client,
    const command_t *cmd);

typedef struct {
    const char *key;
    parser_func_t func;
}option_parser_t;

typedef struct {
    const char *cmd;
    cmd_func_t func;
} option_cmd_t;

extern const command_info_t command_table[];
extern const size_t cmd_table_size;

void parse_port(config_server_t *conf, char **argv, int *i);
void parse_width(config_server_t *conf, char **argv, int *i);
void parse_height(config_server_t *conf, char **argv, int *i);
void parse_clients(config_server_t *conf, char **argv, int *i);
void parse_freq(config_server_t *conf, char **argv, int *i);
void parse_names(config_server_t *conf, char **argv, int *i);

// server_init.c
server_t *setup_server(config_server_t *config);
void cleanup_server(server_t *server);
void put_online(server_t *server);
void init_clients(server_t *server);
void initialize_teams(server_t *server);

// server_network.c
void accept_client_connection(server_t *server);
void close_client_connection(server_t *server, int client_idx);
void handle_network_events(server_t *server);
void setup_client(server_t *server, int idx, int fd);
int find_client_by_fd(server_t *server, int fd); // à implémenter

// server_core.c
void run_server(server_t *server);
void handle_signal(int signal);
void handle_game_logic(server_t *server);
void spawn_ressources(server_t *server);
void check_life(server_t *server, int client_idx);

// server_command_queue.c
void receive_client_data(server_t *server, int client_idx);
void process_command(char *cmd, const session_client_t *client, int freq);
double get_exec_duration(const char *cmd, int freq);
void exec_cmd(server_t *server, int client_idx);

// server_command_handler.c
void handle_command(server_t *server, session_client_t *client,
    const command_t *cmd);
void connec_t(server_t *server, session_client_t *client,
    const command_t *cmd);
void assign_team(server_t *server, int client_idx, const char *team_name);



#endif //SERVER_H
