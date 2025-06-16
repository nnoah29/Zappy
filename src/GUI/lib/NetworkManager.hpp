//
// Created by aureldsk on 15/06/25.
//

#ifndef NETWORKMANAGER_HPP
#define NETWORKMANAGER_HPP
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "Exceptions.hpp"

class NetworkManager {
    NetworkManager() = default;
    ~NetworkManager() = default;
public:
    void connect(std::string, int);
    void disconnect();
    void send(const std::string &message);
    std::string receive(size_t size = 1024);
    bool isConnected() const;
private:
    int clientSocket = -1;
    sockaddr_in serverAddr;
    bool connected = false;
};

#endif //NETWORKMANAGER_HPP
