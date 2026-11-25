#include "sensor-power.h"

#include <assert.h>
#include <errno.h>

int supply_enable(struct sensor *sensor)
{
    if (sensor->fault == SENSOR_SUPPLY_ERROR)
        return -EAGAIN;

    ++sensor->supply_refs;
    return 0;
}

void supply_disable(struct sensor *sensor)
{
    assert(sensor->supply_refs > sensor->clock_refs);
    --sensor->supply_refs;
}

int clock_enable(struct sensor *sensor)
{
    assert(sensor->supply_refs > sensor->clock_refs);
    if (sensor->fault == SENSOR_CLOCK_ERROR)
        return -EIO;

    ++sensor->clock_refs;
    return 0;
}

void clock_disable(struct sensor *sensor)
{
    assert(sensor->clock_refs > 0);
    --sensor->clock_refs;
    sensor->configured = false;
}

int restore_config(struct sensor *sensor)
{
    assert(sensor->clock_refs > 0);
    assert(sensor->supply_refs == sensor->clock_refs);
    if (sensor->fault == SENSOR_RESTORE_TIMEOUT)
        return -ETIMEDOUT;

    sensor->configured = true;
    return 0;
}
