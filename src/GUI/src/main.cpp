#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include "../lib/Exceptions.hpp"
#include <iostream>
#include "../lib/Network.hpp"
#include "../lib/Parser.hpp"
#include  "../lib/Game_world.hpp"
#include <string>
#include <memory>

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
    std::cout << "[DEBUG] Ajout player id=" << p.id << " team=" << p.team << " pos=(" << p.x << "," << p.y << ")" << std::endl;
    gw.addPlayer(p);
}

void Ppo(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 5)
        throw std::runtime_error("Invalid ppo");
    gw.updatePlayerPosition(
        std::stoi(oklm[1].substr(1)),
        std::stoi(oklm[2]),
        std::stoi(oklm[3]),
        std::stoi(oklm[4])
    );
}

void Plv(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid plv");
    gw.updatePlayerLevel(std::stoi(oklm[1].substr(1)), std::stoi(oklm[2]));
}

void Enw(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 5)
        throw std::runtime_error("Invalid enw");
    Egg egg;
    egg.id = (oklm[1][0] == '#') ? std::stoi(oklm[1].substr(1)) : std::stoi(oklm[1]);
    std::cout << "Egg ID: " << egg.id << std::endl;
    egg.idn = (oklm[2][0] == '#') ? std::stoi(oklm[2].substr(1)) : std::stoi(oklm[2]);
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
    Player* p = gw.findPlayer(std::stoi(oklm[1].substr(1)));
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

void Tna(const std::vector<std::string>& oklm, GameWorld& gw, Player* player)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid tna");
    gw.addTeam(oklm[1], player);
}

void Pin(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 11)
        throw std::runtime_error("Invalid pin");
    
    Player* player = gw.findPlayer(std::stoi(oklm[1].substr(1)));
    if (!player)
        return;
    
    player->inventory.food = std::stoi(oklm[4]);
    player->inventory.linemate = std::stoi(oklm[5]);
    player->inventory.deraumere = std::stoi(oklm[6]);
    player->inventory.sibur = std::stoi(oklm[7]);
    player->inventory.mendiane = std::stoi(oklm[8]);
    player->inventory.phiras = std::stoi(oklm[9]);
    player->inventory.thystame = std::stoi(oklm[10]);
    std::cout << "Inventory updated for player #" << player->id << std::endl;
}

void Pex(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid pex");
    
    int playerId = std::stoi(oklm[1].substr(1));
    std::cout << "Player #" << playerId << " expelled another player" << std::endl;
}

void Pbc(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid pbc");
    
    int playerId = std::stoi(oklm[1].substr(1));
    std::string message;
    for (size_t i = 2; i < oklm.size(); ++i) {
        if (i > 2) message += " ";
        message += oklm[i];
    }
    
    std::cout << "Player #" << playerId << " broadcasts: " << message << std::endl;
}

void Pic(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 5)
        throw std::runtime_error("Invalid pic");
    
    int x = std::stoi(oklm[1]);
    int y = std::stoi(oklm[2]);
    int level = std::stoi(oklm[3]);
    
    std::vector<int> playerIds;
    for (size_t i = 4; i < oklm.size(); ++i) {
        playerIds.push_back(std::stoi(oklm[i].substr(1)));
    }
    
    std::cout << "Incantation started at (" << x << "," << y << ") level " << level;
    std::cout << " with players:";
    for (int id : playerIds) {
        std::cout << " #" << id;
    }
    std::cout << std::endl;
}

void Pie(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 4)
        throw std::runtime_error("Invalid pie");
    
    int x = std::stoi(oklm[1]);
    int y = std::stoi(oklm[2]);
    int result = std::stoi(oklm[3]);
    
    std::cout << "Incantation ended at (" << x << "," << y << ") with result: " 
              << (result ? "SUCCESS" : "FAILURE") << std::endl;
}

void Pfk(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid pfk");
    
    int playerId = std::stoi(oklm[1].substr(1));
    std::cout << "Player #" << playerId << " laid an egg" << std::endl;
}

void Pdi(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid pdi");
    
    int playerId = std::stoi(oklm[1].substr(1));
    gw.removePlayer(playerId);
    std::cout << "Player #" << playerId << " died" << std::endl;
}

void Edi(const std::vector<std::string>& oklm, GameWorld& gw)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid edi");
    
    int eggId = std::stoi(oklm[1].substr(1));
    gw.removeEgg(eggId);
    std::cout << "Egg #" << eggId << " died" << std::endl;
}

void Sgt(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid sgt");
    
    int timeUnit = std::stoi(oklm[1]);
    std::cout << "Time unit: " << timeUnit << std::endl;
}

void Sst(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid sst");
    
    int timeUnit = std::stoi(oklm[1]);
    std::cout << "Time unit set to: " << timeUnit << std::endl;
}

void Smg(const std::vector<std::string>& oklm)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid smg");
    
    std::string message;
    for (size_t i = 1; i < oklm.size(); ++i) {
        if (i > 1) message += " ";
        message += oklm[i];
    }
    
    std::cout << "Server message: " << message << std::endl;
}

void parseMessage(const std::string& message, GameWorld& gw)
{
    std::stringstream ss(message);
    std::string line;
    std::vector<std::string> oklm;
    Player player;

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
                Tna(oklm, gw, &player);
            else if (oklm[0] == "pnw")
                Pnw(oklm, gw);
            else if (oklm[0] == "ppo")
                Ppo(oklm, gw);
            else if (oklm[0] == "plv")
                Plv(oklm, gw);
            else if (oklm[0] == "pin")
                Pin(oklm, gw);
            else if (oklm[0] == "enw")
                Enw(oklm, gw);
            else if (oklm[0] == "pdr")
                Pdr(oklm, gw);
            else if (oklm[0] == "pgt")
                Pgt(oklm, gw);
            else if (oklm[0] == "pic")
                Pic(oklm);
            else if (oklm[0] == "pie")
                Pie(oklm);
            else if (oklm[0] == "pfk")
                Pfk(oklm);
            else if (oklm[0] == "pdi")
                Pdi(oklm, gw);
            else if (oklm[0] == "edi")
                Edi(oklm, gw);
            else if (oklm[0] == "sgt")
                Sgt(oklm);
            else if (oklm[0] == "sst")
                Sst(oklm);
            else if (oklm[0] == "smg")
                Smg(oklm);
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
    auto gameWorld = std::make_shared<GameWorld>();
    Player player;
    int mapWidth = 0;
    int mapHeight = 0;
    try {
        network.connect(machine, port);
        std::string welcome = network.receive();
        std::cout << "Server welcome: " << welcome << std::endl;
        network.send("GRAPHIC\n");
        std::string reponse = network.receive();
        std::cout << reponse << std::endl;
        std::stringstream ss(reponse);
        std::string line;
        while (std::getline(ss, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            std::vector<std::string> tokens = Parser::split(line, ' ');
            if (!tokens.empty() && tokens[0] == "msz" && tokens.size() >= 3) {
                mapWidth = std::stoi(tokens[1]);
                mapHeight = std::stoi(tokens[2]);
                break;
            }
        }
        parseMessage(reponse, *gameWorld);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 84;
    }
    Core core;
    if (!core.initialize(mapWidth, mapHeight, gameWorld)) {
        std::cerr << "Failed to initialize Core system" << std::endl;
        return 84;
    }
    core.run();
    return 0;
}