/*
** EPITECH PROJECT, 2025
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
    #include "../Utilitaires/dynamic_buffer.h"


int find_client_by_fd(server_t *server, int fd);
int find_free_slot(server_t *server, session_client_t *client);
void laying_process(server_t *server, session_client_t *client, int egg_idx);
void send_initial_gui_state(server_t *server, session_client_t *gui_client);
void collect_elevating_players(server_t *server, session_client_t *client);
bool check_incantation_prerequisites(server_t *server, int x, int y,
    int level);
void check_and_finish_incantations(server_t *server);
int find_slot_incantation(server_t *server);
void write_vision(server_t *server, session_client_t *client,
    dynamic_buffer_t *db);
void distribute_message(server_t *server, session_client_t *client,
    const char *message_text);
void calculate_direction(server_t *server, session_client_t *client,
    int *x, int *y);
int process_ejection_on_entity(entity_on_tile_t *current_node,
    server_t *server, session_client_t *ejector);
int forward_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int right_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int left_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int look_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int inventory_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int broadcast_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int connect_nbr_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int fork_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int eject_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int take_object_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int set_object_f(server_t *server, session_client_t *client,
    const command_t *cmd);
int incantation_f(server_t *server, session_client_t *client,
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


int msz_h(server_t *server, session_client_t *client, const command_t *cmd);
int bct_h(server_t *server, session_client_t *client, const command_t *cmd);
int mct_h(server_t *server, session_client_t *client, const command_t *cmd);
int tna_h(server_t *server, session_client_t *client, const command_t *cmd);
int plv_h(server_t *server, session_client_t *client, const command_t *cmd);
int pin_h(server_t *server, session_client_t *client, const command_t *cmd);
int sgt_h(server_t *server, session_client_t *client, const command_t *cmd);
int sst_h(server_t *server, session_client_t *client, const command_t *cmd);
int ppo_h(server_t *server, session_client_t *client, const command_t *cmd);


#endif //SESSIONCLIENT_H
