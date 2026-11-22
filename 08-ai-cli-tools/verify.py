"""Verify the CLI tools and the test-round example in a temporary directory."""
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import time

DEMO = Path(__file__).resolve().parent
BIN = DEMO / 'bin'


def run(command, cwd, expected=0):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=45)
    if result.returncode != expected:
        raise RuntimeError((command, result.returncode, result.stdout, result.stderr))
    return result


def replacement_demo(work):
    profile=work/'test profile.conf'
    profile.write_bytes(b'mode=loopback\r\ncapture_dir=./logs/staging\r\n')
    cli=[BIN/'replace-text',profile,'./logs/staging','./logs/run-01']
    result=run(cli,work)
    assert f'{profile}:2: capture_dir=./logs/run-01' in result.stdout
    expected=b'mode=loopback\r\ncapture_dir=./logs/run-01\r\n'
    assert profile.read_bytes()==expected
    again=run(cli,work)
    assert again.stdout=='0 changed line(s)\n' and profile.read_bytes()==expected
    smoke_profile=work/'smoke profile.conf'
    shutil.copyfile(DEMO/'sample/smoke-profile.conf',smoke_profile)
    smoke=run([BIN/'replace-text',smoke_profile,'./logs/smoke','./logs/run-02'],work)
    assert f'{smoke_profile}:2: capture_dir=./logs/run-02' in smoke.stdout
    assert smoke_profile.read_text()=='# Smoke test settings\ncapture_dir=./logs/run-02\nmode=loopback\n'
    assert profile.read_bytes()==expected
    capture_dir=next(line.split('=',1)[1] for line in profile.read_text().splitlines()
                     if line.startswith('capture_dir='))
    return (work/capture_dir).resolve()


def readiness_demo(work):
    tool = BIN / 'wait-ready'
    probe = DEMO / 'sample/query-ready'
    happy = run([tool, '--every', '1', '--timeout', '5', '--', probe, 'delayed', work / 'probe state'], work)
    assert happy.stdout.splitlines() == ['WAITING', 'WAITING', 'READY']
    timed = run([tool, '--timeout', '2', '--', probe, 'never'], work, 124)
    assert timed.stderr.splitlines()[-1] == 'TIMEOUT' and 'READY' not in timed.stdout
    broken = run([tool, '--timeout', '5', '--', probe, 'error'], work, 2)
    assert 'QUERY_ERROR (query exit=7)' in broken.stderr and not broken.stdout
    unusual = run([tool, '--timeout', '5', '--', 'bash', '-c', 'exit 124'], work, 2)
    assert 'QUERY_ERROR (query exit=124)' in unusual.stderr
    started = time.monotonic()
    hung = run([tool, '--timeout', '2', '--', probe, 'hanging'], work, 124)
    assert 'TIMEOUT' in hung.stderr and time.monotonic() - started < 8


def logs_demo(work):
    input_file = work / 'test bench.log'
    shutil.copyfile(DEMO / 'sample/session.log', input_file)
    command = [BIN / 'snap-log', '--out', work / 'local runs', input_file]
    captures = [Path(run(command, work).stdout.strip()) for _ in range(2)]
    assert captures[0] != captures[1]
    for capture in captures:
        assert (capture / 'raw.log').read_bytes() == input_file.read_bytes()
        assert (capture / 'failures.tsv').read_text() == (
            'line\tmessage\n2\tDUT SELFTEST FAIL: KEY_POWER event missing\n')


def rounds_demo(work,output):
    cases=[
        ('pass',0,'DUT SELFTEST PASS'),
        ('fail',1,'DUT SELFTEST FAIL'),
        ('timeout',124,'TEST SKIPPED: readiness exit=124'),
        ('query-error',2,'TEST SKIPPED: readiness exit=2'),
    ]
    reports=[]
    for name,status,marker in cases:
        result=run([DEMO/'sample/run-round',name,output],work,status)
        stored=Path(result.stdout.splitlines()[-1].removeprefix('Saved: '))
        reports.append(stored)
        assert marker in result.stdout and marker in (stored/'raw.log').read_text()
        if status in (124,2):
            assert 'DUT SELFTEST' not in result.stdout
        hits=(stored/'failures.tsv').read_text().splitlines()
        assert len(hits)==(2 if status==1 else 1)
    assert len(set(reports))==4


def dut_ip_demo(work):
    tool = BIN / 'dut-ip'
    mac = '02:00:00:00:08:42'
    before = DEMO / 'sample/arp-before.tsv'
    after = DEMO / 'sample/arp-after.tsv'
    assert run([tool, '--from', before, mac], work).stdout == '192.0.2.42\n'
    assert run([tool, '--from', after, mac], work).stdout == '192.0.2.57\n'

    variants = work / 'multiple replies.tsv'
    variants.write_text('192.0.2.60\t02:00:00:00:08:FA\n'
                        '192.0.2.59\t02:00:00:00:08:fa\n'
                        '192.0.2.60\t02:00:00:00:08:fa\n'
                        '192.0.2.61\t02:00:00:00:08:fb\n')
    assert run([tool, '--from', variants, '02:00:00:00:08:FA'], work).stdout == '192.0.2.59\n192.0.2.60\n'
    missing = run([tool, '--from', after, '02:00:00:00:08:99'], work, 1)
    assert not missing.stdout and 'no IPv4 reply' in missing.stderr
    unreadable = run([tool, '--from', work/'missing.tsv', mac], work, 2)
    assert not unreadable.stdout and 'missing.tsv' in unreadable.stderr
    invalid = run([tool, '--from', after, 'not-a-mac'], work, 2)
    assert not invalid.stdout and 'expected a MAC' in invalid.stderr


if __name__=='__main__':
    with TemporaryDirectory(prefix='cli-tools-demo-') as scratch:
        workspace = Path(scratch)
        dut_ip_demo(workspace)
        print('dut-ip: changed IPv4, exact case-insensitive MAC match and missing reply verified',flush=True)
        output = replacement_demo(workspace)
        print('replace-text: literal paths, line report and original CRLF verified',flush=True)
        readiness_demo(workspace)
        print('wait-ready: READY, TIMEOUT, QUERY_ERROR and hung query verified',flush=True)
        logs_demo(workspace)
        rounds_demo(workspace,output)
        print('snap-log and run-round: result statuses, skipped tests and per-round logs verified',flush=True)
