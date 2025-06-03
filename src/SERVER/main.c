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


#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <bits/signum-generic.h>

#include "my.h"
#include "Server.h"

int help(int ac, char **av) {
    if (ac == 2 && strcmp(av[1], "-help") == 0) {
        printf("USAGE:  ./myftp port path\n");
        printf("\tport is the port number on which the server socket listens\n");
        printf("\tpath is the path to the home directory for the Anonymous user\n");
        return 0;
    }
    fprintf(stderr, "[Error] Invalid argument\n");
    return 84;
}

configServer *parsing(int ac, char **av)
{
    configServer *server = malloc(sizeof(configServer));
    ///


    ///
    return server;
}

int main(int ac, char **av) {
    if (ac != 3)
        return help(ac, av);

    configServer *conf = parsing(ac, av);

    const int port = atoi(av[1]);
    Server *server = initServer(conf);
    runServer(server);
    closeServer(server);
    free(conf);
    return 0;
}
