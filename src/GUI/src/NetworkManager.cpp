//
// Created by aureldsk on 16/06/25.
//

#include "../lib/NetworkManager.hpp"

void NetworkManager::connect(std::string ip, int port) {
    if (connected) {
        throw Error("Already connected");
    }

    clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket < 0) {
        throw Error("Failed to create socket");
    }

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip.c_str(), &serverAddr.sin_addr) <= 0) {
        close(clientSocket);
        throw Error("Invalid IP address");
    }

    if (::connect(clientSocket, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) < 0) {
        close(clientSocket);
        throw Error("Connection failed");
    }

    connected = true;
}
void NetworkManager::disconnect() {
    if (!connected) {
        throw Error("Not connected");
    }
    close(clientSocket);
    connected = false;
}

void NetworkManager::send(const std::string &message) {
    if (!connected) {
        throw Error("Not connected");
    }
    ssize_t bytesSent = ::send(clientSocket, message.c_str(), message.size(), 0);
    if (bytesSent < 0) {
        throw Error("Failed to send message");
    }
}
std::string NetworkManager::receive(size_t size) {
    if (!connected) {
        throw Error("Not connected");
    }
    char buffer[size];
    ssize_t bytesReceived = recv(clientSocket, buffer, size - 1, 0);
    if (bytesReceived < 0) {
        throw Error("Failed to receive message");
    }
    buffer[bytesReceived] = '\0'; // Null-terminate the string
    return std::string(buffer);
}
bool NetworkManager::isConnected() const {
    return connected;
}