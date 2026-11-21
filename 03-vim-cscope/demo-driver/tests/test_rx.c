#include "demo_driver.h"

#include <stdio.h>

static int expect_timeout_cleanup(void)
{
    int buffer_token = 7;
    struct demo_rx_desc ring[] = {
        {
            .status = DEMO_RX_TIMEOUT,
            .dma_mapped = 1,
            .buffer = &buffer_token,
        },
    };
    struct demo_adapter adapter = {
        .ring = ring,
        .ring_size = 1,
        .mapped_count = 1,
    };

    demo_napi.poll(&adapter, 8);

    if (adapter.mapped_count != 0 || ring[0].dma_mapped || ring[0].buffer) {
        fprintf(stderr,
                "FAIL timeout cleanup: mapped=%u buffer=%s status=%d\n",
                adapter.mapped_count,
                ring[0].buffer ? "owned" : "released",
                ring[0].status);
        return 1;
    }

    puts("PASS timeout cleanup released DMA buffer and descriptor");
    return 0;
}

int main(void)
{
    return expect_timeout_cleanup();
}
