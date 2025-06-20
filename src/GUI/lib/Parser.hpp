#ifndef PARSER_HPP
#define PARSER_HPP

#include <string>
#include <vector>
#include <sstream>

class Parser {
public:
    static std::vector<std::string> split(std::string& str, char delimiter = ' ');
};

#endif