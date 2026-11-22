// SPDX-License-Identifier: MIT
#include <stdint.h>

#ifndef BUILD_TAG
#define BUILD_TAG 13
#endif

typedef struct {
    uint32_t build_tag;
    uint32_t sampled_mv;
    uint32_t threshold_mv;
    uint32_t stage;
} controller_t;

volatile controller_t state;
extern volatile uint64_t crash_record[];

void save_report(const uint64_t *registers)
{
    volatile uint32_t *const uart = (uint32_t *)0x09000000;
    const char *message = "FWLAB READY\n";

    for (unsigned index = 0; index < 36; ++index)
        crash_record[index + 1] = registers[index];
    crash_record[0] = UINT64_C(0x00333142414c5746); /* FWLAB13 */
    __asm__ volatile("dsb sy" ::: "memory");
    for (; *message; ++message) {
        while (uart[6] & (1u << 5))
            ;
        uart[0] = (uint32_t)*message;
    }
}

static __attribute__((noinline)) void check_supply(void)
{
    if (state.sampled_mv < state.threshold_mv)
        __asm__ volatile("brk #0x42");
    state.stage = 4;
}

static __attribute__((noinline)) void controller_step(void)
{
    state.stage = 3;
    check_supply();
}

void main(void)
{
    state.build_tag = BUILD_TAG;
    state.sampled_mv = 2750;
    state.threshold_mv = 3000;
    controller_step();
}
