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


#ifndef SERVER_H
#define SERVER_H

#include <poll.h>
#include <netinet/in.h>
#include <poll.h>

#include "Clock.h"
#include "my.h"
#include "SessionClient.h"

#define MAX_CLIENTS 1000


typedef struct {
    int port;
    int server_fd;
    struct sockaddr_in server_addr;
    struct pollfd fds[MAX_CLIENTS];
    SessionClient clients[MAX_CLIENTS];
    Clock *clock;
    int idsGui[MAX_CLIENTS];
    configServer *config;
    int nfds;
} Server;

void runServer(Server *server);
void handle_signal(int signal);
Server *initServer(configServer *config);

#endif //SERVER_H
