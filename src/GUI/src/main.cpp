#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include "../lib/Exceptions.hpp"
#include <iostream>
#include "../lib/NetworkManager.hpp"

int main(int argc, char **argv)
{
    if (argc != 5) {
        std::cerr << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
        exit(84);
    }

    int port = -1;
    std::string machine;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-help" || arg == "--help") {
            std::cout << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
            exit(0);
        }
    }

    for (int i = 1; i < argc; i += 2) {
        std::string flag = argv[i];
        if (i + 1 >= argc) {
            std::cerr << "Error: Missing value for flag: " << flag << std::endl;
            exit(84);
        }

        if (flag == "-p") {
            try {
                port = std::stoi(argv[i + 1]);
                if (port < 0 || port > 65535) {
                    std::cerr << "Error: Port must be between 0 and 65535" << std::endl;
                    exit(84);
                }
            } catch (...) {
                std::cerr << "Error: Invalid port number: " << argv[i + 1] << std::endl;
                exit(84);
            }
        } else if (flag == "-h") {
            machine = argv[i + 1];
            if (machine.empty()) {
                std::cerr << "Error: Machine address cannot be empty" << std::endl;
                exit(84);
            }
        } else {
            std::cerr << "Error: Unknown flag: " << flag << std::endl;
            exit(84);
        }
    }

    if (port == -1) {
        std::cerr << "Error: Port not specified" << std::endl;
        exit(84);
    }
    if (machine.empty()) {
        std::cerr << "Error: Machine address not specified" << std::endl;
        exit(84);
    }

    NetworkManager networkManager;
    try {
        networkManager.connect(machine, port);
        std::string response = networkManager.receive();
        networkManager.send("GRAPHIC\n");
    } catch (const Error& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        exit(84);
    } catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << std::endl;
        exit(84);
    }
    return 0;
}