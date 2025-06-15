#ifndef CORE_HPP
#define CORE_HPP

#include <SFML/Graphics.hpp>
#include <memory>

class Core {
private:
    std::unique_ptr<sf::RenderWindow> m_window;
    sf::Event m_event;
    bool m_running;

public:
    Core() : m_running(false) {}
    ~Core() { shutdown(); }

    bool initialize();
    void run();
    void shutdown();
    void update();
    void render();
    void pollEvents();

    sf::RenderWindow& getWindow() const { return *m_window; }
    bool isRunning() const { return m_running; }

private:
    void handleWindowEvents();
};

#endif
