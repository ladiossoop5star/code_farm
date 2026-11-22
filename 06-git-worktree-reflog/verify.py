"""Build and replay the Git worktree and reflog exercise in a temporary repo."""
import argparse
from hashlib import file_digest
import json
import os
from pathlib import Path
import shutil
import subprocess as sp
from tempfile import TemporaryDirectory


SOURCES = Path(__file__).resolve().parent
ENV = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', LC_ALL='C')
HOTFIX = 'hotfix/ready-timeout'
RESCUE = 'rescue/ready-timeout'


def command(root,*args,success=True):
    proc = sp.run(args,cwd=root,env=ENV,capture_output=True,text=True)
    if (proc.returncode==0)!=success:
        raise RuntimeError(f'{args}: {proc.returncode}\n{proc.stdout}\n{proc.stderr}')
    return proc.stdout.strip(),proc.stderr.strip()


def git(root,*args,success=True):
    return command(root,'git',*args,success=success)


def digest(file):
    with file.open('rb') as stream:
        return file_digest(stream,'sha256').hexdigest()


def prepare(parent):
    primary = parent/'firmware'
    primary.mkdir()
    for name in ('Makefile','wait.c'):
        shutil.copyfile(SOURCES/name,primary/name)
    (primary/'.gitignore').write_text('out/\n')
    git(primary,'init','-q','-b','main')
    for key,value in [('user.name','Presenter'),('user.email','presenter@example.invalid'),
                      ('core.logAllRefUpdates','true'),('commit.gpgSign','false'),
                      ('core.hooksPath',os.devnull)]:
        git(primary,'config',key,value)
    git(primary,'add','wait.c','Makefile','.gitignore')
    git(primary,'commit','-qm','Add firmware READY self-test')
    git(primary,'branch','release/1.x')
    git(primary,'switch','-q','-c','feature/probe-log')
    source=primary/'wait.c'
    original=source.read_text()
    feature=original.replace('    const int ready_after_poll[]','    puts("Starting probe diagnostics");\n    const int ready_after_poll[]',1)
    source.write_text(feature)
    git(primary,'add','wait.c')
    git(primary,'commit','-qm','Start probe diagnostics')
    debug=feature.replace('        if (samples[i])','        printf("probe[%d]=%d\\n", i, samples[i]);\n        if (samples[i])',1)
    source.write_text(debug)
    command(primary,'make','out/selftest')
    return primary


def verify(parent):
    primary=prepare(parent)
    fixes=parent/'firmware-hotfix'
    original_diff=git(primary,'diff','--','wait.c')[0]
    assert 'printf("probe[%d]=%d' in original_diff
    original_artifact=digest(primary/'out/selftest')
    release=git(primary,'rev-parse','release/1.x')[0]
    assert git(primary,'rev-parse','HEAD')[0]!=release

    git(primary,'worktree','add','-q','-b',HOTFIX,'../firmware-hotfix','release/1.x')
    assert git(fixes,'rev-parse','HEAD')[0]==release
    assert git(fixes,'status','--short')[0]==''
    assert git(primary,'branch','--show-current')[0]=='feature/probe-log'
    assert git(fixes,'branch','--show-current')[0]==HOTFIX
    assert HOTFIX in git(primary,'worktree','list')[0]
    assert (primary/git(primary,'rev-parse','--git-common-dir')[0]).resolve() == (
        fixes/git(fixes,'rev-parse','--git-common-dir')[0]).resolve()
    duplicate=git(primary,'worktree','add','../duplicate','feature/probe-log',success=False)[1]
    assert 'feature/probe-log' in duplicate and not (parent/'duplicate').exists()

    fail,_=command(fixes,'make','test',success=False)
    assert fail.endswith('FAIL: DUT stayed BUSY but wait_ready returned READY')
    source=fixes/'wait.c'
    old=source.read_text()
    fixed=old.replace('    return READY;\n}', '    return TIMEOUT;\n}',1)
    assert old!=fixed
    source.write_text(fixed)
    passed,_=command(fixes,'make','test')
    assert passed.endswith('PASS: READY after polling, TIMEOUT when BUSY')
    assert digest(primary/'out/selftest')==original_artifact
    assert digest(fixes/'out/selftest')!=original_artifact
    assert git(primary,'diff','--','wait.c')[0]==original_diff

    git(fixes,'add','wait.c')
    git(fixes,'commit','-qm','Return TIMEOUT when DUT stays BUSY')
    patch=git(fixes,'rev-parse','HEAD')[0]
    assert git(fixes,'for-each-ref','--contains',patch,'--format=%(refname)')[0]==f'refs/heads/{HOTFIX}'
    assert patch in git(fixes,'log','--all','--format=%H')[0].splitlines()
    git(fixes,'switch','--detach','release/1.x')
    git(fixes,'branch','-f',HOTFIX,'release/1.x')
    git(fixes,'switch',HOTFIX)
    assert git(fixes,'branch','--show-current')[0]==HOTFIX
    assert git(fixes,'log','-1','--format=%H')[0]==release
    for root in (primary,fixes):
        assert patch not in git(root,'log','--all','--format=%H')[0].splitlines()
    assert git(fixes,'for-each-ref','--contains',patch)[0]==''
    assert git(fixes,'reflog','show','-2','--format=%H',HOTFIX)[0].splitlines()==[release,patch]
    previous=f'{HOTFIX}@{{1}}'
    assert git(fixes,'rev-parse',previous)[0]==patch
    assert '+    return TIMEOUT;' in git(fixes,'show',previous,'--','wait.c')[0]
    git(fixes,'switch','-c',RESCUE,previous)
    assert git(fixes,'rev-parse',RESCUE)[0]==patch
    assert patch in git(fixes,'log','--all','--format=%H')[0].splitlines()
    assert '+    return TIMEOUT;' in git(fixes,'show',RESCUE,'--','wait.c')[0]
    rescued,_=command(fixes,'make','-B','test')
    assert rescued.endswith('PASS: READY after polling, TIMEOUT when BUSY')

    log=fixes/'run-note.txt'
    log.write_text('make test: PASS\n')
    assert '?? run-note.txt' in git(fixes,'status','--short')[0]
    git(primary,'worktree','remove','../firmware-hotfix',success=False)
    assert log.is_file() and (fixes/'out/selftest').is_file()
    git(primary,'worktree','remove','--force','../firmware-hotfix')
    assert not fixes.exists() and len(git(primary,'worktree','list')[0].splitlines())==1
    assert git(primary,'rev-parse',HOTFIX)[0]==release
    assert git(primary,'rev-parse',RESCUE)[0]==patch
    assert git(primary,'diff','--','wait.c')[0]==original_diff
    assert digest(primary/'out/selftest')==original_artifact
    return {'old_test':fail.splitlines()[-1],'new_test':passed.splitlines()[-1],
            'old_release_selected':True,'same_branch_guarded':True,'independent_output':True,
            'hotfix_switch_shows_old_release':True,'patch_missing_from_log_all':True,
            'patch_found_in_reflog':True,'rescued_test':rescued.splitlines()[-1],
            'dirty_worktree_guarded':True,
            'force_removed_worktree':True,'primary_wip_preserved':True}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',type=Path,metavar='DIRECTORY',help='create a new firmware demo in an existing directory')
    options=parser.parse_args()
    if options.prepare is not None:
        print(prepare(options.prepare.resolve()))
    else:
        with TemporaryDirectory(prefix='firmware-worktree-demo-') as scratch:
            print(json.dumps(verify(Path(scratch)),indent=2))
