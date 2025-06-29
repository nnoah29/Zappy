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

    clientSocket = socket(AF_INET, SOCK_STREAM, 0);

    if (clientSocket < 0)
        throw Error("Failed to create socket");

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip.c_str(), &serverAddr.sin_addr) <= 0) {
        close(clientSocket);
        throw Error("Invalid IP address");
    }

    if (::connect(clientSocket, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0) {
        close(clientSocket);
        throw Error("Connection failed to " + ip + ":" + std::to_string(port) + 
                   " - " + strerror(errno));
    }
    connected = true;
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
