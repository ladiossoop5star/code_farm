# Ask AI to automate a repeated task

[繁體中文](prompts.md)

Use a separate test directory with disposable copies of sample data. Specify the input, expected output, and failure cases. Try the task on an inexpensive model first. You can start any of the prompts below with this instruction:

> Work inside this test directory using these fixtures and requirements. After implementing the tool, run one passing and one failing case. Report what it printed, its exit status, and the files it created or changed.

## replace-text

> I keep replacing log paths in a configuration file. Create a command named replace-text that takes a filename, the old text, and the new text, in that order. Filenames can contain spaces and the replacement values can contain slashes. Match the text literally, preserve line endings, and print the numbers and contents of changed lines. Verify it using ./logs/staging to ./logs/run-01 in test profile.conf and ./logs/smoke to ./logs/run-02 in smoke profile.conf.

## dut-ip

> My headless DUT occasionally gets a new IP address. Create a dut-ip command that takes the MAC address I've recorded and a lab network interface. Use arp-scan on that interface and print each IPv4 address whose full MAC matches. Support --from to read saved scan output. Use the supplied before and after fixtures, and include a no-match case and a failed-query case.

## wait-ready

> Create wait-ready to repeat an existing readiness check before a test. The polling interval and timeout come before the double dash. The check command and its arguments come after it. Check exit code 0 means ready, 1 means keep waiting, and other values mean the check failed. Apply the same deadline if the check hangs. Print READY, TIMEOUT, or QUERY_ERROR and exit 0, 124, or 2, respectively. Verify delayed readiness, no readiness, a failed check, and a hanging check.

## snap-log

> Create snap-log to take my raw log and an output directory. Make a fresh subdirectory for each run, leave the raw bytes intact, and write a failure summary with original line numbers. In the fixture, a failure line starts with DUT SELFTEST FAIL:. Run twice on the same input and check that the directories differ and that cmp confirms each saved raw log matches the input.

## Connect the tools into one run

> Read the output path from the test configuration. Use wait-ready before the self-test. Save both outputs to the same log and archive it with snap-log. Check successful tests, failed tests, and readiness timeouts. Skip the self-test on timeout and retain the log and the appropriate exit code in every scenario. Also verify a query error.
