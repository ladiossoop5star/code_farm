# Small CLI tools for everyday tests

[繁體中文](README.md)

These four commands replace text, look up a DUT's IP address, wait for readiness, and save logs. Local scripts simulate device state and self-test outcomes. The IP examples use saved responses from an isolated network.

You need Linux, Bash, Python 3.9 or later, GNU coreutils, and awk. Run the verifier from this directory to check replacements, saved ARP results, readiness states, raw logs, and the failure summary in a temporary directory.

~~~sh
python3 verify.py
~~~

## Try a low-cost model first

Specify the inputs, expected outputs, and error cases. Try an inexpensive model using the same passing and failing inputs you plan to test afterward. The episode tried options in the GPT Terra, Claude Haiku, Gemini Flash, DeepSeek, and MiniMax families. OpenCode CLI gives you a way to work from the terminal. OpenCode Go was $10 per month at the time of recording, and allowances depend on the plan and model. [OpenCode CLI docs](https://opencode.ai/docs/) · [OpenCode Go details](https://opencode.ai/console/go)

Use an isolated working directory with sample inputs and expected results. Keep company source, real logs, and keys in their usual environment. [Copyable English prompts](prompts.en.md)

## Look up the DUT from recorded results

~~~bash
mac=02:00:00:00:08:42
bin/dut-ip --from sample/arp-before.tsv "$mac"
bin/dut-ip --from sample/arp-after.tsv "$mac"
~~~

Expect `192.0.2.42` and `192.0.2.57`. The tool matches the complete MAC case-insensitively and prints one IPv4 address per line. Exit status `0` means a match, `1` means no match, and `2` means a lookup or input error.

On your own lab network, use `bin/dut-ip --interface lab0 "$mac"` with the actual DUT MAC and the interface attached to the lab network. This mode uses `arp-scan`, which needs permission to send ARP packets. ARP is local to the Layer 2 network. Across a router, look from the DUT's network or check the DHCP server's lease. [arp-scan manual](https://github.com/royhills/arp-scan/blob/master/arp-scan.1.dist)

## Run the three test helpers

Make a temporary copy first. Run the rest of the exercise in the same Bash session.

~~~bash
work=$(mktemp -d)
cp -r bin sample "$work/"
cd "$work"
cp sample/test-profile.conf 'test profile.conf'
cp sample/smoke-profile.conf 'smoke profile.conf'

bin/replace-text 'test profile.conf' './logs/staging' './logs/run-01'
bin/replace-text 'smoke profile.conf' './logs/smoke' './logs/run-02'
~~~

Both commands print the updated line 2. Keep the quotes around a filename that contains spaces. The replacement is literal and preserves the file's line endings.

~~~bash
bin/wait-ready --every 1 --timeout 5 -- sample/query-ready delayed ready.state
bin/wait-ready --timeout 2 -- sample/query-ready never
echo "$?"
bin/wait-ready --timeout 5 -- sample/query-ready error
echo "$?"
bin/wait-ready --timeout 2 -- sample/query-ready hanging
echo "$?"
~~~

The first command prints two `WAITING` messages and then `READY`. The never-ready and hanging checks exit `124`. The failed query exits `2`. Use a new state filename if you rerun the delayed example. When you pass your own check after the double dash, have it exit `0` for ready, `1` to keep waiting, and another status for a query error.

~~~bash
first=$(bin/snap-log --out logs sample/session.log)
printf '%s\n' "$first"
cat "$first/failures.tsv"
sed -n '2p' "$first/raw.log"
bin/snap-log --out logs sample/session.log
cmp sample/session.log "$first/raw.log" && echo 'RAW MATCH'
~~~

The summary shows the failure on line 2 of the raw log, identified by the `DUT SELFTEST FAIL:` prefix. The two runs create separate directories. `RAW MATCH` confirms the saved log is byte-for-byte identical to its input.

## Run the whole test

~~~bash
out=$(sed -n 's/^capture_dir=//p' 'test profile.conf')
for scenario in pass fail timeout query-error; do
    sample/run-round "$scenario" "$out"
    printf 'exit=%s\n' "$?"
done
~~~

| Scenario | Exit | Raw log | Failure summary |
| --- | ---: | --- | --- |
| pass | 0 | READY, then self-test PASS | Header only |
| fail | 1 | READY, then self-test FAIL | One row for line 4 |
| timeout | 124 | TIMEOUT, then test skipped | Header only |
| query-error | 2 | QUERY_ERROR, then test skipped | Header only |

Each run prints a `Saved:` path containing `raw.log` and `failures.tsv`.

## Put the tools on your PATH

Check for existing commands with the same names before installing. `cp -i` prompts before overwriting an existing file.

~~~bash
mkdir -p "$HOME/.local/bin"
cp -i bin/replace-text bin/dut-ip bin/wait-ready bin/snap-log "$HOME/.local/bin/"
export PATH="$HOME/.local/bin:$PATH"
cd sample
command -v wait-ready
wait-ready --timeout 5 -- ./query-ready delayed ../installed-probe.state
~~~

The export applies to the current shell and its children. After testing it, add the setting to your shell startup file if you want it to persist. An alias works well for flags you use often. Keep commands that take arguments or serve other scripts as standalone tools with `--help`.
