#include "../lib/Core.hpp"
#include "../lib/Game_world.hpp"
#include "../lib/RenderingEngine.hpp"
#include "../lib/Input_handler.hpp"
#include "../lib/AnimationSystem.hpp"
#include "../lib/Ressource_manager.hpp"
#include <iostream>
#include <random>

Core::Core() : m_running(false), m_gameWorld(nullptr), m_renderingEngine(nullptr), 
               m_inputHandler(nullptr), m_animationSystem(nullptr)
{
}

Core::~Core() 
{ 
    shutdown(); 
}

bool Core::initialize()
{
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
        m_gameWorld = std::make_unique<GameWorld>();
        if (!m_gameWorld->initialize(10, 10)) {
            std::cerr << "Failed to initialize GameWorld" << std::endl;
            return false;
        }
        initializeTestData();
        m_renderingEngine = std::make_unique<RenderingEngine>(*m_window, *m_gameWorld);
        m_inputHandler = std::make_unique<InputHandler>(*m_window, *m_renderingEngine);
        m_animationSystem = std::make_unique<AnimationSystem>();
        m_clock.restart();        
        m_running = true;
        std::cout << "Core initialized successfully" << std::endl;
        return true;
    }
    catch (const std::exception &e) {
        std::cerr << "Failed to initialize Core: " << e.what() << std::endl;
        return false;
    }
}

void Core::initializeTestData()
{
    int width = m_gameWorld->getWidth();
    int height = m_gameWorld->getHeight();
    int totalTiles = width * height;

    struct { float density; int Resource::*field; } densities[] = {
        {0.5f,  &Resource::food},
        {0.3f,  &Resource::linemate},
        {0.15f, &Resource::deraumere},
        {0.1f,  &Resource::sibur},
        {0.1f,  &Resource::mendiane},
        {0.08f, &Resource::phiras},
        {0.05f, &Resource::thystame}
    };

    int nbTypes = sizeof(densities) / sizeof(densities[0]);
    std::vector<int> totalPerType(nbTypes);
    for (int i = 0; i < nbTypes; ++i)
        totalPerType[i] = static_cast<int>(totalTiles * densities[i].density);

    std::vector<std::pair<int, int>> positions;
    for (int y = 0; y < height; ++y)
        for (int x = 0; x < width; ++x)
            positions.emplace_back(x, y);

    std::random_device rd;
    std::mt19937 g(rd());

    for (int t = 0; t < nbTypes; ++t) {
        std::shuffle(positions.begin(), positions.end(), g);
        for (int i = 0; i < totalPerType[t] && i < (int)positions.size(); ++i) {
            int x = positions[i].first;
            int y = positions[i].second;
            Resource res = m_gameWorld->getTile(x, y).resources;
            res.*(densities[t].field) += 1;
            m_gameWorld->updateTileResources(x, y, res);
        }
    }
    
    Player player1;
    player1.id = 1;
    player1.x = 5;
    player1.y = 5;
    player1.orientation = 1;
    player1.level = 1;
    player1.team = "team1";
    m_gameWorld->addPlayer(player1);
    
    Player player2;
    player2.id = 2;
    player2.x = 10;
    player2.y = 8;
    player2.orientation = 2;
    player2.level = 2;
    player2.team = "team2";
    m_gameWorld->addPlayer(player2);
    
    Player player3;
    player3.id = 3;
    player3.x = 15;
    player3.y = 12;
    player3.orientation = 3;
    player3.level = 1;
    player3.team = "team3";
    m_gameWorld->addPlayer(player3);
    
    Egg egg1;
    egg1.id = 1;
    egg1.x = 7;
    egg1.y = 3;
    egg1.team = "team1";
    m_gameWorld->addEgg(egg1);
    
    Egg egg2;
    egg2.id = 2;
    egg2.x = 12;
    egg2.y = 15;
    egg2.team = "team2";
    m_gameWorld->addEgg(egg2);
    
    std::cout << "Test data initialized" << std::endl;
}

void Core::run()
{
    if (!m_running) {
        std::cerr << "Core not initialized!" << std::endl;
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
}

void Core::shutdown()
{
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
        
        if (m_animationSystem && m_gameWorld) {
            int randX = rand() % m_gameWorld->getWidth();
            int randY = rand() % m_gameWorld->getHeight();
            
            sf::Vector2f worldPos = m_renderingEngine->tileToScreen(randX, randY);
            worldPos.x += 32;
            worldPos.y += 32;
            
            AnimationType types[] = {
                AnimationType::INCANTATION,
                AnimationType::RESOURCE_PICKUP,
                AnimationType::EGG_HATCH,
                AnimationType::PLAYER_EJECT
            };
            
            AnimationType randomType = types[rand() % 4];
            m_animationSystem->addEffect(randomType, worldPos.x, worldPos.y, 2.0f, sf::Color::Cyan);
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
    
    if (m_inputHandler && m_inputHandler->hasTileSelected()) {
        sf::Vector2i selectedTile = m_inputHandler->getSelectedTile();
        
        sf::RectangleShape selectionInfo(sf::Vector2f(250, 60));
        selectionInfo.setPosition(10, 170);
        selectionInfo.setFillColor(sf::Color(0, 0, 100, 128));
        selectionInfo.setOutlineThickness(1);
        selectionInfo.setOutlineColor(sf::Color::Cyan);
        m_window->draw(selectionInfo);
    }
}

void Core::pollEvents()
{
    while (m_window->pollEvent(m_event)) {
        handleWindowEvents();
        
        if (m_inputHandler) {
            m_inputHandler->handleEvent(m_event);
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