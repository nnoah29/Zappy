/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Clock.c
*/

#include "clock.h"

#include <stdlib.h>

my_clock_t *create_clock(int freq)
{
    my_clock_t *clock = malloc(sizeof(my_clock_t));

    clock_gettime(CLOCK_MONOTONIC, &clock->ts);
    clock->tick = 1.0 / freq;
    return clock;
}

double get_elapsed_seconds(my_clock_t *clock)
{
    struct timespec now;
    double elapsed = 0.0;

    clock_gettime(CLOCK_MONOTONIC, &now);
    elapsed = (now.tv_sec - clock->ts.tv_sec) +
        (now.tv_nsec - clock->ts.tv_nsec) / 1e9;
    return elapsed;
}

long get_elapsed_ticks(my_clock_t *clock)
{
    const double elapsed = get_elapsed_seconds(clock);

    return (long)(elapsed * clock->tick);
}

int has_elapsed(struct timespec *target, struct timespec *now)
{
    if (now->tv_sec > target->tv_sec)
        return 1;
    if (now->tv_sec == target->tv_sec && now->tv_nsec >= target->tv_nsec)
        return 1;
    return 0;
}

int timespec_cmp(struct timespec *a, struct timespec *b)
{
    if (a->tv_sec != b->tv_sec)
        return (a->tv_sec < b->tv_sec) ? -1 : 1;
    if (a->tv_nsec != b->tv_nsec)
        return (a->tv_nsec < b->tv_nsec) ? -1 : 1;
    return 0;
}

void add_seconds_to_timespec(struct timespec *ts, double seconds)
{
    const time_t sec = (time_t)seconds;
    const long nsec = (long)((seconds - (double)sec) * 1e9);

    ts->tv_sec += sec;
    ts->tv_nsec += nsec;
    if (ts->tv_nsec >= 1000000000L) {
        ts->tv_sec += 1;
        ts->tv_nsec -= 1000000000L;
    }
}
