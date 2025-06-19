#ifndef PARSER_HPP
#define PARSER_HPP

#include <string>
#include <vector>
#include <sstream>

struct Zappycmd {
        std::string cmd;
        std::vector<std::string> args;
    };

class Parser {
public:
    std::vector<std::string> split(std::string& str, char delimiter = ' ');
    static Zappycmd splitCommand(const std::string& input);
};

#endif