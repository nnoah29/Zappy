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

#include "Commandes.h"
#include <stdlib.h>
#include <string.h>

void init_command_queue(CommandQueue *queue) {
    queue->head = 0;
    queue->tail = 0;
    queue->size = 0;
}

int enqueue_command(CommandQueue *queue, const char *cmd, double duration, struct timespec now)
{
    const int index = queue->tail;

    if (queue->size >= MAX_COMMANDS)
        return 0;
    queue->commands[index].raw_cmd  = strdup(cmd);
    queue->commands[index].duration = duration;
    queue->commands[index].ready_at = now;
    queue->commands[index].ready_at.tv_sec += (time_t)duration;
    queue->commands[index].ready_at.tv_nsec += (long)((duration - (int)duration) * 1e9);
    if (queue->commands[index].ready_at.tv_nsec >= 1e9) {
        queue->commands[index].ready_at.tv_sec += 1;
        queue->commands[index].ready_at.tv_nsec -= 1e9;
    }
    queue->tail = (queue->tail + 1) % MAX_COMMANDS;
    queue->size++;
    return 1;
}

int dequeue_command(CommandQueue *queue) {
    if (queue->size == 0)
        return 0;
    free(queue->commands[queue->head].raw_cmd);
    queue->commands[queue->head].raw_cmd = NULL;
    queue->head = (queue->head + 1) % MAX_COMMANDS;
    queue->size--;
    return 1;
}

Command *peek_command(CommandQueue *queue) {
    if (queue->size == 0)
        return NULL;
    return &queue->commands[queue->head];
}

int is_command_ready(Command *cmd, struct timespec now)
{
    if (!cmd)
        return 0;
    if (now.tv_sec > cmd->ready_at.tv_sec)
        return 1;
    if (now.tv_sec == cmd->ready_at.tv_sec && now.tv_nsec >= cmd->ready_at.tv_nsec)
        return 1;
    return 0;
}
