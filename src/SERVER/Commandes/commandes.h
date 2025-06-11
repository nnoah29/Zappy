/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** commandes.h
*/


#ifndef COMMANDES_H
    #define COMMANDES_H
    #define MAX_COMMANDS 10
    #define MAX_ARGS 10
    #include <time.h>
    #include "../Clock/clock.h"

typedef struct {
    char *raw_cmd;
    char **args;
    double duration;
    struct timespec ready_at;
} command_t;

typedef struct {
    command_t commands[MAX_COMMANDS];
    int head;
    int tail;
    int size;
} command_queue_t;

int enqueue_command(command_queue_t *queue, const char *cmd, double duration,
    struct timespec* now);
command_t *peek_command(command_queue_t *queue);
int is_command_ready(command_t *cmd, struct timespec *now);
int dequeue_command(command_queue_t *queue);
int get_next_ready_command(command_queue_t *queue, struct timespec *now);
int remove_command_at(command_queue_t *queue, int index);
void setup_command(command_queue_t *queue, const char *cmd, int index, double duration);

#endif //COMMANDES_H
