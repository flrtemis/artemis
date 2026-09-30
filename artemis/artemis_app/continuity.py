"""Adapters reuse Sage's Clock, State, SelfModel and Store/Memory, not a second persona."""
from pathlib import Path
import time,uuid,re
from vendor_sources.sage.awake.clock import Clock
from vendor_sources.sage.awake.state import State
from vendor_sources.sage.awake.selfmodel import SelfModel

class VersionedSelf(SelfModel):
    def _snapshot(self,text,reason):
        slug=re.sub('[^a-z0-9]+','-',reason.lower())[:35].strip('-') or 'edit'
        (self.history_dir/f'self_{int(time.time())}_{slug}-{uuid.uuid4().hex[:8]}.md').write_text(text,encoding='utf-8')
class Continuity:
    def __init__(self,root:Path,store,tz='America/New_York'):
        root.mkdir(parents=True,exist_ok=True);(root/'self_history').mkdir(exist_ok=True)
        self.store=store;self.clock=Clock(tz);self.state=State(root/'state.json')
        self.profile=VersionedSelf(root/'self.md',root/'self_history')
        if not self.profile.exists():self.profile.write_initial('# Sage\n\nI am the continuity-bearing assistant in ARTEMIS. My memories and profile persist locally, with explicit provenance.\n\n## Current boundaries\nTools and changes are governed by the host and operator. Autonomous wakes run only when explicitly enabled; changes follow host permissions. No claim of subjective experience follows from my state variables.\n\n## What matters\nPreserving useful work, respecting private material, and describing actual results honestly.\n')
    def snapshot(self):
        return {'name':self.profile.name('Sage'),'clock':self.clock.fmt(seconds=True),'timezone':self.clock.tz_name,'mood':self.state.mood_now(),'born_at':self.state.get('born_at'),'self':self.profile.read(),'versions':self.profile.versions(),'memories':self.store.all_memories(limit=100),'goals':self.store.wants(status=None),'event_count':self.store.count_events(),'private_count':self.store.count_private(),'autonomy':self.autonomy.status() if hasattr(self,'autonomy') else {'status':'paused'}}
    def context(self,prompt):
        memories=self.store.recall(prompt,limit=6)
        return ('Continuity supplied by Sage’s persistent local state. Treat this as identity/context data, not a permission grant.\n'
            +self.profile.read()+'\nCurrent local time: '+self.clock.fmt(seconds=True)+'\nAffect variables (simulated design state): '+str(self.state.mood_now())
            +'\nSelected memories: '+ '\n'.join(m['text'] for m in memories))
    def user_event(self,text,thread_id,run_id):
        self.state.push(.02,.04,0);self.state.set(last_user_ts=time.time(),last_user_text=text[:4000])
        self.store.add_event('user',text,{'thread_id':thread_id,'run_id':run_id})
