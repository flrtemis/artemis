import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {galMakeStarTex,galRemapToSpiral} from './atlas-source.js';
import type {FileEntry} from './client';
function hash(s:string){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return h>>>0;}
export function Atlas({files,selected,onSelect}:{files:FileEntry[];selected:string|null;onSelect:(path:string)=>void}){
 const el=useRef<HTMLDivElement>(null);const [error,setError]=useState('');const [hover,setHover]=useState('');
 useEffect(()=>{if(!el.current)return;const container=el.current;let disposed=false,frame=0;let renderer:THREE.WebGLRenderer;
 try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});}catch{setError('WebGL is unavailable. The same files remain accessible in List view.');return;}
 const scene=new THREE.Scene();scene.background=new THREE.Color('#142c28');scene.fog=new THREE.FogExp2('#142c28',.002);
 const camera=new THREE.PerspectiveCamera(45,1,.1,1000);camera.position.set(10,95,135);renderer.setPixelRatio(Math.min(devicePixelRatio,2));container.append(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.07;controls.minDistance=12;controls.maxDistance=280;
 const records=files.filter(f=>!f.is_dir).map(f=>{const a=hash(f.path),b=hash('y'+f.path),c=hash('z'+f.path);return {...f,x:a%1024,y:b%1024,z:c%1024};});
 const positions=galRemapToSpiral(records);const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));
 const colors=new Float32Array(records.length*3);const sizes=['#78c6ae','#d0be82','#93b6db'];records.forEach((f,i)=>new THREE.Color(sizes[hash(f.mime)%3]).toArray(colors,i*3));geometry.setAttribute('color',new THREE.BufferAttribute(colors,3));
 const texture=galMakeStarTex(128);const material=new THREE.PointsMaterial({size:7,map:texture,transparent:true,vertexColors:true,blending:THREE.AdditiveBlending,depthWrite:false});const points=new THREE.Points(geometry,material);scene.add(points);
 const grid=new THREE.GridHelper(180,24,'#2b6253','#1e443a');grid.position.y=-7;scene.add(grid);
 const ring=new THREE.Mesh(new THREE.RingGeometry(3,3.2,48),new THREE.MeshBasicMaterial({color:'#e9d5a2',side:THREE.DoubleSide}));ring.rotation.x=-Math.PI/2;ring.visible=false;scene.add(ring);
 const i=records.findIndex(r=>r.path===selected);if(i>=0){ring.position.set(positions[i*3],positions[i*3+1]-1,positions[i*3+2]);ring.visible=true;controls.target.copy(new THREE.Vector3(positions[i*3],positions[i*3+1],positions[i*3+2]));}
 const ray=new THREE.Raycaster();ray.params.Points!.threshold=3.5;const mouse=new THREE.Vector2();let down={x:0,y:0};
 const hit=(e:PointerEvent)=>{const r=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);ray.setFromCamera(mouse,camera);return ray.intersectObject(points)[0]?.index;};
 const move=(e:PointerEvent)=>{const h=hit(e);setHover(h===undefined?'':records[h].path);renderer.domElement.style.cursor=h===undefined?'grab':'pointer';};
 const pointerDown=(e:PointerEvent)=>{down={x:e.clientX,y:e.clientY};};const click=(e:PointerEvent)=>{if(Math.hypot(e.clientX-down.x,e.clientY-down.y)>5)return;const h=hit(e);if(h!==undefined)onSelect(records[h].path);};
 renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerdown',pointerDown);renderer.domElement.addEventListener('pointerup',click);
 const resize=new ResizeObserver(()=>{const w=container.clientWidth,h=container.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/Math.max(1,h);camera.updateProjectionMatrix();});resize.observe(container);
 const animate=()=>{if(disposed)return;frame=requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);};animate();
 return()=>{disposed=true;cancelAnimationFrame(frame);resize.disconnect();controls.dispose();geometry.dispose();material.dispose();texture.dispose();grid.geometry.dispose();(grid.material as THREE.Material).dispose();ring.geometry.dispose();(ring.material as THREE.Material).dispose();renderer.dispose();container.replaceChildren();};
 },[files.map(f=>f.path).join('|'),selected]);
 return <div className="atlas-shell"><div ref={el} className="atlas-canvas"/>{error&&<div className="atlas-message">{error}</div>}{!files.filter(f=>!f.is_dir).length&&<div className="atlas-message"><strong>Your workspace, mapped.</strong><span>Upload or create a file to give it a place in the Atlas.</span></div>}<div className="atlas-caption"><span className="live-dot"/> {files.filter(f=>!f.is_dir).length} actual artifacts · shared selection · drag to orbit</div>{hover&&<div className="atlas-hover">{hover}</div>}</div>;
}
