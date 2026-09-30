"""Enter the allocated model cgroup before starting an allocating executable."""
import os
from pathlib import Path
import sys

from lab_run import guarded_root

root = guarded_root()
group = Path(sys.argv[1]).resolve(strict=True)
if group.parent != root or not group.name.startswith('agere-phase2-'):
    raise RuntimeError('Invalid model cgroup')
(group / 'cgroup.procs').write_text(str(os.getpid()))
os.execvpe(sys.argv[2], sys.argv[2:], os.environ)
