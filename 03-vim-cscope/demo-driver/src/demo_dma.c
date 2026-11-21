#include "demo_driver.h"

void demo_dma_map(struct demo_rx_desc *desc)
{
    desc->dma_mapped = 1;
}

void demo_dma_unmap(struct demo_adapter *adapter, struct demo_rx_desc *desc)
{
    if (!desc->dma_mapped)
        return;

    desc->dma_mapped = 0;
    adapter->mapped_count--;
}

void demo_release_rx_buffer(struct demo_adapter *adapter,
                            struct demo_rx_desc *desc)
{
    demo_dma_unmap(adapter, desc);
    desc->buffer = NULL;
    desc->status = DEMO_RX_FREE;
}

int demo_refill_rx_ring(struct demo_adapter *adapter, size_t count)
{
    size_t index;

    for (index = 0; index < count; index++) {
        struct demo_rx_desc *desc = &adapter->ring[index];

        if (desc->buffer == NULL)
            goto rollback;

        demo_dma_map(desc);
        adapter->mapped_count++;
        desc->status = DEMO_RX_READY;
    }
    return 0;

rollback:
    while (index > 0)
        demo_release_rx_buffer(adapter, &adapter->ring[--index]);
    return -1;
}
