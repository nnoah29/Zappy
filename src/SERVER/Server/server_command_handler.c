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

static void handle_command_gui(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    size_t len = 0;

    for (size_t i = 0; i < sizeof(gui_cmds) / sizeof(gui_cmds[0]); ++i) {
        len = strlen(gui_cmds[i].cmd);
        if (strncasecmp(cmd->raw_cmd, gui_cmds[i].cmd, len) == 0) {
            LOG(LOG_DEBUG, "Commande GUI : %s\n", cmd->raw_cmd);
            gui_cmds[i].func(server, client, cmd);
            return;
        }
    }
    LOG(LOG_ERROR, "Commande inconnue (GUI) : %s\n", cmd->raw_cmd);
}

static void handle_command_ai(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    size_t len = 0;

    for (size_t i = 0; i < sizeof(ai_cmds) / sizeof(ai_cmds[0]); i++) {
        len = strlen(ai_cmds[i].cmd);
        if (strncasecmp(cmd->raw_cmd, ai_cmds[i].cmd, len) == 0) {
            LOG(LOG_DEBUG, "Commande AI : %s\n", cmd->raw_cmd);
            ai_cmds[i].func(server, client, cmd);
            return;
        }
    }
    LOG(LOG_ERROR, "Commande inconnue (AI) : %s\n", cmd->raw_cmd);
}

void assign_team(server_t *server, int client_temp_idx, const char *team_name)
{
    char buffer[128];
    const int team_idx = find_team_by_name(server, team_name);
    const int egg_idx = find_egg_in_team(server, team_idx);

    if (team_idx == -1 || server->teams[team_idx].nbMaxPlayers <= 0) {
        send(server->players[client_temp_idx].fd, "ko\n", 3, 0);
        close_client_connection(server, client_temp_idx);
        return;
    }
    if (egg_idx != -1) {
        hatch_egg_for_client(server, client_temp_idx, egg_idx);
        return;
    }
    LOG(LOG_ERROR, "Client temp #%d a échoué à rejoindre l'équipe '%s'.\n",
        client_temp_idx, team_name);
    send(server->players[client_temp_idx].fd, "ko\n", 3, 0);
    close_client_connection(server, client_temp_idx);
}

// TODO :send_full_game_state_to_gui(server, client);
void connec_t(server_t *server, session_client_t *client, const command_t *cmd)
{
    const char *team_name = cmd->raw_cmd;

    if (strcmp(team_name, "GRAPHIC") == 0) {
        client->is_gui = true;
        client->active = true;
        LOG(LOG_DEBUG, "Client %d authentifié comme GUI.", client->idx);
        send_to_all_guis(server, "nfnvbvnlvn");
        return;
    }
    assign_team(server, client->idx, team_name);
}

void handle_command(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    if (!client->active) {
        connec_t(server, client, cmd);
        return;
    }
    LOG(LOG_DEBUG, "Execution de la commande : %s, du joueur %d",
        cmd->raw_cmd, client->idx);
    if (client->is_gui) {
        handle_command_gui(server, client, cmd);
        return;
    }
    handle_command_ai(server, client, cmd);
}
