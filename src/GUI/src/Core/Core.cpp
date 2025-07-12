#include "Core.hpp"
#include "../World/Game_world.hpp"
#include "../RenderEngine/RenderingEngine.hpp"
#include "../InputsHandlers/Input_handler.hpp"
#include "../Animations/AnimationSystem.hpp"
#include "../RessourcesManager/Ressource_manager.hpp"
#include "../Panel/PlayerInfoPanel.hpp"
#include "../Music/MusicManager.hpp"
#include "../GuiClient/Gui_client.hpp"
#include <fstream>
#include <filesystem>
#include <utility>

Core::Core() : m_rng(std::random_device{}())
{
    m_running =  false;
    m_gameWorld = nullptr;
    m_renderingEngine = nullptr;
    m_inputHandler = nullptr;
    m_animationSystem = nullptr;
    m_musicManager = std::make_unique<MusicManager>();
    m_isDisconnected = false;
    m_handlers = {
        {"msz", [&](const auto& tokens, Core&) { Msz(tokens, m_gameWorld); }},
        {"bct", [&](const auto& tokens, Core&) { Bct(tokens, m_gameWorld); }},
        {"tna", [&](const auto& tokens, Core&) { Tna(tokens, m_gameWorld); }},
        {"pnw", [&](const auto& tokens, Core&) { Pnw(tokens, m_gameWorld); }},
        {"ppo", [&](const auto& tokens, Core&) { Ppo(tokens, m_gameWorld); }},
        {"plv", [&](const auto& tokens, Core&) { Plv(tokens, m_gameWorld); }},
        {"pin", [&](const auto& tokens, Core&) { Pin(tokens, m_gameWorld); }},
        {"pex", [&](const auto& tokens, Core& core) { Pex(tokens, core); }},
        {"enw", [&](const auto& tokens, Core&) { Enw(tokens, m_gameWorld); }},
        {"ebo", [&](const auto& tokens, Core&) { Ebo(tokens, m_gameWorld); }},
        {"pdr", [&](const auto& tokens, Core&) { Pdr(tokens, m_gameWorld); }},
        {"pgt", [&](const auto& tokens, Core&) { Pgt(tokens, m_gameWorld); }},
        {"pic", [&](const auto& tokens, Core& core)     { Pic(tokens, core); }},
        {"pie", [&](const auto& tokens, Core& core)     { Pie(tokens, core); }},
        {"pfk", [&](const auto& tokens, Core&) { Pfk(tokens); }},
        {"pdi", [&](const auto& tokens, Core&) { Pdi(tokens, m_gameWorld); }},
        {"pbc", [&](const auto& tokens, Core&) { Pbc(tokens); }},
        {"edi", [&](const auto& tokens, Core&) { Edi(tokens, m_gameWorld); }},
        {"sgt", [&](const auto& tokens, Core&) { Sgt(tokens); }},
        {"sst", [&](const auto& tokens, Core&) { Sst(tokens); }},
        {"smg", [&](const auto& tokens, Core&) { Smg(tokens); }},
        {"seg", [&](const auto&, Core&) {
            LOG(Logger::LogLevel::INFO, "Game over received. Shutting down.");
            m_running = false; }
        }
    };
}

Core::~Core()
{
    shutdown();
}

void Core::setDisconnected()
{
    m_isDisconnected = true;
    m_running = false;
}

bool Core::initialize(std::shared_ptr<GameWorld> gameWorld, Gui_client& client)
{
    if (!m_running || m_isDisconnected) {
        LOG(Logger::LogLevel::ERROR, "Core not initialized or network disconnected!");
    }
    try {
        m_window = std::make_unique<sf::RenderWindow>(
            sf::VideoMode(1920, 1080),
            "Zappy GUI",
            sf::Style::Titlebar | sf::Style::Close | sf::Style::Resize
        );
        m_window->setFramerateLimit(60);
        if (!ResourceManager::getInstance().initialize()) {
            LOG(Logger::LogLevel::ERROR, "Failed to initialize ResourceManager");
            return false;
        }
        m_animationSystem = std::make_unique<AnimationSystem>();
        m_gameWorld = std::move(gameWorld);
        m_messageQueue = &client.getMessageQueue();
        m_gameWorld->setAnimationSystem(m_animationSystem.get());
        m_renderingEngine = std::make_unique<RenderingEngine>(*m_window, *m_gameWorld, *m_animationSystem);
        m_gameWorld->setRenderingEngine(m_renderingEngine.get());
        m_playerInfoPanel = std::make_unique<PlayerInfoPanel>(*m_window, *m_gameWorld);
        m_inputHandler = std::make_unique<InputHandler>(*m_window, *m_renderingEngine);
        initializeUI();
        m_clock.restart();
        m_running = true;

        const std::string musicPath = "src/GUI/assets/music/game_music.ogg";
        if (!m_musicManager->playMusic(musicPath, 25.f)) {
            LOG(Logger::LogLevel::ERROR, "Failed to play music: %s", musicPath.c_str());
        } else {
            LOG(Logger::LogLevel::INFO, "Music started successfully.");
        }
        return true;
    }
    catch (const std::exception &e) {
        LOG(Logger::LogLevel::ERROR, "Failed to initialize Core: %s", e.what());
        return false;
    }
}

void Core::run()
{
    if (!m_running) {
        LOG(Logger::LogLevel::ERROR, "Core not initialized or network disconnected!");
        return;
    }
    LOG(Logger::LogLevel::INFO, "Starting main game loop...");
    while (m_window->isOpen() && m_running) {
        const float deltaTime = m_clock.restart().asSeconds();

        pollEvents();
        update(deltaTime);
        render();
    }
    if (m_window->isOpen())
        m_window->close();
}

void Core::shutdown()
{
    if (m_musicManager) m_musicManager->stopMusic();
    m_inputHandler.reset();
    m_playerInfoPanel.reset();
    m_renderingEngine.reset();
    m_animationSystem.reset();
    m_gameWorld.reset();

    ResourceManager::destroy();

    if (m_window && m_window->isOpen()) {
        m_window->close();
    }
    m_running = false;
    LOG(Logger::LogLevel::INFO, "Core shutdown complete");
}

void Core::update(float deltaTime)
{
    if (m_inputHandler) m_inputHandler->update(deltaTime);
    if (m_animationSystem) m_animationSystem->update(deltaTime);

    processServerMessages();
    updateGameLogic(deltaTime);
}

void Core::updateGameLogic(float deltaTime)
{
    static float animationTimer = 0.0f;
    animationTimer += deltaTime;

    if (animationTimer > 3.0f) {
        animationTimer = 0.0f;

        if (m_animationSystem && m_gameWorld && m_renderingEngine) {
            const auto& players = m_gameWorld->getPlayers();

            if (!players.empty()) {
                std::uniform_int_distribution<size_t> player_dist(0, players.size() - 1);
                const Player& randomPlayer = players[player_dist(m_rng)];

                sf::Vector2f playerScreenPos = m_renderingEngine->tileToScreen(randomPlayer.x, randomPlayer.y);
                playerScreenPos += sf::Vector2f(32.f, 32.f);

                constexpr AnimationType types[] = {
                    AnimationType::INCANTATION, AnimationType::RESOURCE_PICKUP,
                    AnimationType::EGG_HATCH, AnimationType::PLAYER_EJECT
                };
                std::uniform_int_distribution<int> type_dist(0, 3);
                AnimationType randomType = types[type_dist(m_rng)];
                m_animationSystem->addEffect(randomType, playerScreenPos.x, playerScreenPos.y, 2.0f, sf::Color::Cyan);
                LOG(Logger::LogLevel::DEBUG, "Test animation %d created on player %d", static_cast<int>(randomType), randomPlayer.id);
            }
        }
    }
}

RenderingEngine* Core::getRenderingEngine() const { return m_renderingEngine.get(); }
AnimationSystem* Core::getAnimationSystem() const { return m_animationSystem.get(); }

void Core::render() const
{
    m_window->clear(sf::Color(30, 30, 30));

    if (m_renderingEngine) m_renderingEngine->render();
    renderUI();
    if (m_playerInfoPanel && m_playerInfoPanel->isVisible()) {
        m_playerInfoPanel->render();
    }
    m_window->display();
}

void Core::initializeUI()
{
    m_uiBackground.setSize(sf::Vector2f(300, 150));
    m_uiBackground.setPosition(10, 10);
    m_uiBackground.setFillColor(sf::Color(0, 0, 0, 128));
    m_uiBackground.setOutlineThickness(2);
    m_uiBackground.setOutlineColor(sf::Color::White);
}

void Core::renderUI() const
{
    m_window->setView(m_window->getDefaultView());
    m_window->draw(m_uiBackground);
}

void Core::pollEvents()
{
    while (m_window->pollEvent(m_event)) {
        if (m_inputHandler)
            m_inputHandler->handleEvent(m_event);
        handleWindowEvents();
    }
}

void Core::handleWindowEvents()
{
    if (m_event.type == sf::Event::Closed) {
        m_running = false;
    }
    if (m_event.type == sf::Event::Resized) {
        const sf::FloatRect visibleArea(0, 0, m_event.size.width, m_event.size.height);
        m_window->setView(sf::View(visibleArea));
        if (m_renderingEngine) m_renderingEngine->updateCamera();
    }

    if (m_event.type == sf::Event::KeyPressed) {
        if (m_event.key.code == sf::Keyboard::Escape) {
            m_running = false;
        }
    }
    if (m_event.type == sf::Event::MouseButtonPressed && m_event.mouseButton.button == sf::Mouse::Left) {
        const sf::Vector2i mousePos = sf::Mouse::getPosition(*m_window);
        if (m_renderingEngine && m_playerInfoPanel) {
            const int clickedPlayerId = m_renderingEngine->getPlayerIdAtScreenPosition(mousePos);
            m_playerInfoPanel->setSelectedPlayer(clickedPlayerId);
        }
    }
}

void Core::processServerMessages()
{
    while (auto msgOpt = m_messageQueue->try_pop()) {
        parseMessage(*msgOpt);
    }
}

void Core::parseMessage(const std::string& message)
{
    std::stringstream ss(message);
    std::string line;

    while (std::getline(ss, line)) {
        if (line.empty()) continue;
        LOG(Logger::LogLevel::DEBUG, "Parsing server line: '%s'", line.c_str());
        std::vector<std::string> tokens = Parser::split(line, ' ');
        if (tokens.empty()) continue;

        try {
            auto it = m_handlers.find(tokens[0]);
            if (it != m_handlers.end()) {
                it->second(tokens, *this);
            } else {
                LOG(Logger::LogLevel::WARN, "Unknown command received: %s", tokens[0].c_str());
            }
        } catch (const std::exception& e) {
            LOG(Logger::LogLevel::ERROR, "Failed to parse command %s: %s", tokens[0].c_str(), e.what());
        }
    }
}