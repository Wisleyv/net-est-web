import psutil
import sys
PIDS = [11580, 22860, 28368, 30292]

for pid in PIDS:
    print('\n--- PID', pid, '---')
    try:
        p = psutil.Process(pid)
        print('name:', p.name())
        print('exe:', p.exe())
        print('cmdline:', ' '.join(p.cmdline()))
        print('status:', p.status())
        print('create_time:', p.create_time())
        print('cwd:', p.cwd())
        try:
            print('username:', p.username())
        except Exception:
            pass
        try:
            print('ppid:', p.ppid())
            parent = p.parent()
            if parent:
                print('parent_cmdline:', ' '.join(parent.cmdline()))
        except Exception:
            pass
        try:
            conns = p.connections()
            print('connections count:', len(conns))
            for c in conns:
                laddr = getattr(c, 'laddr', None)
                raddr = getattr(c, 'raddr', None)
                print('  ', c.status, laddr, '->', raddr)
        except Exception as e:
            print('  could not get connections:', e)
        try:
            files = p.open_files()
            print('open_files:', [f.path for f in files])
        except Exception as e:
            print('  could not get open_files:', e)
        try:
            print('num_threads:', p.num_threads())
        except Exception:
            pass
        try:
            mem = p.memory_info()
            print('memory:', mem)
        except Exception:
            pass
    except psutil.NoSuchProcess:
        print('No such process')
    except Exception as e:
        print('Error inspecting pid', pid, ':', e)

print('\nDone')
