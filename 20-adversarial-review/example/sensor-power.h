#ifndef SENSOR_POWER_H
#define SENSOR_POWER_H

#include <stdbool.h>

enum sensor_fault {
    SENSOR_NO_FAULT,
    SENSOR_SUPPLY_ERROR,
    SENSOR_CLOCK_ERROR,
    SENSOR_RESTORE_TIMEOUT,
};

struct sensor {
    enum sensor_fault fault;
    unsigned supply_refs;
    unsigned clock_refs;
    bool configured;
};

int sensor_power_on(struct sensor *sensor);
void sensor_power_off(struct sensor *sensor);

int supply_enable(struct sensor *sensor);
void supply_disable(struct sensor *sensor);
int clock_enable(struct sensor *sensor);
void clock_disable(struct sensor *sensor);
int restore_config(struct sensor *sensor);

#endif
