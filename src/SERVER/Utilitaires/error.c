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
