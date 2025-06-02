cmake_minimum_required(VERSION 3.31)
project(SERVER C)

set(CMAKE_C_STANDARD 11)

add_executable(SERVER main.c
        Server.c
        Server.h
        SessionClient.c
        SessionClient.h
        Utilitaires.c
        my.h
)
