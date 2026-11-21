s/\r$//
s/^DUT SELFTEST PASS: received KEY_POWER$/PASS/p
s/^DUT SELFTEST FAIL: gpio-keys input device missing$/NO_DEVICE/p
s/^DUT SELFTEST FAIL: KEY_POWER event missing$/NO_EVENT/p
/^DUT SELFTEST /s/.*/UNKNOWN/p
