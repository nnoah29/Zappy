/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 07/07/25.                                          
**         |___/ 
*/


#ifndef MESSAGEQUEUE_HPP
#define MESSAGEQUEUE_HPP

#include <queue>
#include <string>
#include <mutex>
#include <optional>

class MessageQueue {
public:
    void push(const std::string& message) {
        std::lock_guard<std::mutex> lock(m_mutex);
        m_queue.push(message);
    }

    std::optional<std::string> try_pop() {
        std::lock_guard<std::mutex> lock(m_mutex);
        if (m_queue.empty()) {
            return std::nullopt;
        }
        std::string message = m_queue.front();
        m_queue.pop();
        return message;
    }

private:
    std::queue<std::string> m_queue;
    std::mutex m_mutex;
};

#endif // MESSAGEQUEUE_HPP