//
// Created by aureldsk on 16/06/25.
//

#include "../lib/Network.hpp"

#include <cstring>
#include <string>

Network::Network(): clientSocket(-1), connected(false)
{
    memset(&serverAddr, 0, sizeof(serverAddr));
}

Network::~Network()
{
    disconnect();
}


void Network::connect(std::string ip, int port)
{
    if (connected)
        throw Error("Already connected");

    struct addrinfo hints{}, *res, *p;
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    std::string portStr = std::to_string(port);
    if (getaddrinfo(ip.c_str(), portStr.c_str(), &hints, &res) != 0)
        throw Error("Failed to resolve host: " + ip);

    for (p = res; p != nullptr; p = p->ai_next) {
        clientSocket = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (clientSocket < 0)
            continue;
        if (::connect(clientSocket, p->ai_addr, p->ai_addrlen) == 0) {
            connected = true;
            break;
        }
        close(clientSocket);
        clientSocket = -1;
    }

    freeaddrinfo(res);

    if (!connected)
        throw Error("Connection failed to " + ip + ":" + portStr + " - " + strerror(errno));
}

void Network::disconnect()
{
     if (connected) {
        close(clientSocket);
        connected = false;
    }
}

void Network::send(const std::string &message)
{
    if (!connected)
        throw Error("Not connected");
    ssize_t bytesS = ::send(clientSocket, message.c_str(), message.size(), 0);
    if (bytesS < 0)
        throw Error("Failed to send message");
}

std::string Network::receive(size_t size)
{
    if (!connected)
        throw Error("Not connected");
    char buffer[size];
    ssize_t bytesR = recv(clientSocket, buffer, size - 1, 0);
    if (bytesR < 0)
        throw Error("Failed to receive message");
    buffer[bytesR] = '\0';
    return std::string(buffer);
}
bool Network::isConnected() const
{
    return connected;
}
