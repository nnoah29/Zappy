/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_4.c
*/

#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"
#include "server.h"
#include "../SessionClients/session_client.h"

void connec_t(server_t *server, session_client_t *client, const command_t *cmd)
{
    const char *team_name = cmd->raw_cmd;
    char buffer[128];
    const int client_idx = client->idx;

    // CAS 1 : Le client est un GUI
    if (strcmp(team_name, "GRAPHIC") == 0) {
        client->team_idx = -1;
        client->is_egg = false;
        client->is_gui = true;
        client->active = true;
        printf("Client %d authentifié comme GUI.\n", client_idx);
        // TODO : envoyer toute les donner concernant la map au GUI
        //send_full_game_state_to_gui(server, client);
        return;
    }
    assign_team(server, client_idx, team_name);
}


void handle_command_gui(server_t *server, session_client_t *client, const command_t *cmd)
{
    size_t len = 0;
    if (!cmd || !cmd->raw_cmd)
        return;

    for (size_t i = 0; i < sizeof(gui_cmds) / sizeof(gui_cmds[0]); ++i) {
        len = strlen(gui_cmds[i].cmd);
        if (strncasecmp(cmd->raw_cmd, gui_cmds[i].cmd, len) == 0) {
            gui_cmds[i].func(server, client, cmd);
            return;
        }
    }

    printf("Commande inconnue (GUI) : %s\n", cmd->raw_cmd);
    // send_to_client(client, "sbp\n"); // commande inconnue pour un GUI
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

void exec_cmd(server_t *server, int i)
{
    session_client_t *client = &server->clients[i];
    struct timespec now;
    int cmdIdx = 0;
    const command_t *cmd = NULL;

    get_current_time(&now);
    cmdIdx = get_next_ready_command(client->queue, &now);
    if (cmdIdx < 0)
        return;
    cmd = &client->queue->commands[cmdIdx];
    handle_command(server, client, cmd);
    remove_command_at(client->queue, cmdIdx);
}

void check_life(server_t *server, int i)
{
    session_client_t *client = &server->clients[i];
    struct timespec now;

    get_current_time(&now);
    if (timespec_cmp(&now, &client->next_food_time) >= 0) {
        client->inventory[FOOD] -= 1;
        printf("Client %d a consommé de la nourriture, reste : %d\n", client->idx, client->inventory[FOOD]);
        get_next_food_consumption(client, server);
        if (client->inventory[FOOD] < 0) {
            send(client->fd, "dead\n", 5, 0);
            // TODO: pdi_f(server, client, NULL); // Notifier le GUI
            map_detach_entity(&server->map[client->y][client->x], client); // Le retirer de la carte
            close_client_connection(server, i);
        }
    }
}
