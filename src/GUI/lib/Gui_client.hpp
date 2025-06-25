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
#include <mutex>
#include <thread>

class Gui_client {
    public:
        Gui_client(int port, const std::string &machine);
        ~Gui_client() = default;
        void run();
    private:
    int _port;
    std::string _machine;
    std::shared_ptr<Network> _network;
    std::shared_ptr<GameWorld> _gameWorld;
    std::vector<std::string> _message;
    std::mutex _messageMutex;
    std::thread _receiveThread;

    void parseInit(std::string);
    void receiveMessage();
};

#endif /* !GUI_CLIENT_HPP_ */
