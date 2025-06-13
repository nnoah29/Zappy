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

// static const  option_parser_t parsers[] = {
//     {"-p", parse_port},
//     {"-x", parse_width},
//     {"-y", parse_height},
//     {"-n", parse_names},
//     {"-c", parse_clients},
//     {"-f", parse_freq},
//     {NULL, NULL}
// };

// void gui_protocol(server_t *server, session_client_t *client, char *cmd)
// {
//     if (*cmd == "msz") {

//     }
// }

void msz_function(server_t *server, session_client_t *client, const command_t *cmd)
{
    // printf("msz %d %d\n", cmd.);
}

void bct(config_server_t *server_, server_t *server, session_client_t *client, char *cmd)
{
    printf("bct %d %d\n", server_->map_h, server_->map_w);
    printf("bct %d %d\n", server_->map_h, server_->map_w);
    printf("bct %d %d\n", server_->map_h, server_->map_w);

}

void msz(config_server_t *server_, server_t *server, session_client_t *client, char *cmd)
{
    printf("msz %d %d\n", server_->map_h, server_->map_w);
}