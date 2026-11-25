#include "sensor-power.h"

int sensor_power_on(struct sensor *sensor)
{
    int ret = supply_enable(sensor);
    if (ret)
        return ret;

    ret = clock_enable(sensor);
    if (ret)
        goto disable_supply;

    return restore_config(sensor);

disable_supply:
    supply_disable(sensor);
    return ret;
}

void sensor_power_off(struct sensor *sensor)
{
    clock_disable(sensor);
    supply_disable(sensor);
}
