/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_core.c
*/

#include <errno.h>
#include <stdio.h>
#include <signal.h>
#include <string.h>

#include "server.h"

/**
 * @brief Gère l'état d'exécution du serveur de manière statique.
 *        Permet de vérifier ou de modifier l'état sans variable globale.
 * @param set_new_state Si -1, ne change pas l'état. Sinon, met à jour l'état.
 * @return int L'état actuel (1 pour en cours, 0 pour arrêté).
 */
static int server_is_running(int set_new_state)
{
    static int running_state = 1;

    if (set_new_state != -1) {
        running_state = set_new_state;
    }
    return running_state;
}

void handle_signal(int signal)
{
    (void)signal;
    server_is_running(0);
    LOG(LOG_INFO, "Signal reçu, arrêt du serveur...");
}

void spawn_ressources(server_t *server)
{
    struct timespec now;

    get_current_time(&now);
    if (timespec_cmp(&now, &server->next_respawn_time) >= 0) {
        map_spawn_resources(server);
        re_spawn_ressources_duration(server);
    }
}

void check_win_condition(server_t *server)
{
    int players_at_max_level[MAX_TEAMS] = {0};
    const session_client_t *player = NULL;

    for (int i = 0; i < MAX_CLIENTS; i++) {
        player = &server->players[i];
        if (player->active && !player->is_gui &&
            !player->is_egg && player->level >= 8) {
            players_at_max_level[player->team_idx]++;
        }
    }
    for (int i = 0; i < server->config->nb_teams; i++) {
        if (players_at_max_level[i] >= 6) {
            LOG(LOG_INFO, "Team '%s' has won the game!",
            server->teams[i].name);
            seg_f(server, server->teams[i].name);
            server_is_running(0);
            return;
        }
    }
}

static void check_life(server_t *server, int client_idx)
{
    session_client_t *client = &server->players[client_idx];
    struct timespec now;

    if (client->is_egg || !client->active || client->is_gui)
        return;
    get_current_time(&now);
    if (timespec_cmp(&now, &client->next_food_time) >= 0) {
        if (client->inventory[FOOD] > 0) {
            client->inventory[FOOD]--;
            get_next_food_consumption(client, server);
        } else {
            LOG(LOG_INFO, "Le joueur %d est mort.", client_idx);
            send(client->fd, "dead\n", 5, 0);
            pdi_f(server, client);
            map_detach_entity(&server->map[client->y][client->x], client);
            close_client_connection(server, client_idx);
        }
    }
}

void handle_game_logic(server_t *server)
{
    spawn_ressources(server);
    check_and_finish_incantations(server);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->players[i].fd == -1 || server->players[i].is_egg)
            continue;
        exec_cmd(server, i);
        check_life(server, i);
    }
    check_win_condition(server);
}

void run_server(server_t *server)
{
    int ready = 0;
    int timeout = 0;

    while (server_is_running(-1)) {
        timeout = calculate_next_event_timeout(server);
        ready = poll(server->fds, server->nfds, timeout);
        if (ready < 0 && errno == EINTR)
            continue;
        if (ready < 0) {
            LOG(LOG_ERROR, "Poll failed: %s", strerror(errno));
            continue;
        }
        if (ready > 0)
            handle_network_events(server);
        handle_game_logic(server);
    }
}
