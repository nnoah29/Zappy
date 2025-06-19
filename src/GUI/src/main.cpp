#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include "../lib/Exceptions.hpp"
#include <iostream>
#include "../lib/Network.hpp"
#include "../lib/Threads.hpp"
#include "../lib/Parser.hpp"

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

void parseMessage(const std::string& message) 
{
    std::string messagecl = message;
    messagecl.erase(std::remove(messagecl.begin(), messagecl.end(), '\r'), messagecl.end());
    messagecl.erase(std::remove(messagecl.begin(), messagecl.end(), '\n'), messagecl.end());
    
    auto command = Parser::splitCommand(messagecl);
    
    std::cout << "[" << command.cmd << "] ";
    for (const auto& arg : command.args) 
        std::cout << arg << " ";
    std::cout << "\n";
    
    if (command.cmd == "msz" && command.args.size() >= 2)
        std::cout << ">>> Map size: " << command.args[0] << "x" << command.args[1] << "\n";
    else if (command.cmd == "bct" && command.args.size() >= 9)
        std::cout << ">>> Tile content at (" << command.args[0] << "," << command.args[1] << ")\n";
    else if (command.cmd == "pnw" && command.args.size() >= 6)
        std::cout << ">>> New player #" << command.args[0] << " from team " << command.args[5] << "\n";
    else if (command.cmd == "seg")
        std::cout << "\n>>> WINNING TEAM: " << (command.args.empty() ? "Unknown" : command.args[0]) << "\n\n";
}

int main(int argc, char **argv) 
{
    if (!parseArguments(argc, argv))
        return 84;

    Network network;
    try {
        network.connect(machine, port);
        std::string welcome = network.receive();
        std::cout << "Server welcome: " << welcome << std::endl;
        
        network.send("GRAPHIC\n");
        std::string reponse = network.receive();
        Threads threads(network);
        threads.setMessage(parseMessage);
        threads.start();
        std::cout << "\nGUI started. Waiting for server commands...\n";
        std::cout << "Press Ctrl+C to exit\n\n";
        while (threads.isRunning()) {
            threads.processMessages();
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 84;
    }
    
    return 0;
}