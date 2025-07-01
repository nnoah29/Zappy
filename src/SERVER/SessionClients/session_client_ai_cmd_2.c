/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/**
 * @brief Gère la commande Broadcast.
 *        Version simplifiée : envoie le message à tous les autres joueurs avec
 *        une direction factice K=0.
 * @param server Le pointeur du serveur.
 * @param client Le joueur qui envoie le message.
 * @param cmd La commande parsée.
 * @return int 0 en cas de succès.
 */
int broadcast_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    char message_text[1024] = {0};

    if (cmd->argc < 1)
        return fail_cmd(client->fd);
    for (int i = 0; i < cmd->argc; i++) {
        strcat(message_text, cmd->args[i]);
        if (i < cmd->argc - 1)
            strcat(message_text, " ");
    }
    LOG(LOG_DEBUG, "Player %d broadcasts: '%s'", client->idx, message_text);
    distribute_message(server, client, message_text);
    return 0;
}

int connect_nbr_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    const int team_idx = client->team_idx;
    int remaining_slots = 0;

    if (team_idx >= 0 && team_idx < server->config->nb_teams) {
        remaining_slots = server->teams[team_idx].nbMaxPlayers;
    }
    dprintf(client->fd, "%d\n", remaining_slots);
    LOG(LOG_DEBUG, "Player %d requested the number of remaining "
        "slots.", client->idx);
    (void)cmd;
    return 0;
}

int fork_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    const int egg_idx = find_free_slot(server, client);

    (void)cmd;
    if (egg_idx == -1)
        return fail_cmd(client->fd);
    LOG(LOG_DEBUG, "Le joueur %d pond un œuf. Le nouvel œuf sera à l'index %d.",
        client->idx, egg_idx);
    laying_process(server, client, egg_idx);
    return 0;
}

int eject_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    tile_t *tile = &server->map[client->y][client->x];
    entity_on_tile_t *current_node = tile->entities;
    entity_on_tile_t *next_node = NULL;
    session_client_t *other_player = NULL;
    bool ejected_someone = false;

    (void)cmd;
    while (current_node != NULL) {
        next_node = current_node->next;
        other_player = current_node->entity;
        if (!(other_player && other_player->idx != client->idx)) {
            current_node = next_node;
            continue;
        }
        ejected_someone = true;
        just_eject(server, client, other_player, tile);
        current_node = next_node;
    }
    return dprintf(client->fd, ejected_someone ? "ok\n" : "ko\n");
}

int take_object_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    resource_t res_type = -1;
    tile_t *tile = NULL;

    if (cmd->argc < 1)
        return fail_cmd(client->fd);
    res_type = string_to_resource(cmd->args[0]);
    if (res_type >= NB_RESOURCES)
        return fail_cmd(client->fd);
    tile = &server->map[client->y][client->x];
    if (tile->resources[res_type] > 0) {
        tile->resources[res_type]--;
        client->inventory[res_type]++;
        dprintf(client->fd, "ok\n");
        pgt_f(server, client, res_type);
        bct_f(server, client->x, client->y);
    } else
        dprintf(client->fd, "ko\n");
    LOG(LOG_DEBUG, "Le joueur %d a pris %s", client->idx, cmd->args[0]);
    return 0;
}
