#include "../lib/Core.hpp"
#include <SFML/Graphics.hpp>
#include <iostream>

Core::Core() 
    : m_window(nullptr)
    , m_videoMode()
    , m_title("Zappy GUI")
    , m_event()
    , m_deltaClock()
    , m_deltaTime(0.0f)
    , m_running(false)
    , m_windowWidth(1920)
    , m_windowHeight(1080)
    , m_framerateLimit(60)
    , m_verticalSyncEnabled(false)
{
}


Core::~Core() {
    shutdown();
}

bool Core::initialize() {
    try {
        initializeWindow();
        m_running = true;
        std::cout << "Core initialized successfully" << std::endl;
        std::cout << "Window: " << m_windowWidth << "x" << m_windowHeight << std::endl;
        std::cout << "Title: " << m_title << std::endl;
        return true;
    }
    catch (const std::exception &e) {
        std::cerr << "Failed to initialize Core: " << e.what() << std::endl;
        return false;
    }
}

void Core::run() {
    if (!m_running) {
        std::cerr << "Core not initialized!" << std::endl;
        return;
    }
    while (m_window->isOpen() && m_running) {
        updateDeltaTime();
        pollEvents();
        update();
        render();
    }
}

void Core::shutdown() {
    if (m_window && m_window->isOpen()) {
        m_window->close();
    }
    m_running = false;
    std::cout << "Core shutdown complete" << std::endl;
}

void Core::update() {
    // No logic yet, prevents unused function warning
}

void Core::render() {
    m_window->clear(sf::Color::Black);
    m_window->display();
}

void Core::pollEvents()
{
    while (m_window->pollEvent(m_event)) {
        handleWindowEvents();
    }
}

sf::RenderWindow &Core::getWindow() const
{
    return *m_window;
}

float Core::getDeltaTime() const {
    return m_deltaTime;
}

bool Core::isRunning() const {
    return m_running;
}

void Core::setFramerateLimit(unsigned int limit) {
    m_framerateLimit = limit;
    if (m_window) {
        m_window->setFramerateLimit(limit);
    }
}

void Core::setVerticalSync(bool enabled) {
    m_verticalSyncEnabled = enabled;
    if (m_window) {
        m_window->setVerticalSyncEnabled(enabled);
    }
}

void Core::setWindowTitle(const std::string &title) {
    m_title = title;
    if (m_window) {
        m_window->setTitle(title);
    }
}

void Core::initializeWindow() {
    m_videoMode = sf::VideoMode(m_windowWidth, m_windowHeight);
    if (!m_videoMode.isValid()) {
        std::cerr << "Video mode " << m_windowWidth << "x" << m_windowHeight << " not supported.\n";
        std::cerr << "Supported video modes on your system:\n";
        auto modes = sf::VideoMode::getFullscreenModes();
        for (const auto &mode : modes) {
            std::cerr << "  " << mode.width << "x" << mode.height << "\n";
        }
        if (!modes.empty()) {
    m_videoMode = modes[0];
            std::cerr << "Using fallback resolution: " << m_videoMode.width << "x" << m_videoMode.height << "\n";
        } else {
            throw std::runtime_error("No valid video mode available");
        }
    }
    m_window = std::make_unique<sf::RenderWindow>(
        m_videoMode, 
        m_title, 
        sf::Style::Titlebar | sf::Style::Close | sf::Style::Resize
    );
    
    m_window->setFramerateLimit(m_framerateLimit);
    m_window->setVerticalSyncEnabled(m_verticalSyncEnabled);
}

void Core::updateDeltaTime() {
    m_deltaTime = m_deltaClock.restart().asSeconds();
}

void Core::handleWindowEvents() {
    sf::FloatRect visibleArea;
    switch (m_event.type) {
        case sf::Event::Closed:
            m_running = false;
            break;
        case sf::Event::Resized:
            visibleArea = sf::FloatRect(0, 0, m_event.size.width, m_event.size.height);
            m_window->setView(sf::View(visibleArea));
            break;
        case sf::Event::KeyPressed:
            if (m_event.key.code == sf::Keyboard::Escape) {
                m_running = false;
            }
            break;
        default:
            break;
    }
}
