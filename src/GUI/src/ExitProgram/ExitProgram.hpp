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


#ifndef EXITPROGRAM_HPP
#define EXITPROGRAM_HPP
#include <exception>


// Définition de l’exception
class ExitProgram final : public std::exception {
public:
    const char* what() const noexcept override {
        return "Le GUI s'est arrêté proprement.";
    }
};




#endif //EXITPROGRAM_HPP
