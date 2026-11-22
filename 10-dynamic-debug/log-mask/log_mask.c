#include <linux/atomic.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>

enum log_group {
	MASK_PCIE = BIT(0),
	MASK_DMA = BIT(1),
	MASK_RESET = BIT(2),
	MASK_SUPPORTED = MASK_PCIE | MASK_DMA | MASK_RESET,
};

static unsigned int debug_mask;
static atomic_t run_id = ATOMIC_INIT(0);
static struct proc_dir_entry *directory;

static ssize_t read_mask(struct file *file, char __user *buffer, size_t count,
			 loff_t *offset)
{
	char text[16];
	int length = scnprintf(text, sizeof(text), "0x%02x\n",
			       READ_ONCE(debug_mask));

	return simple_read_from_buffer(buffer, count, offset, text, length);
}

static ssize_t write_mask(struct file *file, const char __user *buffer,
			  size_t count, loff_t *offset)
{
	unsigned int mask;
	int ret;

	ret = kstrtouint_from_user(buffer, count, 0, &mask);
	if (ret)
		return ret;
	if (mask & ~MASK_SUPPORTED)
		return -EINVAL;

	WRITE_ONCE(debug_mask, mask);
	return count;
}

static ssize_t run_test(struct file *file, const char __user *buffer,
			size_t count, loff_t *offset)
{
	unsigned int start;
	unsigned int mask;
	int run;
	int ret;

	ret = kstrtouint_from_user(buffer, count, 0, &start);
	if (ret)
		return ret;
	if (start != 1)
		return -EINVAL;

	/* Use fixed sample events to show what each bit selects. */
	mask = READ_ONCE(debug_mask);
	run = atomic_inc_return(&run_id);
	if (mask & MASK_RESET)
		pr_info("DLOG RESET start\n");
	if (mask & MASK_PCIE)
		pr_info("DLOG PCIe read offset=0x10 value=0x01\n");
	if (mask & MASK_DMA)
		pr_info("DLOG DMA completion slot=3\n");
	pr_info("DLOG run=%d complete\n", run);
	return count;
}

static const struct proc_ops mask_ops = {
	.proc_read = read_mask,
	.proc_write = write_mask,
};

static const struct proc_ops run_ops = {
	.proc_write = run_test,
};

static int __init log_mask_init(void)
{
	directory = proc_mkdir("demo_drv", NULL);
	if (!directory)
		return -ENOMEM;
	if (!proc_create("debug_mask", 0600, directory, &mask_ops) ||
	    !proc_create("trigger", 0200, directory, &run_ops)) {
		proc_remove(directory);
		return -ENOMEM;
	}
	return 0;
}

static void __exit log_mask_exit(void)
{
	proc_remove(directory);
}

module_init(log_mask_init);
module_exit(log_mask_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Synthetic driver events for a debug mask lesson");
