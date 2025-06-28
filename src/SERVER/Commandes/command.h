/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** commandes.h
*/

#ifndef COMMANDES_H
    #define COMMANDES_H
    #define MAX_COMMANDS 10
    #define MAX_ARGS 100
    #include <time.h>
    #include "../Clock/clock.h"

typedef struct {
    char *raw_cmd;
    char **args;
    double duration;
    struct timespec ready_at;
    int argc;
} command_t;

typedef struct {
    command_t commands[MAX_COMMANDS];
    int head;
    int tail;
    int size;
} command_queue_t;

// command_queue.c
void init_command_queue(command_queue_t *queue);
int remove_command_at(command_queue_t *queue, int index);
int get_next_ready_command(command_queue_t *queue, struct timespec *now);
int enqueue_command(command_queue_t *queue, const char *cmd, double duration,
    struct timespec* now);
// command_utils.c
int is_command_ready(command_t *cmd, struct timespec *now);
void setup_command(command_queue_t *queue, const char *cmd, int index,
    double duration);
#endif //COMMANDES_H
