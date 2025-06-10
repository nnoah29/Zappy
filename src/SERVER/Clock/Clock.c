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


#include "Clock.h"

#include <stdlib.h>

Clock *initClock(int freq)
{
    Clock *clock = malloc(sizeof(Clock));
    clock_gettime(CLOCK_MONOTONIC, &clock->ts);
    clock->tick = 1.0 / freq;
    return clock;
}


double get_elapsed_seconds(Clock *clock) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    const double elapsed = (now.tv_sec - clock->ts.tv_sec) + (now.tv_nsec - clock->ts.tv_nsec) / 1e9;
    return elapsed;
}

long get_elapsed_ticks(Clock *clock)
{
    const double elapsed = get_elapsed_seconds(clock);

    return (long)(elapsed * clock->tick);
}

void get_current_time(struct timespec *ts)
{
    clock_gettime(CLOCK_MONOTONIC, ts);
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