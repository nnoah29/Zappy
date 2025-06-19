/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Clock.h
*/

#ifndef CLOCK_H
    #define CLOCK_H
    #include <time.h>

int timespec_cmp(struct timespec *a, struct timespec *b);
void add_seconds_to_timespec(struct timespec *ts, double seconds);
void get_current_time(struct timespec *ts);
#endif //CLOCK_H
