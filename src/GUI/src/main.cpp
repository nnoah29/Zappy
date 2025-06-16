#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include "../lib/Exceptions.hpp"
#include <iostream>
#include "../lib/NetworkManager.hpp"

int main(int argc, char **argv)
{
    try {
        if (argc != 5)
            throw Error("USAGE: ./zappy_gui -p port -h machine");

        int port = -1;
        std::string machine;
        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            if (arg == "-help" || arg == "--help") {
                std::cout << "USAGE: ./zappy_gui -p port -h machine" << std::endl;
                return 0;
            }
        }

        for (int i = 1; i < argc; i += 2) {
            std::string flag = argv[i];
            if (i + 1 >= argc)
                throw Error("Missing value for flag: " + flag);

            if (flag == "-p") {
                try {
                    port = std::stoi(argv[i + 1]);
                    if (port < 0 || port > 65535) {
                        throw Error("Port must be between 0 and 65535");
                    }
                } catch (const std::exception&) {
                    throw Error("Invalid port number: " + std::string(argv[i + 1]));
                }
            } else if (flag == "-h") {
                machine = argv[i + 1];
                if (machine.empty()) {
                    throw Error("Machine address cannot be empty");
                }
            } else {
                throw Error("Unknown flag: " + flag);
            }
        }
        if (port == -1) {
            throw Error("Port not specified");
        }
        if (machine.empty()) {
            throw Error("Machine address not specified");
        }
        NetworkManager networkManager;
        networkManager.connect(machine, port);
        networkManager.send("@ALPHIC");
        networkManager.disconnect();
    } catch (const Error& e) {
        std::cerr << "Erreur: " << e.what() << std::endl;
        return 84;
    } catch (const std::exception& e) {
        std::cerr << "Erreur inattendue: " << e.what() << std::endl;
        return 84;
    }
    return 0;
}
