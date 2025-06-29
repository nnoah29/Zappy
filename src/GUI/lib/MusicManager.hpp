#pragma once
#include <SFML/Audio.hpp>
#include <memory>

class MusicManager {
public:
    MusicManager();
    ~MusicManager();
    bool playMusic(const std::string& path, float volume = 50.f);
    void stopMusic();
    float getVolume() const;
    sf::Music::Status getStatus() const;
    void setVolume(float volume);
private:
    std::unique_ptr<sf::Music> m_music;
};
