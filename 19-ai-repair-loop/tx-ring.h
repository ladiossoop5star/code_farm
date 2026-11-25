#ifndef TX_RING_H
#define TX_RING_H

#include <stddef.h>

enum { TX_RING_SIZE = 8 };

struct tx_ring {
    unsigned next_to_clean;
    unsigned pending;
    unsigned id[TX_RING_SIZE];
};

/* hw_head points just past the descriptors the device has completed. */
size_t tx_reclaim(struct tx_ring *ring, unsigned hw_head, unsigned completed[]);

#endif
