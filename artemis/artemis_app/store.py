"""Durable unified state, extending Sage's actual SQLite Memory implementation.
Original Sage tables remain intact. New integration tables live in the same database.
"""
from __future__ import annotations
import json,time,uuid
from pathlib import Path
from contextlib import contextmanager
from vendor_sources.sage.awake.memory import Memory

ACTIVE=('queued','running','awaiting_approval','cancelling')
def uid():return uuid.uuid4().hex
def dump(x):return json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':'))
class Store(Memory):
    def __init__(self,path:Path):
        path.parent.mkdir(parents=True,exist_ok=True)
        super().__init__(path)
        with self._lock:
            self._db.executescript('''
CREATE TABLE IF NOT EXISTS threads(id TEXT PRIMARY KEY,title TEXT NOT NULL,created REAL NOT NULL,context TEXT NOT NULL DEFAULT '[]');
CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,thread_id TEXT NOT NULL,role TEXT NOT NULL,content TEXT NOT NULL,meta TEXT NOT NULL DEFAULT '{}',ts REAL NOT NULL);
CREATE INDEX IF NOT EXISTS messages_thread ON messages(thread_id,ts);
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY,thread_id TEXT,kind TEXT NOT NULL,status TEXT NOT NULL,input TEXT NOT NULL DEFAULT '',state TEXT NOT NULL DEFAULT '{}',result TEXT,error TEXT,steps INTEGER NOT NULL DEFAULT 0,created REAL NOT NULL,updated REAL NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_chat ON runs(thread_id) WHERE kind='chat' AND status IN ('queued','running','awaiting_approval','cancelling');
CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY,run_id TEXT NOT NULL,call_id TEXT NOT NULL,tool TEXT NOT NULL,args TEXT NOT NULL,digest TEXT NOT NULL,precondition TEXT NOT NULL DEFAULT '{}',status TEXT NOT NULL,created REAL NOT NULL,output TEXT);
CREATE INDEX IF NOT EXISTS approvals_run ON approvals(run_id);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,path TEXT NOT NULL UNIQUE,sha256 TEXT NOT NULL,size INTEGER NOT NULL,mime TEXT NOT NULL,producer TEXT,updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS revisions(id TEXT PRIMARY KEY,path TEXT NOT NULL,sha256 TEXT NOT NULL,producer TEXT,created REAL NOT NULL);
''')
            self._db.commit()
    @contextmanager
    def tx(self):
        with self._lock:
            try:
                self._db.execute('BEGIN IMMEDIATE');yield self._db;self._db.commit()
            except Exception:self._db.rollback();raise
    def settings(self,key,default=None):
        with self._lock:r=self._db.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
        return json.loads(r[0]) if r else default
    def setting(self,key,value):
        with self.tx() as db:db.execute('INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,dump(value)))
    def threads(self):
        with self._lock:return [dict(r) for r in self._db.execute('SELECT id,title,created FROM threads ORDER BY created DESC')]
    def thread(self,id):
        with self._lock:r=self._db.execute('SELECT * FROM threads WHERE id=?',(id,)).fetchone()
        if not r:raise KeyError('Conversation not found')
        d=dict(r);d['context']=json.loads(d['context']);return d
    def new_thread(self,title='New conversation'):
        id=uid()
        with self.tx() as db:db.execute('INSERT INTO threads(id,title,created) VALUES(?,?,?)',(id,title[:100],time.time()))
        return self.thread(id)
    def title(self,id,title):
        with self.tx() as db:db.execute('UPDATE threads SET title=? WHERE id=?',(title[:70],id))
    def message(self,thread_id,role,content,meta=None):
        id=uid();ts=time.time()
        with self.tx() as db:db.execute('INSERT INTO messages VALUES(?,?,?,?,?,?)',(id,thread_id,role,content,dump(meta or {}),ts))
        return {'id':id,'thread_id':thread_id,'role':role,'content':content,'meta':meta or {},'ts':ts}
    def messages(self,thread_id):
        self.thread(thread_id)
        with self._lock:rows=self._db.execute('SELECT * FROM messages WHERE thread_id=? ORDER BY ts',(thread_id,)).fetchall()
        return [{**dict(r),'meta':json.loads(r['meta'])} for r in rows]
    def context(self,thread_id,messages):
        with self.tx() as db:db.execute('UPDATE threads SET context=? WHERE id=?',(dump(messages),thread_id))
    def new_run(self,kind,input='',thread_id=None,state=None):
        id=uid();ts=time.time()
        with self.tx() as db:db.execute('INSERT INTO runs(id,thread_id,kind,status,input,state,created,updated) VALUES(?,?,?,\'queued\',?,?,?,?)',(id,thread_id,kind,input,dump(state or {}),ts,ts))
        return self.run(id)
    def run(self,id):
        with self._lock:r=self._db.execute('SELECT * FROM runs WHERE id=?',(id,)).fetchone()
        if not r:raise KeyError('Run not found')
        d=dict(r);d['state']=json.loads(d['state']);d['result']=json.loads(d['result']) if d['result'] else None;return d
    def update_run(self,id,**changes):
        allowed={'status','state','result','error','steps'}
        if not changes or not set(changes)<=allowed:raise ValueError('Invalid run fields')
        values=[];fields=[]
        for k,v in changes.items():fields.append(k+'=?');values.append(dump(v) if k in ['state','result'] and v is not None else v)
        with self.tx() as db:db.execute('UPDATE runs SET '+','.join(fields)+',updated=? WHERE id=?',[*values,time.time(),id])
        return self.run(id)
    def runs(self,limit=80):
        with self._lock:ids=[r[0] for r in self._db.execute('SELECT id FROM runs ORDER BY created DESC LIMIT ?',(limit,))]
        # Never expose raw model contexts in browser activity projections.
        return [{k:v for k,v in self.run(i).items() if k!='state'} for i in ids]
    def approval(self,id):
        with self._lock:r=self._db.execute('SELECT * FROM approvals WHERE id=?',(id,)).fetchone()
        if not r:raise KeyError('Approval not found')
        d=dict(r)
        for k in ['args','precondition','output']:d[k]=json.loads(d[k]) if d[k] else None
        return d
    def approvals(self):
        with self._lock:ids=[r[0] for r in self._db.execute("SELECT id FROM approvals WHERE status='pending' ORDER BY created")]
        return [self.approval(i) for i in ids]
    def new_approval(self,run_id,call_id,tool,args,digest,precondition):
        id=uid()
        with self.tx() as db:db.execute('INSERT INTO approvals(id,run_id,call_id,tool,args,digest,precondition,status,created) VALUES(?,?,?,?,?,?,?,\'pending\',?)',(id,run_id,call_id,tool,dump(args),digest,dump(precondition),time.time()))
        return self.approval(id)
    def claim_approval(self,id):
        with self.tx() as db:
            if db.execute("UPDATE approvals SET status='executing' WHERE id=? AND status='pending'",(id,)).rowcount!=1:raise ValueError('Approval already decided')
    def approval_result(self,id,status,output):
        with self.tx() as db:db.execute('UPDATE approvals SET status=?,output=? WHERE id=?',(status,dump(output),id))
    def cancel(self,id):
        with self.tx() as db:
            r=db.execute('SELECT status FROM runs WHERE id=?',(id,)).fetchone()
            if not r:raise KeyError('Run not found')
            if r[0] in ACTIVE:
                db.execute("UPDATE runs SET status='cancelled',updated=? WHERE id=?",(time.time(),id))
                db.execute("UPDATE approvals SET status='cancelled' WHERE run_id=? AND status='pending'",(id,))
        return self.run(id)
    def recover(self):
        # Never replay an operation whose process died between side effect and commit.
        with self.tx() as db:
            db.execute("UPDATE approvals SET status='unknown_outcome' WHERE status='executing'")
            db.execute("UPDATE runs SET status='interrupted',error='Host restarted during execution. Inspect artifacts before retrying.',updated=? WHERE status IN ('running','queued','cancelling')",(time.time(),))
            db.execute("UPDATE runs SET status='interrupted',error='A side effect has an unknown outcome; automatic replay blocked.' WHERE id IN (SELECT run_id FROM approvals WHERE status='unknown_outcome')")
            db.execute("UPDATE approvals SET status='cancelled' WHERE status='pending' AND run_id IN (SELECT id FROM runs WHERE status='interrupted')")
    def artifacts(self):
        with self._lock:return [dict(r) for r in self._db.execute('SELECT * FROM artifacts ORDER BY updated DESC')]
    def artifact(self,path,sha256,size,mime,producer=None):
        with self.tx() as db:
            db.execute('INSERT INTO artifacts VALUES(?,?,?,?,?,?,?) ON CONFLICT(path) DO UPDATE SET sha256=excluded.sha256,size=excluded.size,mime=excluded.mime,producer=COALESCE(excluded.producer,artifacts.producer),updated=excluded.updated WHERE artifacts.sha256 != excluded.sha256 OR excluded.producer IS NOT NULL',(uid(),path,sha256,size,mime,producer,time.time()))
    def revision(self,path,sha256,producer):
        with self.tx() as db:db.execute('INSERT INTO revisions VALUES(?,?,?,?,?)',(uid(),path,sha256,producer,time.time()))
    def revisions(self,path):
        with self._lock:return [dict(r) for r in self._db.execute('SELECT * FROM revisions WHERE path=? ORDER BY created DESC',(path,))]
    def public_events(self,after=0,limit=150):
        # Existing private/wake/raw-thought records are retained, but not projected.
        kinds=('user','reply','memory','want','self_edit','arrived','offline','tool','run','approval','dataset','file','host','world','training','presence','letter','message','look_back')
        with self._lock:rows=self._db.execute('SELECT * FROM events WHERE id>? AND kind IN (%s) ORDER BY id LIMIT ?'%','.join('?'*len(kinds)),[after,*kinds,limit]).fetchall()
        return [self._row(r) for r in rows]
