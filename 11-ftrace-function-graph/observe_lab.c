// SPDX-License-Identifier: GPL-2.0
#include <linux/delay.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/platform_device.h>

static DEFINE_MUTEX(run_lock);
static bool simulate_timeout;
static volatile unsigned int last_phase;

static noinline int observe_wait_ready(struct device *device)
{
	dev_dbg(device, "OBS status READY=%d\n", !simulate_timeout);
	if (simulate_timeout) {
		usleep_range(5000, 6000);
		return -ETIMEDOUT;
	}
	return 0;
}

static noinline void observe_enable_queue(struct device *device)
{
	dev_dbg(device, "OBS queue armed\n");
}

static noinline void observe_cleanup(struct device *device)
{
	dev_dbg(device, "OBS cleanup failed probe\n");
}

static noinline int observe_probe(struct platform_device *device)
{
	int result;

	dev_dbg(&device->dev, "OBS probe begin\n");
	result = observe_wait_ready(&device->dev);
	if (result) {
		observe_cleanup(&device->dev);
		dev_info(&device->dev, "OBS probe ret=%d\n", result);
		return result;
	}
	observe_enable_queue(&device->dev);
	dev_info(&device->dev, "OBS probe ret=0\n");
	return 0;
}

static struct platform_driver observe_driver = {
	.probe = observe_probe,
	.driver = { .name = "observe-lab" },
};

noinline void observe_measure(unsigned int phase, unsigned int delay_us);

noinline void observe_measure(unsigned int phase, unsigned int delay_us)
{
	last_phase = phase;
	usleep_range(delay_us, delay_us + 150);
}

static void measure_phase(unsigned int phase)
{
	unsigned int index;

	for (index = 0; index < 12; index++) {
		unsigned int delay_us = 1000;

		if (phase == 1 && index == 11)
			delay_us = 24000;
		if (phase == 2)
			delay_us = 6000;
		observe_measure(phase, delay_us);
	}
	pr_info("OBS measurement phase=%u samples=12\n", phase);
}

static int set_run(const char *value, const struct kernel_param *param)
{
	struct platform_device *device;
	int result = 0;

	if (!mutex_trylock(&run_lock))
		return -EBUSY;
	if (sysfs_streq(value, "ready") || sysfs_streq(value, "timeout")) {
		simulate_timeout = sysfs_streq(value, "timeout");
		pr_debug("OBS trigger timeout=%d\n", simulate_timeout);
		device = platform_device_register_simple("observe-lab", -1, NULL, 0);
		if (IS_ERR(device))
			result = PTR_ERR(device);
		else
			platform_device_unregister(device);
	} else if (sysfs_streq(value, "baseline")) {
		measure_phase(0);
	} else if (sysfs_streq(value, "outlier")) {
		measure_phase(1);
	} else if (sysfs_streq(value, "pressure")) {
		measure_phase(2);
	} else {
		result = -EINVAL;
	}
	mutex_unlock(&run_lock);
	return result;
}

static const struct kernel_param_ops run_ops = { .set = set_run };
module_param_cb(run, &run_ops, NULL, 0200);

static int __init observe_init(void)
{
	return platform_driver_register(&observe_driver);
}

static void __exit observe_exit(void)
{
	platform_driver_unregister(&observe_driver);
}

module_init(observe_init);
module_exit(observe_exit);
MODULE_DESCRIPTION("Isolated kernel observability teaching fixture");
MODULE_LICENSE("GPL");
