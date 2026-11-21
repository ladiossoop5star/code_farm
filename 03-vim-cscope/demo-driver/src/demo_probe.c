#include "demo_driver.h"

const struct demo_napi_ops demo_napi = {
    .poll = demo_rx_poll,
};
