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


#include <stdio.h>
#include <stdlib.h>
#include "../my.h"

void exit_error(char *error, int degree)
{
    (void)degree;
    printf("[ERROR] : %s\n", error);
    exit(84);
}
