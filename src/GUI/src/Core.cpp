#include "../lib/Core.hpp"
#include "../lib/Game_world.hpp"
#include "../lib/RenderingEngine.hpp"
#include "../lib/Input_handler.hpp"
#include "../lib/AnimationSystem.hpp"
#include "../lib/Ressource_manager.hpp"
#include "../lib/PlayerInfoPanel.hpp"
#include "../lib/MusicManager.hpp"
#include <fstream>
#include <filesystem>
#include <iostream>
#include <random>

Core::Core() : m_running(false), m_gameWorld(nullptr), m_renderingEngine(nullptr), 
               m_inputHandler(nullptr), m_animationSystem(nullptr), m_musicManager(std::make_unique<MusicManager>()), 
               Disconnected(false)
{
}

Core::~Core() 
{ 
    shutdown(); 
}

void Core::setDisconnected()
{
    Disconnected = true;
    m_running = false;
}

bool Core::initialize(std::shared_ptr<GameWorld> gameWorld)
{
    if (!m_running || Disconnected)
        std::cerr << "Core not initialized or network disconnected!" << std::endl;
    try {
        m_window = std::make_unique<sf::RenderWindow>(
            sf::VideoMode(1920, 1080), 
            "Zappy GUI",
            sf::Style::Titlebar | sf::Style::Close | sf::Style::Resize
        );        
        m_window->setFramerateLimit(60);
        if (!ResourceManager::getInstance().initialize()) {
            std::cerr << "Failed to initialize ResourceManager" << std::endl;
            return false;
        }
        m_animationSystem = std::make_unique<AnimationSystem>();
        m_gameWorld = gameWorld;
        m_gameWorld->setAnimationSystem(m_animationSystem.get());
        m_renderingEngine = std::make_unique<RenderingEngine>(*m_window, *m_gameWorld);
        m_gameWorld->setRenderingEngine(m_renderingEngine.get());
        m_playerInfoPanel = std::make_unique<PlayerInfoPanel>(*m_window, *m_gameWorld);
        m_inputHandler = std::make_unique<InputHandler>(*m_window, *m_renderingEngine);
        m_clock.restart();        
        m_running = true;
        std::string musicPath = "src/GUI/assets/music/game_music.ogg";
        std::cout << "Tentative de chargement de la musique : " << musicPath << std::endl;
        std::ifstream file(musicPath);
        if (!file.good()) {
            std::cerr << "ERREUR: Fichier musical introuvable : " << musicPath << std::endl;
            std::cerr << "Répertoire de travail actuel : " << std::filesystem::current_path() << std::endl;
        } else {
            std::cout << "Fichier musical trouvé" << std::endl;
        }
        file.close();
        if (!m_musicManager->playMusic(musicPath, 50.f)) {
            std::cerr << "ERREUR: Impossible de jouer la musique : " << musicPath << std::endl;
        } else {
            std::cout << "Musique lancée avec succès" << std::endl;
        }
        return true;
    }
    catch (const std::exception &e) {
        std::cerr << "Failed to initialize Core: " << e.what() << std::endl;
        return false;
    }
}

void Core::run()
{
    if (!m_running) {
         std::cerr << "Core not initialized or network disconnected!" << std::endl;
        return;
    }
    
    std::cout << "Starting main game loop..." << std::endl;
    std::cout << "Controls:" << std::endl;
    std::cout << "- WASD or Arrow keys: Move camera" << std::endl;
    std::cout << "- Mouse wheel: Zoom in/out" << std::endl;
    std::cout << "- Right mouse button + drag: Pan camera" << std::endl;
    std::cout << "- Left mouse button: Select tile" << std::endl;
    std::cout << "- Escape: Exit" << std::endl;
    
    while (m_window->isOpen() && m_running) {
        float deltaTime = m_clock.restart().asSeconds();
        
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
    m_renderingEngine.reset();
    m_animationSystem.reset();
    m_gameWorld.reset();
    
    ResourceManager::destroy();
    
    if (m_window && m_window->isOpen()) {
        m_window->close();
    }
    m_running = false;
    std::cout << "Core shutdown complete" << std::endl;
}

void Core::update(float deltaTime)
{
    if (m_inputHandler) {
        m_inputHandler->update(deltaTime);
    }
    
    if (m_animationSystem) {
        m_animationSystem->update(deltaTime);
    }
    
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
                int randomPlayerIndex = rand() % players.size();
                const Player& randomPlayer = players[randomPlayerIndex];
                sf::Vector2f playerScreenPos = m_renderingEngine->tileToScreen(randomPlayer.x, randomPlayer.y);
                playerScreenPos.x += 32;
                playerScreenPos.y += 32;
                AnimationType types[] = {
                    AnimationType::INCANTATION,
                    AnimationType::RESOURCE_PICKUP,
                    AnimationType::EGG_HATCH,
                    AnimationType::PLAYER_EJECT
                };
                AnimationType randomType = types[rand() % 4];
                m_animationSystem->addEffect(randomType, playerScreenPos.x, playerScreenPos.y, 2.0f, sf::Color::Cyan);                
                std::cout << "Animation " << static_cast<int>(randomType) 
                          << " créée sur le joueur " << randomPlayer.id 
                          << " à la position (" << randomPlayer.x << ", " << randomPlayer.y << ")" << std::endl;
            }
        }
    }
}

void Core::render()
{
    m_window->clear(sf::Color(30, 30, 30));
    
    if (m_renderingEngine) {
        m_renderingEngine->render();
    }
    if (m_animationSystem) {
        m_animationSystem->render(*m_window);
    }
    renderUI();
    if (m_playerInfoPanel && m_playerInfoPanel->isVisible()) {
        m_playerInfoPanel->render();
    }
    m_window->display();
}

void Core::renderUI()
{
    m_window->setView(m_window->getDefaultView());    
    sf::Font font;
    sf::Text infoText;
    sf::RectangleShape uiBackground(sf::Vector2f(300, 150));
    uiBackground.setPosition(10, 10);
    uiBackground.setFillColor(sf::Color(0, 0, 0, 128));
    uiBackground.setOutlineThickness(2);
    uiBackground.setOutlineColor(sf::Color::White);
    m_window->draw(uiBackground);
}

void Core::pollEvents()
{
    while (m_window->pollEvent(m_event)) {
        std::cout << "[DEBUG][Core] pollEvents: event type=" << m_event.type << std::endl;
        handleWindowEvents();
        if (m_inputHandler) {
            m_inputHandler->handleEvent(m_event);
        }
        if (m_event.type == sf::Event::MouseButtonPressed && 
            m_event.mouseButton.button == sf::Mouse::Left) {
            
            sf::Vector2i mousePos = sf::Mouse::getPosition(*m_window);
            std::cout << "[DEBUG][Core] Mouse click at " << mousePos.x << "," << mousePos.y << std::endl;
            
            if (m_renderingEngine && m_playerInfoPanel) {
                int clickedPlayerId = m_renderingEngine->getPlayerIdAtScreenPosition(mousePos);
                std::cout << "[DEBUG][Core] getPlayerIdAtScreenPosition returned: " << clickedPlayerId << std::endl;
                
                if (clickedPlayerId != -1) {
                    std::cout << "[DEBUG][Core] Setting selected player to: " << clickedPlayerId << std::endl;
                    m_playerInfoPanel->setSelectedPlayer(clickedPlayerId);
                    m_gameWorld->initializePlayerInventory(clickedPlayerId);
                } else {
                    m_playerInfoPanel->setSelectedPlayer(-1);
                }
            }
        }
    }
}

void Core::handleWindowEvents()
{
    switch (m_event.type) {
        case sf::Event::Closed:
            m_running = false;
            break;
            
        case sf::Event::Resized:
            {
                sf::FloatRect visibleArea(0, 0, m_event.size.width, m_event.size.height);
                m_window->setView(sf::View(visibleArea));
                
                if (m_renderingEngine) {
                    m_renderingEngine->updateCamera();
                }
            }
            break;
        case sf::Event::KeyPressed:
            if (m_event.key.code == sf::Keyboard::Escape) {
                m_running = false;
            }
            else if (m_event.key.code == sf::Keyboard::Space) {
                if (m_animationSystem && m_gameWorld) {
                    sf::Vector2f center(m_gameWorld->getWidth() * 32.0f, m_gameWorld->getHeight() * 32.0f);
                    m_animationSystem->addEffect(AnimationType::INCANTATION, center.x, center.y, 3.0f, sf::Color::Magenta);
                }
            }
            break;

        default:
            break;
    }
}
