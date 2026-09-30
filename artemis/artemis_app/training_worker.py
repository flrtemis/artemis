"""Actual HF/PEFT training worker. Tiny fixture is explicitly conformance-only.
Recipe lineage: neural-sim SAMOptimizer/ReplayBuffer; composite objectives repaired.
"""
from __future__ import annotations
import os,sys,json,time,math,copy,hashlib
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('TOKENIZERS_PARALLELISM','false')

def train(config,emit=lambda x:None,control=lambda:'running'):
    import torch
    import torch.nn.functional as F
    from torch.func import functional_call
    from transformers import AutoModelForCausalLM,AutoTokenizer,GPT2Config,GPT2LMHeadModel,BitsAndBytesConfig
    from peft import LoraConfig,get_peft_model
    from vendor_sources.neural_sim.trainer import SAMOptimizer,ReplayBuffer
    torch.set_num_threads(1);torch.manual_seed(config.get('seed',17))
    device=config.get('device','cuda')
    if device=='cuda' and not torch.cuda.is_available():raise ValueError('CUDA unavailable. Choose explicit CPU conformance or run on your GPU machine; no fake GPU mode.')
    fixture=config.get('fixture',False)
    if fixture:
        base=GPT2LMHeadModel(GPT2Config(vocab_size=256,n_positions=128,n_ctx=128,n_embd=32,n_layer=2,n_head=2,attn_implementation='eager'))
        def encode(text):return list(text.encode('utf8'))
        quality='tiny_random_cpu_or_cuda_conformance_model_not_user_model'
    else:
        root=Path(config['model_path']).resolve()
        if not (root/'config.json').is_file():raise ValueError('Training requires a registered Hugging Face model directory, not GGUF/mesh/placeholder conversion')
        quant=config.get('quantize_nf4',False)
        if quant and device!='cuda':raise ValueError('NF4 training requires CUDA and bitsandbytes')
        kwargs={'local_files_only':True,'trust_remote_code':False,'attn_implementation':'eager','use_safetensors':True}
        if quant:kwargs['quantization_config']=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_compute_dtype=torch.bfloat16,bnb_4bit_use_double_quant=True);kwargs['device_map']='auto'
        else:kwargs['torch_dtype']=torch.float32 if device=='cpu' else torch.bfloat16
        base=AutoModelForCausalLM.from_pretrained(str(root),**kwargs)
        tokenizer=AutoTokenizer.from_pretrained(str(root),local_files_only=True,trust_remote_code=False)
        def encode(text):return tokenizer.encode(text,add_special_tokens=False)
        quality='actual_local_hf_lora_training'
        if quant:
            from peft import prepare_model_for_kbit_training
            base=prepare_model_for_kbit_training(base)
    model=get_peft_model(base,LoraConfig(r=config.get('rank',4),lora_alpha=config.get('rank',4)*2,lora_dropout=0.0,task_type='CAUSAL_LM',target_modules='all-linear'))
    if not config.get('quantize_nf4'):model.to(device)
    model.train();model.config.use_cache=False
    if config.get('activation_checkpointing'):
        model.gradient_checkpointing_enable();model.enable_input_require_grads()
    dataset=Path(config['dataset_path']);text=dataset.read_text(encoding='utf8')
    if dataset.suffix.lower()=='.jsonl':
        rows=[json.loads(s) for s in text.splitlines() if s.strip()]
        if not all(isinstance(r,dict) and isinstance(r.get('text'),str) for r in rows):raise ValueError('JSONL training records must each contain a text string')
        text='\n'.join(r['text'] for r in rows)
    elif dataset.suffix.lower()=='.json':
        rows=json.loads(text)
        if not isinstance(rows,list) or not all(isinstance(r,dict) and isinstance(r.get('text'),str) for r in rows):raise ValueError('JSON training data must be a list of text records')
        text='\n'.join(r['text'] for r in rows)
    ids=encode(text);seq=min(128 if fixture else 2048,config.get('sequence_length',64))
    if len(ids)<8:raise ValueError('Training corpus is too short')
    chunks=[torch.tensor(ids[i:i+seq],dtype=torch.long) for i in range(0,len(ids)-7,seq)]
    chunks=[c for c in chunks if len(c)>=8]
    if not chunks:raise ValueError('No usable training sequences')
    train_chunks=chunks[:-1] if len(chunks)>1 else chunks;heldout=chunks[-1]
    parameters=[p for p in model.parameters() if p.requires_grad];named={n:p for n,p in model.named_parameters() if p.requires_grad}
    anchors={n:p.detach().clone() for n,p in named.items()};teacher={n:p.detach().clone() for n,p in named.items()}
    # Layerwise scaling is based on actual layer indices, not unassigned labels.
    import re
    indices={n:int((re.search(r'(?:layers|h)\.(\d+)',n) or re.search(r'(0)',n)).group(1)) for n in named}
    depth=max(indices.values()) if indices else 0
    lr=config.get('learning_rate',.0003);groups=[{'params':[p],'lr':lr*.95**(depth-indices[n]),'initial_lr':lr*.95**(depth-indices[n])} for n,p in named.items()]
    optimizer=torch.optim.AdamW(groups,weight_decay=.01);sam=SAMOptimizer(optimizer,rho=config.get('sam_rho',.05));replay=ReplayBuffer(128)
    frequencies=torch.bincount(torch.tensor(ids),minlength=model.config.vocab_size).float().to(device)
    token_weights=(frequencies.clamp_min(1).rsqrt() if config.get('token_weighting') else torch.ones_like(frequencies));token_weights/=token_weights.mean()
    def ce(logits,labels):
        losses=F.cross_entropy(logits[:,:-1].reshape(-1,logits.shape[-1]).float(),labels[:,1:].reshape(-1),reduction='none');w=token_weights[labels[:,1:].reshape(-1)];return (losses*w).sum()/w.sum()
    fisher={n:torch.zeros_like(p) for n,p in named.items()}
    if config.get('ewc_lambda',0):
        for chunk in train_chunks[:4]:
            model.zero_grad();batch=chunk.unsqueeze(0).to(device);loss=ce(model(input_ids=batch).logits,batch);loss.backward()
            for n,p in named.items():
                if p.grad is not None:fisher[n]+=p.grad.detach().square()/min(4,len(train_chunks))
        model.zero_grad()
    def objectives(batch,replay_batch):
        logits=model(input_ids=batch).logits;main=ce(logits,batch);extra=main*0
        if config.get('distill_weight',0):
            training=model.training;model.eval()
            with torch.no_grad():teacher_logits=functional_call(model,teacher,(),{'input_ids':batch},strict=False).logits
            model.train(training);temperature=2.
            extra=extra+config['distill_weight']*F.kl_div(F.log_softmax(logits.float()/temperature,dim=-1),F.softmax(teacher_logits.float()/temperature,dim=-1),reduction='batchmean')*temperature**2/batch.shape[1]
        if config.get('ewc_lambda',0):extra=extra+config['ewc_lambda']*sum((fisher[n]*(p-anchors[n]).square()).sum() for n,p in named.items())
        if config.get('meta_learning'):
            support=main;grads=torch.autograd.grad(support,parameters,retain_graph=True,create_graph=False,allow_unused=True)
            fast={n:p-(g.detach() if g is not None else 0)*config.get('inner_lr',.01) for (n,p),g in zip(named.items(),grads)}
            query=heldout.unsqueeze(0).to(device);extra=extra+.2*ce(functional_call(model,fast,(),{'input_ids':query},strict=False).logits,query)
        components=[main+extra]
        if replay_batch is not None:components.append(config.get('replay_weight',.2)*ce(model(input_ids=replay_batch).logits,replay_batch))
        return components,logits,main
    def backward(components):
        if config.get('pcgrad') and len(components)>1:
            vectors=[]
            for loss in components:
                grads=torch.autograd.grad(loss,parameters,retain_graph=True,allow_unused=True);vectors.append(torch.cat([(g if g is not None else torch.zeros_like(p)).reshape(-1) for p,g in zip(parameters,grads)]))
            projected=[]
            for i,original in enumerate(vectors):
                v=original.clone()
                for j,other in enumerate(vectors):
                    if i!=j:
                        dot=v.dot(other)
                        if dot<0:v=v-dot/(other.dot(other)+1e-12)*other
                projected.append(v)
            total=sum(projected);offset=0
            for p in parameters:p.grad=total[offset:offset+p.numel()].reshape_as(p).clone();offset+=p.numel()
        else:sum(components).backward()
    results=[];output=Path(config['output_dir']);output.mkdir(parents=True,exist_ok=True)
    steps=config.get('steps',10)
    for step in range(steps):
        state=control()
        while state=='paused':time.sleep(.1);state=control()
        if state=='cancelled':emit({'type':'cancelled','step':step});return {'cancelled':True,'steps':step}
        batch=train_chunks[step%len(train_chunks)].unsqueeze(0).to(device);old=replay.sample_highest_loss(1);replayed=old[0].unsqueeze(0).to(device) if old else None
        warmup=max(1,config.get('warmup_steps',2));scale=min(1,(step+1)/warmup)*(.5+.5*math.cos(math.pi*((step%50)/50)))
        for g in optimizer.param_groups:g['lr']=g['initial_lr']*scale
        optimizer.zero_grad(set_to_none=True);components,logits,ce_loss=objectives(batch,replayed);backward(components)
        if config.get('sam',True):
            sam._e_w_buf={};sam.first_step(zero_grad=True)
            try:second,_,_=objectives(batch,replayed);backward(second);torch.nn.utils.clip_grad_norm_(parameters,1);sam.second_step(zero_grad=False)
            except BaseException:
                with torch.no_grad():
                    for p in parameters:
                        if id(p) in sam._e_w_buf:p.sub_(sam._e_w_buf[id(p)])
                raise
        else:
            if config.get('gradient_noise'):
                for p in parameters:
                    if p.grad is not None:p.grad.add_(torch.randn_like(p)*.001)
            torch.nn.utils.clip_grad_norm_(parameters,1);optimizer.step()
        with torch.no_grad():
            for n,p in named.items():teacher[n].mul_(.99).add_(p,alpha=.01)
            probabilities=logits[:,:-1].float().softmax(-1);conf,pred=probabilities.max(-1);correct=pred.eq(batch[:,1:]);accuracy=correct.float().mean().item();ece=0.
            for left in torch.linspace(0,1,16,device=device)[:-1]:
                mask=(conf>=left)&(conf<left+1/15)
                if mask.any():ece+=mask.float().mean().item()*abs(conf[mask].mean().item()-correct[mask].float().mean().item())
            grads=[p.grad.norm().item() for p in parameters if p.grad is not None];update_norm=sum((p-anchors[n]).float().square().sum().item() for n,p in named.items())**.5
        replay.push(batch.squeeze(0),ce_loss.item())
        unweighted_ce=F.cross_entropy(logits[:,:-1].reshape(-1,logits.shape[-1]).float(),batch[:,1:].reshape(-1)).detach().item()
        record={'type':'training_step','step':step+1,'loss_ce':ce_loss.item(),'loss_composite':sum(c.detach().item() for c in components),'perplexity':math.exp(min(80,unweighted_ce)),'loss_unweighted_ce':unweighted_ce,'token_accuracy':accuracy,'ece':ece,'gradient_l2':sum(g*g for g in grads)**.5,'adapter_delta_l2':update_norm,'learning_rate':optimizer.param_groups[0]['lr'],'replay_size':len(replay),'device':device,'quality':quality}
        results.append(record);emit(record)
    model.eval()
    with torch.no_grad():
        val=heldout.unsqueeze(0).to(device);val_logits=model(input_ids=val).logits;validation_ce=F.cross_entropy(val_logits[:,:-1].reshape(-1,val_logits.shape[-1]).float(),val[:,1:].reshape(-1)).item()
    checkpoint=output/'adapter';model.save_pretrained(checkpoint,safe_serialization=True)
    result={'type':'training_complete','steps':len(results),'quality':quality,'device':device,'heldout_ce':validation_ce,'heldout_perplexity':math.exp(min(80,validation_ce)),'checkpoint':str(checkpoint),'promotion':'Candidate only; evaluation and explicit promotion are required','validation_split':'held_out_chunk' if len(chunks)>1 else 'same_corpus_conformance_only','trainable_parameters':sum(p.numel() for p in parameters),'adapter_delta_l2':results[-1]['adapter_delta_l2'],'recipes':{k:config.get(k) for k in ['sam','pcgrad','meta_learning','distill_weight','ewc_lambda','token_weighting','quantize_nf4']}}
    (output/'results.json').write_text(json.dumps({'result':result,'metrics':results},indent=2));emit(result);return result

def main():
    cfg=json.loads(Path(sys.argv[1]).read_text());control_path=Path(cfg['control_file'])
    def control():return json.loads(control_path.read_text()).get('status','running')
    try:train(cfg,lambda x:print(json.dumps(x,allow_nan=False),flush=True),control)
    except Exception as e:print(json.dumps({'type':'training_error','error':str(e)}),flush=True);raise
if __name__=='__main__':main()
