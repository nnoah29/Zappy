/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 02/06/25.                                          
**         |___/ 
*/


#ifndef MY_H
#define MY_H
#include <unistd.h>
#include "Server/Server.h"

typedef void (*parser_func)(ConfigServer *conf, char **argv, int *i);
typedef struct {
    const char *key;
    parser_func func;
} OptionParser;

void exit_error(char *error, int degree);

void parse_port(ConfigServer *conf, char **argv, int *i);
void parse_width(ConfigServer *conf, char **argv, int *i);
void parse_height(ConfigServer *conf, char **argv, int *i);
void parse_clients(ConfigServer *conf, char **argv, int *i);
void parse_freq(ConfigServer *conf, char **argv, int *i);
void parse_names(ConfigServer *conf, char **argv, int *i);

#endif //MY_H
