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
} Command;

typedef struct {
    Command commands[MAX_COMMANDS];
    int head;
    int tail;
    int size;
} CommandQueue;

typedef struct  Cmd_Idx {
    int idx;
    Command *cmd;
} Cmd_Idx;

int enqueue_command(CommandQueue *queue, const char *cmd, double duration, struct timespec now);
Command *peek_command(CommandQueue *queue);
int is_command_ready(Command *cmd, struct timespec now);
int dequeue_command(CommandQueue *queue);
int get_next_ready_command(CommandQueue* queue, struct timespec now);
int remove_command_at(CommandQueue *queue, int index);

#endif //COMMANDES_H
