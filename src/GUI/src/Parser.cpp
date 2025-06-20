#include "../lib/Parser.hpp"

std::vector<std::string> Parser::split(std::string& str, char sep)
{
    std::vector<std::string> vec;
    std::string pht;
    std::stringstream stream(str);
    
    while (std::getline(stream, pht, sep)) {
        vec.push_back(pht);
    }
    return vec;
}
