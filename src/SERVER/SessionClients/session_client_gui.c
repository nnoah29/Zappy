/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** session_client_gui.c
*/

#include "session_client.h"
#include "../Server/server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

void send_to_all_guis(server_t *server, const char *msg)
{
    for (int i = 0; i < server->nfds; ++i) {
        if (server->fds[i].fd < 0 || !server->clients[i].is_gui
            || server->clients[i].is_egg)
            continue;
        send(server->clients[i].fd, msg, strlen(msg), 0);
    }
}

/// Envoie la taille de la map (msz)
void msz_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("msz\n");
}

/// Envoie le contenu d’une case spécifique (bct X Y)
void bct_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("bct\n");
}

/// Envoie le contenu de toute la map (mct)
void mct_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("mct\n");
}

/// Envoie la liste des équipes (tna)
void tna_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("tna\n");
}

/// Envoie la position d’un joueur (#n) (ppo)
void ppo_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    char buffer[100];

    snprintf(buffer, sizeof(buffer), "ppo #%d %d %d %d\n",
        client->idx, client->x, client->y, client->orientation);
    send_to_all_guis(server, buffer);
    (void)cmd;
    printf("ppo\n");
}

/// Envoie le niveau d’un joueur (#n) (plv)
void plv_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("plv\n");
}

/// Envoie l’inventaire d’un joueur (#n) (pin)
void pin_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pin\n");
}

/// Envoie le temps d’exécution d’une action (sgt)
void sgt_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("sgt\n");
}

/// Définit le temps d’exécution d’une action (sst T)
void sst_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("sst\n");
}

/// Notifie qu’un joueur a été éjecté (pex)
void pex_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pex\n");
}

/// Notifie qu’un joueur a envoyé un message (pbc)
void pbc_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pbc\n");
}

/// Notifie le début d’une incantation (pic)
void pic_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pic\n");
}

/// Notifie le résultat d’une incantation (pie)
void pie_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pie\n");
}

/// Notifie qu’un œuf a été pondu (pfk)
void pfk_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pfk\n");
}

/// Notifie qu’un joueur a déposé une ressource (pdr)
void pdr_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pdr\n");
}

/// Notifie qu’un joueur a ramassé une ressource (pgt)
void pgt_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pgt\n");
}

/// Notifie la mort d’un joueur (pdi)
void pdi_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("pdi\n");
}

/// Notifie qu’un joueur a pondu un œuf (enw)
void enw_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("enw\n");
}

/// Notifie qu’un œuf a été éclos (ebo)
void ebo_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("ebo\n");
}

/// Notifie qu’un œuf est mort (edi)
void edi_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("edi\n");
}

/// Notifie la fin du jeu (seg)
void seg_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("seg\n");
}

/// Envoie un message du serveur au GUI (smg)
void smg_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("smg\n");
}

/// Notifie une commande non autorisée (suc)
void suc_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("suc\n");
}

/// Notifie une commande invalide (sbp)
void sbp_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("sbp\n");
}


void pnw_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    char buffer[128];

    snprintf(buffer, sizeof(buffer), "pnw #%d %d %d %d %d %s\n",
        client->idx, client->x, client->y, client->orientation, client->level, server->teams[client->team_idx].name);
    send_to_all_guis(server, buffer);
    printf("pnw\n");
}
