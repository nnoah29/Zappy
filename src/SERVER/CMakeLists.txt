cmake_minimum_required(VERSION 3.31)
project(SERVER C)

set(CMAKE_C_STANDARD 11)

add_executable(SERVER main.c
        Server/server.c
        Server/server.h
        SessionClients/sessionClient.c
        SessionClients/sessionClient.h
        my.h
        Clock/Clock.c
        Clock/Clock.h
        Commandes/commandes.c
        Commandes/commandes.h
        Server/server.c
        Utilitaires/utilitaires.c
        Utilitaires/utilitaires_2.c
)
