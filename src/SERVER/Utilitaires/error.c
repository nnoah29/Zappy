/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** error.c
*/

#include <stdio.h>
#include <stdlib.h>
#include "../my.h"

void exit_error(char *error, int degree)
{
    LOG(LOG_ERROR, "%s", error);
    exit(degree);
}

int fail_cmd(int fd)
{
    dprintf(fd, "ko\n");
    return 84;
}

void error_msg_eggs_init(server_t *s, int eggs_created, int team_idx)
{
    LOG(LOG_ERROR, "N'a pu créer que %d/%d œufs pour "
        "l'équipe '%s'. Pas assez de slots.\n", eggs_created,
        s->teams[team_idx].nbEggs, s->teams[team_idx].name);
}
