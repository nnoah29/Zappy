/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Clock.h
*/

#ifndef CLOCK_H
    #define CLOCK_H
    #include <time.h>

typedef struct {
    struct timespec ts;
    double tick;
} my_clock_t;

my_clock_t *create_clock(int freq);
void get_current_time(struct timespec *ts);
long get_elapsed_ticks(my_clock_t *clock);
int timespec_cmp(struct timespec *a, struct timespec *b);
#endif //CLOCK_H
