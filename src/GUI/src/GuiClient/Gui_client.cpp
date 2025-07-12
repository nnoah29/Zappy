/*
** EPITECH PROJECT, 2025
** GUI
** File description:
** Gui_client
*/

#include "Gui_client.hpp"

Gui_client::Gui_client(int port, const std::string &machine)
    : _port(port), _machine(machine), _network(std::make_shared<Network>()),
      _gameWorld(std::make_shared<GameWorld>()) {
}

bool Gui_client::isDisconnected() const
{ 
    return !_network->isConnected();
}


void Gui_client::receiveMessage()
{
    while (_network->isConnected()) {
        try {
            std::string message = _network->receive();

            if (message.empty()) {
                _core.setDisconnected();
                break;
            }
            _messageQueue.push(message);
        } catch (const std::exception& e) {
            LOG(Logger::LogLevel::ERROR, "Network receive error: %s", e.what());
            _core.setDisconnected();
            break;
        }
    }
    LOG(Logger::LogLevel::INFO, "Network thread is shutting down.");
}

Gui_client::~Gui_client() {
    disconnect();
}

void Gui_client::disconnect() {
    if (_network) {
        _network->disconnect();
    }
    if (_receiveThread.joinable()) {
        _receiveThread.join();
    }
}

void Gui_client::run() 
{
    try {
        _network->connect(_machine, _port);
        const std::string welcome = _network->receive();
        std::cout << "Server welcome: " << welcome << std::endl;
        _network->send("GRAPHIC\n");

        _gameWorld->setNetwork(_network);
        if (!_core.initialize(_gameWorld, *this)) {
            std::cerr << "Failed to initialize Core system" << std::endl;
            return;
        }
        _receiveThread = std::thread(&Gui_client::receiveMessage, this);
        _core.run();
        if (_receiveThread.joinable())
            _receiveThread.join();
    } catch (const std::exception &e) {
        LOG(Logger::LogLevel::ERROR, e.what());
        if (_receiveThread.joinable())
            _receiveThread.join();
        throw std::runtime_error("Failed to run GUI client");
    }
}
