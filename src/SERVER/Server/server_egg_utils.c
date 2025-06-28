/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_command_handler.c
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "server.h"

int find_team_by_name(server_t *server, const char *team_name)
{
    for (int i = 0; i < server->config->nb_teams; i++) {
        if (strcmp(server->teams[i].name, team_name) == 0) {
            return i;
        }
    }
    return -1;
}

int find_egg_in_team(server_t *server, int team_idx)
{
    const session_client_t *entity = NULL;

    for (int i = 0; i < MAX_CLIENTS; i++) {
        entity = &server->players[i];
        if (entity->is_egg && entity->team_idx == team_idx
            && entity->fd == -1) {
            return i;
        }
    }
    return -1;
}

void setup_player_from_egg(session_client_t *egg,
    session_client_t *client_temp, server_t *server, int egg_idx)
{
    teams_t *team = &server->teams[egg->team_idx];
    char buffer[128];

    egg->fd = client_temp->fd;
    egg->idx = egg_idx;
    egg->queue = client_temp->queue;
    egg->is_egg = false;
    egg->active = true;
    egg->level = 1;
    egg->orientation = ((int)random() % 4);
    for (int k = 0; k < 7; k++)
        egg->inventory[k] = 0;
    egg->inventory[FOOD] = 10;
    get_current_time(&egg->next_food_time);
    get_next_food_consumption(egg, server);
    client_temp->fd = -1;
    client_temp->queue = NULL;
    close_client_connection(server, client_temp->idx);
}

/**
 * @brief Fait éclore un oeuf pour un client qui vient de se connecter.
 *        Transfère la connexion du slot temporaire vers le slot de l'oeuf,
 *        transforme l'oeuf en joueur, et nettoie le slot temporaire.
 *
 * @param server Le pointeur du serveur.
 * @param client_temp_idx L'index du slot de connexion temporaire.
 * @param egg_idx L'index de l'oeuf qui va éclore.
 */
void hatch_egg_for_client(server_t *server, int client_temp_idx, int egg_idx)
{
    session_client_t *client_temp = &server->players[client_temp_idx];
    session_client_t *egg = &server->players[egg_idx];
    teams_t *team = &server->teams[egg->team_idx];
    char buffer[128];

    setup_player_from_egg(egg, client_temp, server, egg_idx);
    team->nbPlayers++;
    team->nbEggs--;
    team->players[team->nbPlayers - 1] = egg;
    snprintf(buffer, sizeof(buffer), "%d\n",
        team->nbMaxPlayers - team->nbPlayers);
    send(egg->fd, buffer, strlen(buffer), 0);
    snprintf(buffer, sizeof(buffer), "%d %d\n",
        server->config->map_w, server->config->map_h);
    send(egg->fd, buffer, strlen(buffer), 0);
    ebo_f(server, egg->idx);
    pnw_f(server, egg);
    LOG(LOG_INFO, "Client (fd=%d) a pris le contrôle de l'oeuf #%d, devenu "
    "joueur #%d dans l'équipe '%s'.", egg->fd, egg->idx, egg->idx,
    team->name);
}

void init_eggs(int team_idx, server_t *s)
{
    int eggs_created = 0;

    LOG(LOG_DEBUG, "Initialisation des oeuf de l'équipe '%s'.",
        s->teams[team_idx].name);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (eggs_created >= s->teams[team_idx].nbEggs)
            break;
        if (s->players[i].fd == -1 && !s->players[i].is_egg) {
            s->players[i].is_egg = true;
            s->players[i].team_idx = team_idx;
            s->players[i].x = (int)random() % s->config->map_w;
            s->players[i].y = (int)random() % s->config->map_h;
            s->players[i].level = 1;
            map_add_entity(&s->map[s->players[i].y][s->players[i].y],
                &s->players[i]);
            eggs_created++;
        }
    }
    if (eggs_created < s->teams[team_idx].nbEggs)
        error_msg_eggs_init(s, eggs_created, team_idx);
}
