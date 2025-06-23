#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include "../lib/Exceptions.hpp"
#include <iostream>
#include "../lib/Network.hpp"
#include "../lib/Parser.hpp"
#include  "../lib/Game_world.hpp"
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

void Msz(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid msz");
    gw.initialize(std::stoi(oklm[1]), std::stoi(oklm[2]));
}

void Bct(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 10)
        throw std::runtime_error("Invalid bct");
    Resource res;
    res.food = std::stoi(oklm[3]);
    std::cout << "food: " << res.food << std::endl;
    res.linemate = std::stoi(oklm[4]);
    std::cout << "linemate: " << res.linemate << std::endl;
    res.deraumere = std::stoi(oklm[5]);
    std::cout << "deraumere: " << res.deraumere << std::endl;
    res.sibur = std::stoi(oklm[6]);
    std::cout << "sibur: " << res.sibur << std::endl;
    res.mendiane = std::stoi(oklm[7]);
    std::cout << "mendiane: " << res.mendiane << std::endl;
    res.phiras = std::stoi(oklm[8]);
    std::cout << "phiras: " << res.phiras << std::endl;
    res.thystame = std::stoi(oklm[9]);
    std::cout << "thystame: " << res.thystame << std::endl;
    gw.updateTileResources(std::stoi(oklm[1]), std::stoi(oklm[2]), res);
    std::cout << "Tile at (" << oklm[1] << ", " << oklm[2] << ") updated with resources." << std::endl;
}

void Pnw(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 7)
        throw std::runtime_error("Invalid pnw");
    Player p;
    p.id = std::stoi(oklm[1].substr(1));
    p.x = std::stoi(oklm[2]);
    p.y = std::stoi(oklm[3]);
    p.orientation = std::stoi(oklm[4]);
    p.level = std::stoi(oklm[5]);
    p.team = oklm[6];
    gw.addPlayer(p);
}

void Ppo(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 5)
        throw std::runtime_error("Invalid ppo");
    gw.updatePlayerPosition(
        std::stoi(oklm[1]),
        std::stoi(oklm[2]),
        std::stoi(oklm[3]),
        std::stoi(oklm[4])
    );
}

void Plv(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid plv");
    gw.updatePlayerLevel(std::stoi(oklm[1]), std::stoi(oklm[2]));
}

void Enw(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 5)
        throw std::runtime_error("Invalid enw");
    Egg egg;
    egg.id = std::stoi(oklm[1].substr(1));
    std::cout << "Egg ID: " << egg.id << std::endl;
    egg.idn = std::stoi(oklm[2].substr(1));
    std::cout << "Player Id: " << egg.idn << std::endl;
    egg.x = std::stoi(oklm[3]);
    std::cout << "Egg X: " << egg.x << std::endl;
    egg.y = std::stoi(oklm[4]);
    std::cout << "Egg Y: " << egg.y << std::endl;
    gw.addEgg(egg);
}

void Pdr(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid pdr");
    Player* p = gw.findPlayer(std::stoi(oklm[1]));
    if (p)
        gw.updateResource(p->x, p->y, std::stoi(oklm[2]), 1);
}

void Pgt(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid pgt");
    Player* p = gw.findPlayer(std::stoi(oklm[1]));
    if (p)
        gw.updateResource(p->x, p->y, std::stoi(oklm[2]), -1);
}

void Tna(const std::vector<std::string>& oklm, Player& player)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid tna");
    player.team = oklm[1];
    std::cout << "Team " << player.team << " added." << std::endl;
}
void parseMessage(const std::string& message, GameWorld& gw, Player& player)
{
    std::stringstream ss(message);
    std::string line;
    std::vector<std::string> oklm;

    while (std::getline(ss, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        oklm = Parser::split(line, ' ');
        if (oklm.empty())
            continue;
        try {
            if (oklm[0] == "msz") 
                Msz(oklm, gw);
            else if (oklm[0] == "bct")
                Bct(oklm, gw);
            else if (oklm[0] == "tna")
                Tna(oklm, player);
            else if (oklm[0] == "pnw")
                Pnw(oklm, gw);
            else if (oklm[0] == "ppo")
                Ppo(oklm, gw);
            else if (oklm[0] == "plv")
                Plv(oklm, gw);
            else if (oklm[0] == "pin")
                std::cout<<"Inventory"<<std::endl;
            else if (oklm[0] == "enw")
                Enw(oklm, gw);
            else if (oklm[0] == "pdr")
                Pdr(oklm, gw);
            else if (oklm[0] == "pgt")
                Pgt(oklm, gw);
            else if (oklm[0] == "pic")
                std::cout<<"start of incantation"<<std::endl;
            else if (oklm[0] == "pie")
                std::cout<<"end of incantation"<<std::endl;
            else if (oklm[0] == "seg") std::cout << "Winner: " << oklm[1] << "\n";
        } catch (const std::exception& e) {
            std::cerr << "Parse error: " << e.what() << "\n";
        }
    }
}

int main(int argc, char **argv) 
{
    if (!parseArguments(argc, argv))
        return 84;

    Network network;
    GameWorld gameWorld;
    Player player;
    try {
        network.connect(machine, port);
        std::string welcome = network.receive();
        std::cout << "Server welcome: " << welcome << std::endl;
        network.send("GRAPHIC\n");
        std::string reponse = network.receive();
        std::cout << reponse << std::endl;
        parseMessage(reponse, gameWorld, player);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 84;
    }
    // Core core;
    // if (!core.initialize()) {
    //     std::cerr << "Failed to initialize Core system" << std::endl;
    //     return 84;
    // }
    // core.run();
    return 0;
}