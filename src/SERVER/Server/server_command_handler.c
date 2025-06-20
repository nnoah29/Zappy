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


static const option_cmd_t gui_cmds[] = {
    {"msz", msz_h},
    {"bct", bct_h},
    {"mct", mct_h},
    {"tna", tna_h},
    {"ppo", ppo_h},
    {"plv", plv_h},
    {"pin", pin_h},
    {"sgt", sgt_h},
    {"sst", sst_h},
};

static const option_cmd_t ai_cmds[] = {
    {"Forward", forward_f},
    {"Right", right_f},
    {"Left", left_f},
    {"Look", look_f},
    {"Inventory", inventory_f},
    {"Broadcast", broadcast_f},
    {"Connect_nbr", connect_nbr_f},
    {"Fork", fork_f},
    {"Eject", eject_f},
    {"Take", take_object_f},
    {"Set", set_object_f},
};

void handle_command_gui(server_t *server, session_client_t *client, const command_t *cmd)
{
    size_t len = 0;

    for (size_t i = 0; i < sizeof(gui_cmds) / sizeof(gui_cmds[0]); ++i) {
        len = strlen(gui_cmds[i].cmd);
        if (strncasecmp(cmd->raw_cmd, gui_cmds[i].cmd, len) == 0) {
            gui_cmds[i].func(server, client, cmd);
            return;
        }
    }
    printf("Commande inconnue (GUI) : %s\n", cmd->raw_cmd);
    // send_to_client(client, "sbp\n");
}

void handle_command_ai(server_t *server, session_client_t *client, const command_t *cmd)
{
    size_t len = 0;

    for (size_t i = 0; i < sizeof(ai_cmds) / sizeof(ai_cmds[0]); i++) {
        len = strlen(ai_cmds[i].cmd);
        if (strncasecmp(cmd->raw_cmd, ai_cmds[i].cmd, len) == 0) {
            ai_cmds[i].func(server, client, cmd);
            return;
        }
    }
    printf("Commande inconnue (AI) : %s\n", cmd->raw_cmd);
    // send_to_client(client, "ko\n");
}

void register_player_in_team(server_t *server, int client_idx, int team_idx)
{
    const int nb = server->teams[team_idx].nbPlayers;
    session_client_t* client = &server->clients[client_idx];

    server->teams[team_idx].players[nb] = client;
    server->teams[team_idx].nbPlayers++;
    server->teams[team_idx].nbMaxPlayers--;
    client->team_idx = team_idx;
    client->is_egg = false;
    client->is_gui = false;
    client->active = true;
    client->level = 1;
    client->x = (int)random() % server->config->map_w;
    client->y = (int)random() % server->config->map_h;
    client->orientation = ((int)random() % 4) + 1;
    for (int k = 0; k < 7; k++) client->inventory[k] = 0;
    client->inventory[FOOD] = 10;
    map_add_entity(&server->map[client->y][client->x], client);
    get_current_time(&(client->next_food_time));
    get_next_food_consumption(client, server);
}

void assign_team(server_t *server, int client_idx, const char* team_name)
{
    char buffer[128];

    for (int j = 0; j < server->config->nb_teams; j++) {
        if (strcmp(team_name, server->teams[j].name) == 0 &&
            server->teams[j].nbMaxPlayers > 0) {
            register_player_in_team(server, client_idx, j);
            snprintf(buffer, sizeof(buffer), "%d\n", server->teams[j].nbMaxPlayers);
            send(server->clients[client_idx].fd, buffer, strlen(buffer), 0);
            snprintf(buffer, sizeof(buffer), "%d %d\n", server->config->map_w, server->config->map_h);
            send(server->clients[client_idx].fd, buffer, strlen(buffer), 0);
            pnw_f(server, &server->clients[client_idx]);
            printf("Client %d a rejoint l'équipe '%s'.\n", client_idx, team_name);
            return;
        }
    }
    printf("Client %d a échoué à rejoindre l'équipe '%s'.\n", client_idx, team_name);
    send(server->clients[client_idx].fd, "ko\n", 3, 0);
}

void connec_t(server_t *server, session_client_t *client, const command_t *cmd)
{
    const char *team_name = cmd->raw_cmd;

    if (strcmp(team_name, "GRAPHIC") == 0) {
        client->is_gui = true;
        client->active = true;
        printf("Client %d authentifié comme GUI.\n", client->idx);
        // send_full_game_state_to_gui(server, client);
        return;
    }
    assign_team(server, client->idx, team_name);
}

void handle_command(server_t *server, session_client_t *client, const command_t *cmd)
{
    if (!client->active) {
        connec_t(server, client, cmd);
        return;
    }
    if (client->is_gui) {
        handle_command_gui(server, client, cmd);
        return;
    }
    handle_command_ai(server, client, cmd);
}