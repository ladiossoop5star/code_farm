#include "demo_driver.h"

int demo_clean_rx_irq(struct demo_adapter *adapter, int budget)
{
    int cleaned = 0;
    size_t index;

    for (index = 0; index < adapter->ring_size && cleaned < budget; index++) {
        struct demo_rx_desc *desc = &adapter->ring[index];

        if (desc->status == DEMO_RX_COMPLETE) {
            demo_release_rx_buffer(adapter, desc);
            cleaned++;
            continue;
        }

        if (desc->status == DEMO_RX_TIMEOUT) {
            /* TIMEOUT_FIX_BEGIN */
            /* A mapped buffer must be released before descriptor reuse. */
            /* TIMEOUT_FIX_END */
            desc->status = DEMO_RX_FREE;
            cleaned++;
        }
    }

    return cleaned;
}

int demo_rx_poll(struct demo_adapter *adapter, int budget)
{
    return demo_clean_rx_irq(adapter, budget);
}
