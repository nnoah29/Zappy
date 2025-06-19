/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.h
*/

#ifndef SESSIONCLIENT_H
    #define SESSIONCLIENT_H
    #include <stdbool.h>
    #include <time.h>
    #include "../my.h"
    #include "../Server/server.h"


void forward_f(server_t *server, session_client_t *client, const command_t *cmd);
void right_f(server_t *server, session_client_t *client, const command_t *cmd);
void left_f(server_t *server, session_client_t *client, const command_t *cmd);
void look_f(server_t *server, session_client_t *client, const command_t *cmd);
void inventory_f(server_t *server, session_client_t *client, const command_t *cmd);
void broadcast_f(server_t *server, session_client_t *client, const command_t *cmd);
void connect_nbr_f(server_t *server, session_client_t *client, const command_t *cmd);
void fork_f(server_t *server, session_client_t *client, const command_t *cmd);
void eject_f(server_t *server, session_client_t *client, const command_t *cmd);
void take_object_f(server_t *server, session_client_t *client, const command_t *cmd);
void set_object_f(server_t *server, session_client_t *client, const command_t *cmd);
void msz_f(server_t *server, session_client_t *client, const command_t *cmd);
void bct_f(server_t *server, session_client_t *client, const command_t *cmd);
void mct_f(server_t *server, session_client_t *client, const command_t *cmd);
void tna_f(server_t *server, session_client_t *client, const command_t *cmd);
void ppo_f(server_t *server, session_client_t *client, const command_t *cmd);
void plv_f(server_t *server, session_client_t *client, const command_t *cmd);
void pin_f(server_t *server, session_client_t *client, const command_t *cmd);
void sgt_f(server_t *server, session_client_t *client, const command_t *cmd);
void sst_f(server_t *server, session_client_t *client, const command_t *cmd);
void pex_f(server_t *server, session_client_t *client, const command_t *cmd);
void pbc_f(server_t *server, session_client_t *client, const command_t *cmd);
void pic_f(server_t *server, session_client_t *client, const command_t *cmd);
void pie_f(server_t *server, session_client_t *client, const command_t *cmd);
void pfk_f(server_t *server, session_client_t *client, const command_t *cmd);
void pdr_f(server_t *server, session_client_t *client, const command_t *cmd);
void pgt_f(server_t *server, session_client_t *client, const command_t *cmd);
void pdi_f(server_t *server, session_client_t *client, const command_t *cmd);
void enw_f(server_t *server, session_client_t *client, const command_t *cmd);
void ebo_f(server_t *server, session_client_t *client, const command_t *cmd);
void edi_f(server_t *server, session_client_t *client, const command_t *cmd);
void seg_f(server_t *server, session_client_t *client, const command_t *cmd);
void smg_f(server_t *server, session_client_t *client, const command_t *cmd);
void suc_f(server_t *server, session_client_t *client, const command_t *cmd);
void sbp_f(server_t *server, session_client_t *client, const command_t *cmd);
void pnw_f(server_t *server, session_client_t *client, const command_t *cmd);


#endif //SESSIONCLIENT_H
