/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "../SessionClients/session_client.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void just_eject(server_t *server, session_client_t *client,
    session_client_t *other_player, tile_t *tile)
{
    if (other_player->is_egg)
        eject_egg(server, other_player, tile);
    else
        eject_player(server, other_player, client);
}

void eject_egg(server_t *server, session_client_t *other_player,
    tile_t *tile)
{
    edi_f(server, other_player->idx);
    map_detach_entity(tile, other_player);
    close_client_connection(server, other_player->idx);
}

void eject_player(server_t *server, session_client_t
    *other_player, session_client_t *client)
{
    int_pair_t new_pos;

    calculate_direction(server, client, &new_pos.x, &new_pos.y);
    map_move_entity(server->map, other_player, new_pos.x, new_pos.y);
    ppo_f(server, other_player);
    pex_f(server, other_player);
}
