# Sensor power-on contract

The caller starts with the sensor inactive and no supply or clock references owned by the driver. Calls are serialized. The caller invokes `sensor_power_off()` only after a successful `sensor_power_on()`, and may retry after a failed power-on.

- Power-on enables the supply, enables the input clock, then restores sensor configuration. On success it leaves one reference to each resource and an active configuration.
- Any of the three operations can fail. Power-on returns the original error and releases the resources acquired by that attempt in reverse order. On return from a failure, the driver owns neither reference.
- Power-off releases the clock before the supply and clears the configuration. The modeled release operations always succeed.
