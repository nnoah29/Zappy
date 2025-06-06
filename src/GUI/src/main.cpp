#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include <iostream>

int main(int argc, char **argv)
{
    if (argc != 5) {
        std::cout << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
        return 0;
    }
    for (int i = 1; i < argc; ++i) {
        if (std::string(argv[i]) == "-help" || std::string(argv[i]) == "--help") {
            std::cout << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
            return 0;
        }
    }
    int port = -1;
    std::string machine;
    for (int i = 1; i < argc; i += 2) {
        if (std::string(argv[i]) == "-p" && i + 1 < argc) {
            port = std::stoi(argv[i + 1]);
        } else if (std::string(argv[i]) == "-h" && i + 1 < argc) {
            machine = argv[i + 1];
        }
    }
    if (port == -1 || machine.empty()) {
        std::cout << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
        return 0;
    }
    Core gameCore;     
    std::cout << "Starting game loop..." << std::endl;
    gameCore.initialize();
    gameCore.run();
    std::cout << "Game loop ended." << std::endl;
    
    return 0;
}
