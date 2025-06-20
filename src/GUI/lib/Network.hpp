//
// Created by aureldsk on 15/06/25.
//

#ifndef NETWORK_HPP
#define NETWORK_HPP
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "Exceptions.hpp"

class Network {
public:
    Network();
    ~Network();
    void connect(std::string, int);
    void disconnect();
    void send(const std::string &message);
    std::string receive(size_t size = 10000);
    bool isConnected() const;
private:
    int clientSocket;
    sockaddr_in serverAddr;
    bool connected;
};

#endif //NETWORK_HPP
