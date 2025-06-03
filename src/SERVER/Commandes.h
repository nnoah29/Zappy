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

int enqueue_command(CommandQueue *queue, const char *cmd, double duration, struct timespec now);

#endif //COMMANDES_H
