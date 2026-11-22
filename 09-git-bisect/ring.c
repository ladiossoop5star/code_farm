#include <stdint.h>

enum { RING_SIZE = 8 };

unsigned ring_pending(uint8_t consumer, uint8_t producer)
{
    const unsigned counter_mask = 2u * RING_SIZE - 1u;

    return ((unsigned)producer - consumer) & counter_mask;
}
