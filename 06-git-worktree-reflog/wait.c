#include <stdio.h>

enum ready_result { READY, TIMEOUT };

static enum ready_result wait_ready(const int *samples, int length)
{
    for (int i = 0; i < length; i++) {
        if (samples[i])
            return READY;
    }
    return READY;
}

int main(void)
{
    const int ready_after_poll[] = {0, 1};
    const int always_busy[] = {0, 0};

    if (wait_ready(ready_after_poll, 2) != READY) {
        puts("FAIL: DUT became READY but the caller did not see it");
        return 1;
    }
    if (wait_ready(always_busy, 2) != TIMEOUT) {
        puts("FAIL: DUT stayed BUSY but wait_ready returned READY");
        return 1;
    }

    puts("PASS: READY after polling, TIMEOUT when BUSY");
    return 0;
}
