"""Explicit, backup-safe import of existing Sage state. Never modifies the original.
Use before launching the new host, not while an existing destination host is running.
"""
from pathlib import Path
import sqlite3,shutil,uuid,os

def import_sage(source:Path,destination:Path):
    source=source.expanduser().resolve();destination=destination.expanduser().resolve()
    if not (source/'awake.sqlite3').is_file():raise ValueError('Source must be the existing Sage/data directory with awake.sqlite3')
    if source==destination or destination.is_relative_to(source):raise ValueError('Import destination must differ from the original')
    if destination.exists() and any(destination.iterdir()):raise ValueError('Destination already contains state. Import into a fresh data directory; never overwrite history')
    destination.parent.mkdir(parents=True,exist_ok=True)
    stage=destination.parent/('.sage-import-'+uuid.uuid4().hex);stage.mkdir(mode=0o700)
    try:
        original=sqlite3.connect((source/'awake.sqlite3').as_uri()+'?mode=ro',uri=True)
        copied=sqlite3.connect(stage/'awake.sqlite3')
        try:
            original.backup(copied)
            if copied.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Imported SQLite integrity check failed')
        finally:copied.close();original.close()
        for name in ['self.md','state.json']:
            if (source/name).is_file():shutil.copy2(source/name,stage/name)
        for name in ['self_history','letters']:
            if (source/name).is_dir():shutil.copytree(source/name,stage/name,symlinks=False)
        (stage/'.imported').write_text('Explicit Sage backup import. Originals unchanged.\n')
        if destination.exists():destination.rmdir()
        stage.rename(destination)
        print('Existing Sage state imported with SQLite backup API (including committed WAL data). Originals unchanged. No private text printed.')
    except Exception:
        shutil.rmtree(stage,ignore_errors=True);raise
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);args=p.parse_args();import_sage(args.source,args.destination)
