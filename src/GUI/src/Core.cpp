#include "../lib/Core.hpp"
#include <iostream>

bool Core::initialize()
{
    try {
        m_window = std::make_unique<sf::RenderWindow>(
            sf::VideoMode(1920, 1080), 
            "Zappy GUI",
            sf::Style::Titlebar | sf::Style::Close | sf::Style::Resize
        );
        
        m_window->setFramerateLimit(60);
        m_running = true;
        std::cout << "Core initialized successfully" << std::endl;
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
        std::cerr << "Core not initialized!" << std::endl;
        return;
    }
    while (m_window->isOpen() && m_running) {
        pollEvents();
        update();
        render();
    }
}

void Core::shutdown()
{
    if (m_window && m_window->isOpen()) {
        m_window->close();
    }
    m_running = false;
    std::cout << "Core shutdown complete" << std::endl;
}

void Core::update()
{
    // logic de jeu
}

void Core::render()
{
    m_window->clear(sf::Color::Black);
    m_window->display();
}

void Core::pollEvents()
{
    while (m_window->pollEvent(m_event)) {
        handleWindowEvents();
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
            }
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
