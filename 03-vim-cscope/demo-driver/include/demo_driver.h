#ifndef DEMO_DRIVER_H
#define DEMO_DRIVER_H

#include <stddef.h>

enum demo_rx_status {
    DEMO_RX_FREE,
    DEMO_RX_READY,
    DEMO_RX_COMPLETE,
    DEMO_RX_TIMEOUT,
};

struct demo_rx_desc {
    enum demo_rx_status status;
    int dma_mapped;
    void *buffer;
};

struct demo_adapter {
    struct demo_rx_desc *ring;
    size_t ring_size;
    unsigned int mapped_count;
};

struct demo_napi_ops {
    int (*poll)(struct demo_adapter *adapter, int budget);
};

extern const struct demo_napi_ops demo_napi;

int demo_rx_poll(struct demo_adapter *adapter, int budget);
int demo_clean_rx_irq(struct demo_adapter *adapter, int budget);
int demo_refill_rx_ring(struct demo_adapter *adapter, size_t count);
void demo_release_rx_buffer(struct demo_adapter *adapter,
                            struct demo_rx_desc *desc);
void demo_dma_map(struct demo_rx_desc *desc);
void demo_dma_unmap(struct demo_adapter *adapter,
                    struct demo_rx_desc *desc);

#endif
