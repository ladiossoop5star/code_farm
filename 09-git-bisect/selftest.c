#include <stdint.h>
#include <stdio.h>

unsigned ring_pending(uint8_t consumer, uint8_t producer);

int main(void)
{
    const struct {
        const char *name;
        uint8_t consumer;
        uint8_t producer;
        unsigned expected;
    } controls[] = {
        { "empty", 0, 0, 0 },
        { "partial", 3, 7, 4 },
        { "counter-wrap", 13, 2, 5 },
    };

    for (size_t i = 0; i < sizeof(controls) / sizeof(controls[0]); i++) {
        unsigned pending = ring_pending(controls[i].consumer, controls[i].producer);
        if (pending != controls[i].expected) {
            fprintf(stderr, "UNEXPECTED %s: wanted %u, got %u\n",
                    controls[i].name, controls[i].expected, pending);
            return 20;
        }
    }

    unsigned pending = ring_pending(0, 8);
    if (pending == 0) {
        puts("FAIL full ring: expected 8, got 0");
        return 10;
    }
    if (pending != 8) {
        fprintf(stderr, "UNEXPECTED full ring: wanted 8, got %u\n", pending);
        return 20;
    }
    puts("PASS full ring: expected 8, got 8");
    return 0;
}
