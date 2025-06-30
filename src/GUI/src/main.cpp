#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include "../lib/Exceptions.hpp"
#include <iostream>
#include "../lib/Network.hpp"
#include "../lib/Parser.hpp"
#include  "../lib/Game_world.hpp"
#include "../lib/Gui_client.hpp"
#include<string>

static int port = -1;
static std::string machine;

bool parseArguments(int argc, char** argv) 
{
    if (argc != 5) {
        std::cerr << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
        return false;
    }

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-help" || arg == "--help") {
            std::cout << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
            return false;
        }
    }

    for (int i = 1; i < argc; i += 2) {
        std::string flag = argv[i];
        if (i + 1 >= argc) {
            std::cerr << "Error: Missing value for flag: " << flag << std::endl;
            return false;
        }

        if (flag == "-p") {
            try {
                port = std::stoi(argv[i + 1]);
                if (port < 0 || port > 65535) {
                    std::cerr << "Error: Port must be between 0 and 65535" << std::endl;
                    return false;
                }
            } catch (...) {
                std::cerr << "Error: Invalid port number: " << argv[i + 1] << std::endl;
                return false;
            }
        } else if (flag == "-h") {
            machine = argv[i + 1];
            if (machine.empty()) {
                std::cerr << "Error: Machine address cannot be empty" << std::endl;
                return false;
            }
        } else {
            std::cerr << "Error: Unknown flag: " << flag << std::endl;
            return false;
        }
    }

    if (port == -1) {
        std::cerr << "Error: Port not specified" << std::endl;
        return false;
    }
    if (machine.empty()) {
        std::cerr << "Error: Machine address not specified" << std::endl;
        return false;
    }
    
    return true;
}

int main(int argc, char **argv) 
{
    if (!parseArguments(argc, argv))
        return 84;
    try {
        Gui_client guiClient(port, machine);
        guiClient.run();
        if (guiClient.isDisconnected())
            return 84;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 84;
    }
    return 0;
}