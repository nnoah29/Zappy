#include "../lib/MusicManager.hpp"
#include <iostream>

MusicManager::MusicManager() : m_music(std::make_unique<sf::Music>()) {
    std::cout << "MusicManager créé" << std::endl;
}

MusicManager::~MusicManager() {
    stopMusic();
    std::cout << "MusicManager détruit" << std::endl;
}

bool MusicManager::playMusic(const std::string& path, float volume) {
    std::cout << "Tentative d'ouverture du fichier musical : " << path << std::endl;
    
    if (!m_music->openFromFile(path)) {
        std::cerr << "ERREUR: Impossible d'ouvrir le fichier musical : " << path << std::endl;
        return false;
    }
    
    std::cout << "Fichier musical ouvert avec succès" << std::endl;
    std::cout << "Durée de la musique : " << m_music->getDuration().asSeconds() << "s" << std::endl;
    
    m_music->setLoop(true);
    m_music->setVolume(volume);
    
    std::cout << "Configuration : Volume=" << volume << "%, Loop=true" << std::endl;
    
    m_music->play();
    sf::Music::Status status = m_music->getStatus();
    std::cout << "Statut de la musique après play() : ";
    switch(status) {
        case sf::Music::Stopped:
            std::cout << "Stopped" << std::endl;
            return false;
        case sf::Music::Paused:
            std::cout << "Paused" << std::endl;
            break;
        case sf::Music::Playing:
            std::cout << "Playing" << std::endl;
            break;
    }
    
    return true;
}

void MusicManager::stopMusic() {
    if (m_music && m_music->getStatus() == sf::Music::Playing) {
        std::cout << "Arrêt de la musique" << std::endl;
        m_music->stop();
    }
}

float MusicManager::getVolume() const {
    return m_music ? m_music->getVolume() : 0.0f;
}

sf::Music::Status MusicManager::getStatus() const {
    return m_music ? m_music->getStatus() : sf::Music::Stopped;
}

void MusicManager::setVolume(float volume) {
    if (m_music) {
        m_music->setVolume(volume);
        std::cout << "Volume changé à : " << volume << "%" << std::endl;
    }
}