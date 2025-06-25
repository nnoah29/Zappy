cmake_minimum_required(VERSION 3.31)
project(SERVER C)

set(CMAKE_C_STANDARD 11)

add_executable(SERVER main.c
        Server/server.h
        SessionClients/session_client_ai_cmd_1.c
        SessionClients/session_client.h
        my.h
        Clock/clock.c
        Clock/clock.h
        Commandes/command.h
        SessionClients/session_client_gui_cmd_1.c
        Map/map.h
        SessionClients/session_client_gui_notification_1.c
        SessionClients/session_client_gui_cmd_2.c
        SessionClients/session_client_gui_notification_2.c
        SessionClients/session_client_gui_notification_3.c
        SessionClients/session_client_gui_notification_4.c
        SessionClients/session_client_ai_cmd_2.c
        SessionClients/session_client_ai_cmd_3.c
        Server/server_init.c
        Server/server_network.c
        Server/server_core.c
        Server/server_command_queue.c
        Server/server_command_handler.c
        Commandes/command_queue.c
        Commandes/command_utils.c
        Utilitaires/argument_parser_core.c
        Utilitaires/argument_parser_teams.c
        Utilitaires/event_scheduler.c
        Utilitaires/client_utils.c
        Utilitaires/error.c
        Map/map_management.c
        Map/map_entities.c
        Utilitaires/look_utils.c
        Utilitaires/ai_utils.c
        Server/server_egg_utils.c
        Logger/logger.c
        Logger/logger.h
)
