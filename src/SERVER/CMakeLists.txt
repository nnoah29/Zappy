cmake_minimum_required(VERSION 3.31)
project(SERVER C)

set(CMAKE_C_STANDARD 11)

add_executable(SERVER main.c
        Server/server.c
        Server/server.h
        SessionClients/session_client.c
        SessionClients/session_client.h
        my.h
        Clock/clock.c
        Clock/clock.h
        Commandes/commandes.c
        Commandes/commandes.h
        Server/server.c
        Utilitaires/utilitaires.c
        Utilitaires/utilitaires_2.c
        Server/server_2.c
        Server/server_3.c
        Server/server_4.c
        Server/server_5.c
        Commandes/commandes_2.c
)
