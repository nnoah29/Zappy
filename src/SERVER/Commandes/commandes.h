/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 02/06/25.                                          
**         |___/ 
*/


#ifndef COMMANDES_H
#define COMMANDES_H

#define MAX_COMMANDS 10
#include <time.h>
#include "../Clock/Clock.h"

typedef struct {
    char *raw_cmd;
    double duration;
    struct timespec ready_at;
} command_t;

typedef struct {
    command_t commands[MAX_COMMANDS];
    int head;
    int tail;
    int size;
} command_queue_t;

int enqueue_command(command_queue_t *queue, const char *cmd, double duration, struct timespec now);
command_t *peek_command(command_queue_t *queue);
int is_command_ready(command_t *cmd, struct timespec now);
int dequeue_command(command_queue_t *queue);
int get_next_ready_command(command_queue_t* queue, struct timespec now);
int remove_command_at(command_queue_t *queue, int index);

#endif //COMMANDES_H
