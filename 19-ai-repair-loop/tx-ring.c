#include "tx-ring.h"

size_t tx_reclaim(struct tx_ring *ring, unsigned hw_head, unsigned completed[])
{
    size_t count = 0;

    while (ring->pending && ring->next_to_clean < hw_head) {
        completed[count++] = ring->id[ring->next_to_clean];
        ring->next_to_clean = (ring->next_to_clean + 1) % TX_RING_SIZE;
        ring->pending--;
    }

    return count;
}
