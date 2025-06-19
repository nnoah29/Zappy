/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_5.c
*/

#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"
#include "../SessionClients/session_client.h"

const option_cmd_t ai_cmds[] = {
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

/**
 * @brief Traite les données reçues d'un client spécifique.
 *
 * Cette fonction est appelée lorsqu'on sait qu'un client (pas le serveur d'écoute)
 * a des données à lire. Elle trouve l'index du client et appelle receive_client_data.
 * @param server Le pointeur du serveur.
 * @param i
 */
static void process_client_activity(server_t *server, int i)
{
    int client_idx = -1;

    if (server->fds[i].fd == server->server_fd)
            accept_client_connection(server);
    else {
        client_idx = find_client_by_fd(server, server->fds[i].fd);
        if (client_idx != -1)
            receive_client_data(server, client_idx);
    }
}

/**
 * @brief Parcourt les descripteurs de fichiers après un appel à poll()
 *        et délègue le traitement des événements réseau.
 *
 * @param server Le pointeur du serveur.
 */
void handle_network_events(server_t *server)
{
    for (int i = 0; i < server->nfds; i++) {
        if (!(server->fds[i].revents & POLLIN))
            continue;
        process_client_activity(server, i);
    }
}

void handle_command_ai(server_t *server, session_client_t *client, const command_t *cmd)
{
    size_t len = 0;

    if (!cmd || !cmd->raw_cmd)
        return;
    for (size_t i = 0; i < sizeof(ai_cmds) / sizeof(ai_cmds[0]); i++) {
        len = strlen(ai_cmds[i].cmd);
        if (strncasecmp(cmd->raw_cmd, ai_cmds[i].cmd, len) == 0) {
            ai_cmds[i].func(server, client, cmd);
            return;
        }
    }
    printf("Commande inconnue (AI) : %s\n", cmd->raw_cmd);
    // TODO: send_to_client(client, "ko\n");
}
