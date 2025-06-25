/*
** EPITECH PROJECT, 2025
** GUI
** File description:
** Gui_client
*/

#ifndef GUI_CLIENT_HPP_
#define GUI_CLIENT_HPP_
#include "Core.hpp"
#include "Exceptions.hpp"
#include "Parser.hpp"
#include<string>
#include "Network.hpp"
#include "Game_world.hpp"
#include <memory>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>

class Gui_client {
    public:
        Gui_client(int port, const std::string &machine);
        ~Gui_client() = default;
        void run();
    private:
    int _port;
    std::string _machine;
    std::shared_ptr<Network> network;
    std::shared_ptr<GameWorld> gameWorld;
    std::vector<std::string> message;
    void parseMessage();
};

#endif /* !GUI_CLIENT_HPP_ */
