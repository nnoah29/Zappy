#include "MusicManager.hpp"
#include "../Logger/Logger.hpp"

MusicManager::MusicManager() {
   LOG(Logger::LogLevel::DEBUG, "MusicManager created.");
}

MusicManager::~MusicManager() {
    stopMusic();
    LOG(Logger::LogLevel::INFO, "MusicManager destroyed.");
}

bool MusicManager::playMusic(const std::string& path, float volume)
{
    LOG(Logger::LogLevel::DEBUG, "Attempting to open music file: %s", path.c_str());

    if (!m_music.openFromFile(path)) {
        LOG(Logger::LogLevel::ERROR, "Failed to open music file: %s", path.c_str());
        return false;
    }
    m_music.setLoop(true);
    m_music.setVolume(volume);
    LOG(Logger::LogLevel::INFO, "Playing music '%s' (Volume: %.1f, Loop: true)", path.c_str(), volume);
    m_music.play();
    if (m_music.getStatus() != sf::Music::Playing) {
        LOG(Logger::LogLevel::ERROR, "Music status is not 'Playing' after calling play().");
        return false;
    }
    return true;
}

void MusicManager::stopMusic()
{
    if (m_music.getStatus() == sf::Music::Playing) {
        LOG(Logger::LogLevel::INFO, "Stopping music.");
        m_music.stop();
    }
}

void MusicManager::setVolume(float volume)
{
    const float clampedVolume = std::max(0.f, std::min(100.f, volume));
    m_music.setVolume(clampedVolume);
    LOG(Logger::LogLevel::DEBUG, "Music volume set to: %.1f", clampedVolume);
}

float MusicManager::getVolume() const {
    return m_music.getVolume();
}

sf::Music::Status MusicManager::getStatus() const {
    return m_music.getStatus();
}