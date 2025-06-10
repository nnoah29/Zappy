cmake_minimum_required(VERSION 3.31)
project(SERVER C)

set(CMAKE_C_STANDARD 11)

add_executable(SERVER main.c
        Server/Server_t.c
        Server/Server_t.h
        SessionClients/SessionClient.c
        SessionClients/SessionClient.h
        Utilitaires/Utilitaires.c
        my.h
        Clock/Clock.c
        Clock/Clock.h
        Commandes/Commandes.c
        Commandes/Commandes.h
)
