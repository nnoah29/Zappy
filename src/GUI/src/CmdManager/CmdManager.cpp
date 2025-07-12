/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 08/07/25.                                          
**         |___/ 
*/
#include "../GuiClient/Gui_client.hpp"

void Msz(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 3)
        throw std::runtime_error("Invalid msz");
    LOG(Logger::LogLevel::DEBUG, "Map size set to: %d x %d", std::stoi(tokens[1]), std::stoi(tokens[2]));
    gw->initialize(std::stoi(tokens[1]), std::stoi(tokens[2]));
}

void Bct(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 10)
        throw std::runtime_error("Invalid bct");
    Resource res;
    const int x = std::stoi(tokens[1]);
    const int y = std::stoi(tokens[2]);
    res.food = std::stoi(tokens[3]);
    res.linemate = std::stoi(tokens[4]);
    res.deraumere = std::stoi(tokens[5]);
    res.sibur = std::stoi(tokens[6]);
    res.mendiane = std::stoi(tokens[7]);
    res.phiras = std::stoi(tokens[8]);
    res.thystame = std::stoi(tokens[9]);
    gw->updateTileResources(x, y, res);
    LOG(Logger::LogLevel::DEBUG, "Tile at (%d, %d) updated with resources.", x, y);

}

void Pnw(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 7)
        throw std::runtime_error("Invalid pnw");
    Player p;
    p.id = std::stoi(tokens[1].substr(1));
    p.x = std::stoi(tokens[2]);
    p.y = std::stoi(tokens[3]);
    p.orientation = std::stoi(tokens[4]);
    p.level = std::stoi(tokens[5]);
    p.team = tokens[6];
    gw->addPlayer(p);

}

void Ppo(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 5)
        throw std::runtime_error("Invalid ppo");
    gw->updatePlayerPosition(
        std::stoi(tokens[1].substr(1)),
        std::stoi(tokens[2]),
        std::stoi(tokens[3]),
        std::stoi(tokens[4])
    );
}

void Plv(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 3)
        throw std::runtime_error("Invalid plv");
    gw->updatePlayerLevel(std::stoi(tokens[1].substr(1)), std::stoi(tokens[2]));
}

void Enw(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 5)
        throw std::runtime_error("Invalid enw");
    Egg egg;
    egg.id = ( tokens[1][0] == '#') ? std::stoi(tokens[1].substr(1)) : std::stoi(tokens[1]);
    egg.idn = (tokens[2][0] == '#') ? std::stoi(tokens[2].substr(1)) : std::stoi(tokens[2]);
    egg.x = std::stoi(tokens[3]);
    egg.y = std::stoi(tokens[4]);
    gw->addEgg(egg);
}

void Pdr(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 3)
        throw std::runtime_error("Invalid pdr");
    Player* p = gw->findPlayer(std::stoi(tokens[1].substr(1)));
    if (p)
        gw->updateResource(p->x, p->y, static_cast<GameWorld::ResourceType>(std::stoi(tokens[2])), 1);
}

void Pgt(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 3)
        throw std::runtime_error("Invalid pgt");
    const int res = std::stoi(tokens[2]);
    const Player* p = gw->findPlayer(std::stoi(tokens[1].substr(1)));
    if (p)
        gw->updateResource(p->x, p->y, static_cast<GameWorld::ResourceType>(res), -1);
    LOG(Logger::LogLevel::DEBUG, "Player #%d resource updated at (%d, %d) for resource type: %d", p->id, p->x, p->y, res);
}

void Tna(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid tna");
    gw->addTeam(tokens[1]);
}

void Pin(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 11)
        throw std::runtime_error("Invalid pin");

    const int playerId = std::stoi(tokens[1].substr(1));
    LOG(Logger::LogLevel::DEBUG, "Pin received for player #%d", playerId);
    Player* player = gw->findPlayer(playerId);
    if (!player) {
        LOG(Logger::LogLevel::WARN, "Pin: Player not found in GameWorld for id: %d", playerId);
        return;
    }
    PlayerInventory inv;
    inv.food = std::stoi(tokens[4]);
    inv.linemate = std::stoi(tokens[5]);
    inv.deraumere = std::stoi(tokens[6]);
    inv.sibur = std::stoi(tokens[7]);
    inv.mendiane = std::stoi(tokens[8]);
    inv.phiras = std::stoi(tokens[9]);
    inv.thystame = std::stoi(tokens[10]);
    LOG(Logger::LogLevel::DEBUG, "Updating inventory for player #%d", playerId);
    gw->updatePlayerInventory(playerId, inv);
}

void Pex(const std::vector<std::string>& tokens, Core& core) // 'core' est maintenant utilisé !
{
    if (tokens.size() < 2) throw std::runtime_error("Invalid pex");

    const int playerId = std::stoi(tokens[1].substr(1));
    LOG(Logger::LogLevel::INFO, "Player #%d was expelled.", playerId);

    GameWorld* world = core.getGameWorld();
    const RenderingEngine* renderer = core.getRenderingEngine();
    AnimationSystem* animSystem = core.getAnimationSystem();

    if (!world || !renderer || !animSystem) return;

    Player* player = world->findPlayer(playerId);
    if (player) {
        sf::Vector2f screenPos = renderer->tileToScreen(player->x, player->y);
        screenPos.x += RenderingEngine::getTileSize() / 2.0f;
        screenPos.y += RenderingEngine::getTileSize() / 2.0f;

        animSystem->addEffect(AnimationType::PLAYER_EJECT, screenPos.x, screenPos.y, 1.5f, sf::Color(255, 80, 80));
    }
}


void Pbc(const std::vector<std::string>& tokens)
{
    if (tokens.size() < 3)
        throw std::runtime_error("Invalid pbc");

    int playerId = std::stoi(tokens[1].substr(1));
    std::string message;
    for (size_t i = 2; i < tokens.size(); ++i) {
        if (i > 2) message += " ";
        message += tokens[i];
    }
    LOG(Logger::LogLevel::DEBUG, "Player #%d broadcasts: %s", playerId, message.c_str());
}

void Pic(const std::vector<std::string>& tokens, Core& core)
{
    if (tokens.size() < 4)
        throw std::runtime_error("Invalid pic format");

    const int x = std::stoi(tokens[1]);
    const int y = std::stoi(tokens[2]);
    const int level = std::stoi(tokens[3]);

    const RenderingEngine* renderer = core.getRenderingEngine();
    AnimationSystem *animSystem = core.getAnimationSystem();

    if (renderer && animSystem) {
        sf::Vector2f screenPos = renderer->tileToScreen(x, y);
        screenPos.x += renderer->getTileSize() / 2.0f;
        screenPos.y += renderer->getTileSize() / 2.0f;

        const AnimationId id = AnimationSystem::makeAnimationId(x, y);
        animSystem->startPersistentEffect(id, AnimationType::INCANTATION, screenPos.x, screenPos.y, sf::Color::Magenta);

        std::vector<int> playerIds;
        for (size_t i = 4; i < tokens.size(); ++i) {
            playerIds.push_back(std::stoi(tokens[i].substr(1)));
        }
        std::string oss = "Incantation started at (" + std::to_string(x) + "," + std::to_string(y) + ") level " +
            std::to_string(level) + " with players:";
        for (const int playerId : playerIds) {
            oss += " #" + std::to_string(playerId);
        }
        LOG(Logger::LogLevel::DEBUG, oss.c_str());
    }
}

void Pie(const std::vector<std::string>& tokens, Core& core) {
    if (tokens.size() < 4)
        throw std::runtime_error("Invalid pie format");

    const int x = std::stoi(tokens[1]);
    const int y = std::stoi(tokens[2]);
    const bool success = (std::stoi(tokens[3]) == 1);

    AnimationSystem *animSystem = core.getAnimationSystem();
    if (animSystem) {
        const AnimationId id = AnimationSystem::makeAnimationId(x, y);
        animSystem->stopPersistentEffect(id, success);
        LOG(Logger::LogLevel::DEBUG, "Incantation ended at (%d, %d) with result: %s", x,
            y, success ? "SUCCESS" : "FAILURE");
    }
}

void Pfk(const std::vector<std::string>& tokens)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid pfk");

    const int playerId = std::stoi(tokens[1].substr(1));
    LOG(Logger::LogLevel::DEBUG, "Player #%d laid an egg", playerId);
}

void Pdi(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid pdi");

    const int playerId = std::stoi(tokens[1].substr(1));
    gw->removePlayer(playerId);
    LOG(Logger::LogLevel::INFO, "Player #%d died", playerId);
}

void Edi(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid edi");

    const int eggId = std::stoi(tokens[1].substr(1));
    gw->removeEgg(eggId);
    LOG(Logger::LogLevel::DEBUG, "Egg, #%d died");
}

void Ebo(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid ebo");
    const int eggId = std::stoi(tokens[1].substr(1));
    gw->removeEgg(eggId);
    LOG(Logger::LogLevel::DEBUG, "Egg, Player connected for egg #%d", eggId);
}

void Sgt(const std::vector<std::string>& tokens)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid sgt");

    const int timeUnit = std::stoi(tokens[1]);
    LOG(Logger::LogLevel::DEBUG, "Server time unit set to: %d", timeUnit);
}

void Sst(const std::vector<std::string>& tokens)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid sst");

    const int timeUnit = std::stoi(tokens[1]);
    LOG(Logger::LogLevel::DEBUG, "Time unit set to: %d", timeUnit);
}

void Smg(const std::vector<std::string>& tokens)
{
    if (tokens.size() < 2)
        throw std::runtime_error("Invalid smg");

    std::string message;
    for (size_t i = 1; i < tokens.size(); ++i) {
        if (i > 1)
            message += " ";
        message += tokens[i];
    }
    LOG(Logger::LogLevel::DEBUG, "Server message: %s", message.c_str());
}