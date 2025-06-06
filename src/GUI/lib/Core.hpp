#ifndef CORE_HPP
#define CORE_HPP

#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <SFML/System.hpp>
#include <memory>
#include <string>

class Core {
private:
    std::unique_ptr<sf::RenderWindow> m_window;
    sf::VideoMode m_videoMode;
    std::string m_title;
    sf::Event m_event;
    sf::Clock m_deltaClock;
    float m_deltaTime;
    bool m_running;
    
    int m_windowWidth;
    int m_windowHeight;
    int m_framerateLimit;
    bool m_verticalSyncEnabled;

public:
    Core();
    ~Core();

    bool initialize();
    void run();
    void shutdown();    
    void update();
    void render();
    void pollEvents();
    sf::RenderWindow& getWindow() const;
    float getDeltaTime() const;
    bool isRunning() const;
    void setFramerateLimit(unsigned int limit);
    void setVerticalSync(bool enabled);
    void setWindowTitle(const std::string& title);
    void handleWindowEvents();
    
private:
    void initializeWindow();
    void updateDeltaTime();
};

#endif