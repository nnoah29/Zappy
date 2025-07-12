#pragma once
#include <SFML/Audio.hpp>
#include <string>

class MusicManager {
public:
    MusicManager();
    ~MusicManager();

    bool playMusic(const std::string& path, float volume = 50.f);
    void stopMusic();
    void setVolume(float volume);

    float getVolume() const;
    sf::Music::Status getStatus() const;

private:
    sf::Music m_music;
};