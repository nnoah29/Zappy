#include "../lib/Threads.hpp"
#include <iostream>

Threads::Threads(Network& network):network_(network), message_(nullptr) {}

Threads::~Threads()
{
    stop();
}

void Threads::start()
{
    if (running_)
        return;
    
    running_ = true;
    thread_ = std::thread(&Threads::run, this);
}

void Threads::stop()
{
    if (running_) {
        running_ = false;
        if (thread_.joinable())
            thread_.join();
    }
}

void Threads::setMessage(Message handler)
{
    message_ = handler;
}

bool Threads::isRunning()
{
    return running_;
}

void Threads::run()
{
    while (running_) {
        try {
            std::string message = network_.receive();
            if (!message.empty()) {
                std::lock_guard<std::mutex> lock(Mutex_);
                Queue_.push(message);
            }
        } catch (const std::exception& e) {
            std::cerr << "Network error: " << e.what() << std::endl;
            running_ = false;
        }
    }
}

void Threads::processMessages()
{
    std::lock_guard<std::mutex> lock(Mutex_);
    while (!Queue_.empty()) {
        std::string message = Queue_.front();
        Queue_.pop();
        
        if (message_)
            message_(message);
    }
}