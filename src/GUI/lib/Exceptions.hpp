#ifndef ERROR_HPP
#define ERROR_HPP
#include <exception>
#include <iostream>
#include <string>

class Error: public std::exception {
    private:
        std::string message;
    public:
        explicit Error(const std::string& msg) : message(msg) {}
        const char* what() const noexcept override {
            return message.c_str();
        }
};

#endif //ERROR_HPP