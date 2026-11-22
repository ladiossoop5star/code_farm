"""Build and verify the four-commit DMA history used by this episode."""
import argparse
import json
import os
from pathlib import Path
import subprocess as sp
from tempfile import TemporaryDirectory

ENV = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
ENV.update(LC_ALL='C', GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
BASE = """#include <stdint.h>
#include <stddef.h>

struct dma_caps { int split_at_4k; };
struct descriptor { uintptr_t addr; size_t len; };

static inline int crosses_4k(uintptr_t addr, size_t len)
{
    return len > 0x1000 - (addr & 0xfff);
}

/* Model accepts payloads up to 4 KiB and allocates two output slots. */
size_t dma_submit(const struct dma_caps *caps, uintptr_t addr, size_t len,
                  struct descriptor out[2])
{
    (void)caps;
    out[0] = (struct descriptor){addr, len};
    return 1;
}
"""
SPLIT = """    if (crosses_4k(addr, len)) {
        size_t first = 0x1000 - (addr & 0xfff);
        out[0] = (struct descriptor){addr, first};
        out[1] = (struct descriptor){addr + first, len - first};
        return 2;
    }
"""
CAPS = """/* Controller capabilities for this demo model. */
static const struct dma_caps rev_a = { .split_at_4k = 1 };
static const struct dma_caps rev_b = { .split_at_4k = 0 };
"""
SELFTEST_SUPPORT = """#include <assert.h>
#include <stdio.h>
#include "dma_submit.c"

static void check(const char *label, const struct dma_caps *caps, uintptr_t addr,
                  size_t len, size_t expected)
{
    struct descriptor out[2];
    size_t actual = dma_submit(caps, addr, len, out);
    assert(actual == expected);
    assert(out[0].addr == addr);
    if (actual == 2) {
        assert(out[0].len == 16 && out[1].len == 16);
        assert(out[1].addr == 0x2000);
        printf("PASS  %s  ->  16 + 16 bytes (2 descriptors)\\n", label);
    } else {
        assert(out[0].len == len);
        printf("PASS  %s  ->  %zu bytes (1 descriptor)\\n", label, len);
    }
}
"""
SELFTEST_CASES = """#include "selftest-support.h"
#include "dma_caps.c"

int main(void)
{
    check("Rev A | 0x1ff0 | 32 bytes", &rev_a, 0x1ff0, 32, 2);
    check("Rev B | 0x1ff0 | 32 bytes", &rev_b, 0x1ff0, 32, 1);
    check("Rev A | 0x1ff0 | 16 bytes", &rev_a, 0x1ff0, 16, 1);
    return 0;
}
"""
NEEDLE = 'crosses_4k(addr, len)'
SCOPE = ('-L','/if (crosses_4k(addr, len)/,+2','--','dma_submit.c')
G_PATTERN = r'crosses_4k\(addr, len\)'
SPLIT_MESSAGE = 'Split descriptors at 4 KiB DMA boundaries'
GATE_MESSAGE = 'Apply 4 KiB split only on Rev A'
STYLE_MESSAGE = 'Normalize indentation in DMA submit'


def prepare(repo):
    repo.mkdir()
    def run(*args):
        return sp.check_output(args,cwd=repo,env=ENV,text=True).strip()
    def git(*args):
        return run('git',*args)
    def write(name,value):
        (repo/name).write_text(value)
    def commit(title,body):
        git('add','.')
        git('commit','-q','-m',title,'-m',body)
        return git('rev-parse','HEAD')
    git('init','-q','-b','main')
    for key,value in (('user.name','Presenter'),('user.email','presenter@example.invalid'),
                      ('core.hooksPath',os.devnull),('commit.gpgSign','false'),('core.autocrlf','false')):
        git('config',key,value)
    write('.gitignore','/selftest\n/design-notes.md\n')
    write('dma_submit.c',BASE)
    write('selftest-support.h',SELFTEST_SUPPORT)
    commit('Submit DMA descriptors','Initial implementation uses one descriptor.')
    with_split=BASE.replace('    out[0]',SPLIT+'    out[0]',1)
    write('dma_submit.c',with_split)
    added=commit(SPLIT_MESSAGE,
                 'The Rev A model cannot consume a payload that crosses a 4 KiB DMA boundary.\nSplit crossing payloads conservatively while revision capabilities are unavailable.')
    with_gate=with_split.replace('    (void)caps;\n','').replace(
        f'    if ({NEEDLE})',f'      if ({NEEDLE} && caps->split_at_4k)')
    write('dma_submit.c',with_gate)
    write('dma_caps.c',CAPS)
    write('selftest.c',SELFTEST_CASES)
    write('Makefile','.PHONY: test\ntest: selftest\n\t./selftest\n\nselftest: selftest.c selftest-support.h dma_caps.c dma_submit.c\n\t$(CC) -Wall -Wextra -Werror -o $@ selftest.c\n')
    gate=commit(GATE_MESSAGE,'Use the controller revision capability. Rev B supports a crossing payload.\nKeep a boundary-edge case and test the same crossing input on both revisions.')
    write('dma_submit.c',with_gate.replace('      if (crosses_4k','    if (crosses_4k'))
    style=commit(STYLE_MESSAGE,'Whitespace-only indentation adjustment to the if line.')
    result={'split':git('rev-parse','--short',added),'gate':git('rev-parse','--short',gate),
            'style':git('rev-parse','--short',style)}
    for flags, expected in [((),style),(('-w',),gate)]:
        blame=git('blame',*flags,*SCOPE)
        assert expected.startswith(blame.split()[0]),(flags,blame,expected)
    assert git('log','--format=%H','-S'+NEEDLE,'--','dma_submit.c').splitlines()==[added]
    assert git('log','--format=%H','-G'+G_PATTERN,'--','dma_submit.c').splitlines()==[style,gate,added]
    patch=git('show',gate)
    assert all(file in patch for file in ('dma_caps.c','dma_submit.c','selftest.c'))
    output=run('make','test')
    assert 'Rev A | 0x1ff0 | 32 bytes  ->  16 + 16 bytes (2 descriptors)' in output
    assert 'Rev B | 0x1ff0 | 32 bytes  ->  32 bytes (1 descriptor)' in output
    assert 'Rev A | 0x1ff0 | 16 bytes  ->  16 bytes (1 descriptor)' in output
    (repo/'selftest').unlink()
    write('design-notes.md',f"""# DMA 4 KiB boundary split

Origin        {result['split']}  {SPLIT_MESSAGE}
                Rev A needs a split when the DMA address range crosses 4 KiB.

Revision gate {result['gate']}  {GATE_MESSAGE}
                Rev A: split_at_4k = 1
                Rev B: split_at_4k = 0

Reproduce      0x1ff0 / 32 bytes / Rev A  ->  two 16-byte descriptors
                0x1ff0 / 32 bytes / Rev B  ->  one 32-byte descriptor
                0x1ff0 / 16 bytes / Rev A  ->  one 16-byte descriptor

Verify on DUT  Supported revisions, probe result and reported capabilities
                Actual DMA address and length, plus submitted descriptors
""")
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('repository',nargs='?',type=Path)
    args=ap.parse_args()
    if args.repository:
        print(json.dumps(prepare(args.repository),indent=2))
    else:
        with TemporaryDirectory(prefix='dma-pickaxe-verify-') as temp:
            print(json.dumps(prepare(Path(temp)/'dma-demo'),indent=2))
