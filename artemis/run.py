#!/usr/bin/env python3
"""One launcher. No legacy application servers or arbitrary generated code are started."""
import argparse,os,sys,secrets
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description='ARTEMIS unified local workspace')
    p.add_argument('--host',default='127.0.0.1',help='Use 0.0.0.0 only for an authenticated remote/proxy setup')
    p.add_argument('--port',type=int,default=8000)
    p.add_argument('--data-dir',default=str(Path(__file__).parent/'.runtime'))
    p.add_argument('--import-sage',type=Path,help='Explicitly copy existing Sage/data before first launch; originals remain unchanged')
    args=p.parse_args();os.umask(0o077)
    data_root=Path(args.data_dir).resolve();data_root.mkdir(parents=True,exist_ok=True)
    # Linux/WSL launcher permits one owner for persistent state and file mutations.
    import fcntl
    ownership=(data_root/'host.lock').open('a+')
    try:fcntl.flock(ownership.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise SystemExit('This data directory is already owned by another ARTEMIS host.')
    ownership.seek(0);ownership.truncate();ownership.write(str(os.getpid()));ownership.flush()
    if args.import_sage:
        from scripts.import_sage import import_sage
        import_sage(args.import_sage,Path(args.data_dir)/'sage')
    os.environ['ARTEMIS_DATA_DIR']=args.data_dir
    from artemis_app.api import create_app
    import uvicorn
    app=create_app()
    print('\nARTEMIS · integration milestone 02',flush=True)
    print('One gateway · shared continuity, tools, files and approvals',flush=True)
    print('Operator key: '+app.state.operator_key,flush=True)
    print(f'Open http://localhost:{args.port} and use this key. It changes on restart unless ARTEMIS_OPERATOR_KEY is set.',flush=True)
    print('Originals preserved. Autonomy is opt-in; kernel isolation, speech, training and native World have explicit runtime/model requirements.\n',flush=True)
    uvicorn.run(app,host=args.host,port=args.port,log_level='info')
if __name__=='__main__':main()
