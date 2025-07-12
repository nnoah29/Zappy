/*
** EPITECH PROJECT, 2025
** GUI
** File description:
** Gui_client
*/

#ifndef GUI_CLIENT_HPP_
#define GUI_CLIENT_HPP_
#include "../Core/Core.hpp"
#include "../../lib/Exceptions.hpp"
#include "../Parser/Parser.hpp"
#include<string>
#include "../Network/Network.hpp"
#include "../World/Game_world.hpp"
#include <memory>
#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <mutex>
#include <thread>
#include <atomic>

#include "../MessageQueue/MessageQueue.hpp"
#include "../Logger/Logger.hpp"

class Gui_client {
    public:
        Gui_client(int port, const std::string &machine);
        ~Gui_client();
        void disconnect();
        void run();
        bool isDisconnected() const;
        MessageQueue& getMessageQueue() { return _messageQueue; }
    private:
    int _port;
    std::string _machine;
    std::shared_ptr<Network> _network;
    std::shared_ptr<GameWorld> _gameWorld;
    std::vector<std::string> _message;
    std::mutex _messageMutex;
    MessageQueue _messageQueue;
    std::thread _receiveThread;
    Core _core;
    std::atomic<bool> _stopRequested{false};
    void receiveMessage();
};


#endif /* !GUI_CLIENT_HPP_ */
