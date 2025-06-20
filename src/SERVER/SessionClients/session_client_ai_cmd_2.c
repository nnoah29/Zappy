/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include <stdio.h>

void broadcast_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("broadcast\n");
}

void connect_nbr_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("connect_nbr\n");
}

void fork_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("fork\n");
}

void eject_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("eject\n");
}

void take_object_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("take_object\n");
}
