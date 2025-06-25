/*
** EPITECH PROJECT, 2025
** GUI
** File description:
** Gui_client
*/

#include "../lib/Gui_client.hpp"

Gui_client::Gui_client(int port, const std::string &machine)
    : _port(port), _machine(machine), _network(std::make_shared<Network>()),
      _gameWorld(std::make_shared<GameWorld>()) {
}

void Msz(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid msz");
    gw->initialize(std::stoi(oklm[1]), std::stoi(oklm[2]));
}

void Bct(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
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
    gw->updateTileResources(std::stoi(oklm[1]), std::stoi(oklm[2]), res);
    std::cout << "Tile at (" << oklm[1] << ", " << oklm[2] << ") updated with resources." << std::endl;
}

void Pnw(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
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
    gw->addPlayer(p);
}

void Ppo(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 5)
        throw std::runtime_error("Invalid ppo");
    gw->updatePlayerPosition(
        std::stoi(oklm[1].substr(1)),
        std::stoi(oklm[2]),
        std::stoi(oklm[3]),
        std::stoi(oklm[4])
    );
}

void Plv(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid plv");
    gw->updatePlayerLevel(std::stoi(oklm[1].substr(1)), std::stoi(oklm[2]));
}

void Enw(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
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
    gw->addEgg(egg);
}

void Pdr(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid pdr");
    Player* p = gw->findPlayer(std::stoi(oklm[1].substr(1)));
    if (p)
        gw->updateResource(p->x, p->y, std::stoi(oklm[2]), 1);
}

void Pgt(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 3)
        throw std::runtime_error("Invalid pgt");
    Player* p = gw->findPlayer(std::stoi(oklm[1]));
    if (p)
        gw->updateResource(p->x, p->y, std::stoi(oklm[2]), -1);
}

void Tna(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw, Player* player)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid tna");
    gw->addTeam(oklm[1], player);
}

void Pin(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 11)
        throw std::runtime_error("Invalid pin");
    
    Player* player = gw->findPlayer(std::stoi(oklm[1].substr(1)));
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

void Pdi(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid pdi");
    
    int playerId = std::stoi(oklm[1].substr(1));
    gw->removePlayer(playerId);
    std::cout << "Player #" << playerId << " died" << std::endl;
}

void Edi(const std::vector<std::string>& oklm, std::shared_ptr<GameWorld> gw)
{
    if (oklm.size() < 2)
        throw std::runtime_error("Invalid edi");
    
    int eggId = std::stoi(oklm[1].substr(1));
    gw->removeEgg(eggId);
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
        if (i > 1)
            message += " ";
        message += oklm[i];
    }
    std::cout << "Server message: " << message << std::endl;
}

void Gui_client::parseMessage(std::string init)
{
    std::stringstream ss(init);
    std::string line;
    std::vector<std::string> tab;
    Player player;

    while (std::getline(ss, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        tab = Parser::split(line, ' ');
        if (tab.empty())
            continue;
        try {
            if (tab[0] == "msz") 
                Msz(tab, _gameWorld);
            else if (tab[0] == "bct")
                Bct(tab, _gameWorld);
            else if (tab[0] == "tna")
                Tna(tab, _gameWorld, &player);
            else if (tab[0] == "pnw")
                Pnw(tab, _gameWorld);
            else if (tab[0] == "ppo")
                Ppo(tab, _gameWorld);
            else if (tab[0] == "plv")
                Plv(tab, _gameWorld);
            else if (tab[0] == "pin")
                Pin(tab, _gameWorld);
            else if (tab[0] == "enw")
                Enw(tab, _gameWorld);
            else if (tab[0] == "pdr")
                Pdr(tab, _gameWorld);
            else if (tab[0] == "pgt")
                Pgt(tab, _gameWorld);
            else if (tab[0] == "pic")
                Pic(tab);
            else if (tab[0] == "pie")
                Pie(tab);
            else if (tab[0] == "pfk")
                Pfk(tab);
            else if (tab[0] == "pdi")
                Pdi(tab, _gameWorld);
            else if (tab[0] == "edi")
                Edi(tab, _gameWorld);
            else if (tab[0] == "sgt")
                Sgt(tab);
            else if (tab[0] == "sst")
                Sst(tab);
            else if (tab[0] == "smg")
                Smg(tab);
            else if (tab[0] == "seg") std::cout << "Winner: " << tab[1] << "\n";
        } catch (const std::exception& e) {
            std::cerr << "Parse error: " << e.what() << "\n";
        }
    }
}

void Gui_client::receiveMessage()
{
    while (true) {
        std::string message = _network->receive();
        if (message.empty()) {
            std::cerr << "Connection lost or empty message received." << std::endl;
            break;
        }
        std::cout << message << std::endl;
        _messageMutex.lock();
        _message.push_back(message);
        _messageMutex.unlock();
        if (message == "seg") {
            std::cout << "Game over. Exiting..." << std::endl;
            _network->disconnect();
            break;
        }
    }
}

void Gui_client::run() 
{
    try {
        _network->connect(_machine, _port);
        std::string welcome = _network->receive();
        std::cout << "Server welcome: " << welcome << std::endl;
        _network->send("GRAPHIC\n");
        std::string init = _network->receive();
        std::cout << init << std::endl;
        parseMessage(init);
        _receiveThread = std::thread(&Gui_client::receiveMessage, this);
        if (_receiveThread.joinable())
            _receiveThread.join();
    } catch (const std::exception &e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}