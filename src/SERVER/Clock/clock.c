/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Clock.c
*/

#include "clock.h"

#include <stdlib.h>

void get_current_time(struct timespec *ts)
{
    clock_gettime(CLOCK_MONOTONIC, ts);
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
