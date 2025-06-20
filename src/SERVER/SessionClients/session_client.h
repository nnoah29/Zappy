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


int find_client_by_fd(server_t *server, int fd);
void forward_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void right_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void left_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void look_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void inventory_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void broadcast_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void connect_nbr_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void fork_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void eject_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void take_object_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void set_object_f(server_t *server, session_client_t *client,
    const command_t *cmd);
void send_to_all_guis(server_t *server, const char *msg);

void pex_f(server_t *server, session_client_t *client);
void pbc_f(server_t *server, session_client_t *client, const char *message);
void pic_f(server_t *server, session_client_t *client,
    const char *player_list_str);
void suc_f(server_t *server, session_client_t *client, const command_t *cmd);
void sbp_f(server_t *server, session_client_t *client, const command_t *cmd);
void ppo_f(server_t *server, session_client_t *client);
void pex_f(server_t *server, session_client_t *client);
void pbc_f(server_t *server, session_client_t *client, const char *message);
void pic_f(server_t *server, session_client_t *client,
    const char *player_list_str);
void pie_f(server_t *server, int x, int y, int result);
void pfk_f(server_t *server, session_client_t *player);
void pdr_f(server_t *server, session_client_t *player, int resource_idx);
void pgt_f(server_t *server, session_client_t *player, int resource_idx);
void pdi_f(server_t *server, session_client_t *player);
void enw_f(server_t *server, session_client_t *egg);
void ebo_f(server_t *server, int egg_id);
void edi_f(server_t *server, int egg_id);
void seg_f(server_t *server, const char *winning_team);
void smg_f(server_t *server, const char *message);
void pnw_f(server_t *server, session_client_t *client);
void bct_f(server_t *server, int x, int y);
void mct_f(server_t *server);


void msz_h(server_t *server, session_client_t *client, const command_t *cmd);
void bct_h(server_t *server, session_client_t *client, const command_t *cmd);
void mct_h(server_t *server, session_client_t *client, const command_t *cmd);
void tna_h(server_t *server, session_client_t *client, const command_t *cmd);
void plv_h(server_t *server, session_client_t *client, const command_t *cmd);
void pin_h(server_t *server, session_client_t *client, const command_t *cmd);
void sgt_h(server_t *server, session_client_t *client, const command_t *cmd);
void sst_h(server_t *server, session_client_t *client, const command_t *cmd);
void ppo_h(server_t *server, session_client_t *client, const command_t *cmd);


#endif //SESSIONCLIENT_H
