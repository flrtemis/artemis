// Scene builders/room geometry/brain positions ported from pinned Command Center.
import * as THREE from 'three';
export function createFacility(scene, status={}) {
let MAT={};const collisionBoxes=[],interactiveObjects=[],roomZones=[];const monitorMeshes={};const runningTools=status;
const CFG = {
  CEILING_H: 3.4,
  EYE_H: 1.65,
  WALL_THICK: 0.15,
  DOOR_W: 2.8,
  DOOR_H: 2.6,
  MOVE_SPEED: 4.5,
  SPRINT_MULT: 1.8,
  PLAYER_RADIUS: 0.35,
  INTERACT_DIST: 2.8,
  MOUSE_SENS: 0.002,
};

const TOOLS = {
  artemis: { name: 'ARTEMIS (Sage)', desc: 'Unified AI kernel — memory, mind, senses, voice, bridge, guardian, feelings, appraisal. The central nervous system.', tags: ['Python','FastAPI','SQLite','WebSocket'], hasLaunch: true },
  ears: { name: 'ARTEMIS Ears', desc: 'Adaptive audio perception. Speech-to-text via faster-whisper, audio analysis via librosa. The hearing sense.', tags: ['Python','faster-whisper','librosa'], hasLaunch: true },
  csm: { name: 'CSM-1B Voice', desc: 'Conversational speech synthesis. Wav-to-wav generation on RTX 5070 Ti via WSL CUDA.', tags: ['Python','PyTorch','WSL/CUDA'], hasLaunch: true },
  'neural-sim': { name: 'Neural Simulation', desc: 'Real-time LLM training dashboard. Anatomical 8192-point brain clouds (human + AI), 48 diagnostic metrics, LoRA fine-tuning with MAML meta-learning, SAM optimizer, self-modification engine with Bayesian optimization & rollback, EWC continual learning, gradient surgery, EMA teacher distillation, live WebSocket brain reactivity.', tags: ['Python','Three.js','WSL/CUDA','LoRA','MAML','SAM','EWC','BayesOpt'], hasLaunch: true, url: 'http://localhost:8765' },
  'artemis-server': { name: 'Artemis Server', desc: 'Portable HTTP file server with Cloudflare tunnel integration and Tkinter GUI.', tags: ['Go','Python/Tkinter'], hasLaunch: true },
  comms: { name: 'Comms Platform', desc: 'AI-coordinated node-to-node encrypted communication platform.', tags: ['Python','FastAPI','WebSocket'], hasLaunch: true },
  'converter-gui': { name: 'Bat→Exe Converter', desc: 'Reverse-engineered reimplementation. Converts .bat scripts to standalone .exe with custom C stubs.', tags: ['Python','C'], hasLaunch: true },
  gateway: { name: 'Gateway Router', desc: 'Dual-node virtual private router. WireGuard config generation and keepalive management.', tags: ['Python','WireGuard'], hasLaunch: true },
  mirror: { name: 'Mirror', desc: 'ADB screen mirror service. Captures Android device screen and serves it via FastAPI.', tags: ['Python','FastAPI','ADB'], hasLaunch: true },
  ghidra: { name: 'Ghidra 12.0.4', desc: 'Full static analysis suite for binaries — DEX, SO, APK, ELF, PE. Pre-built distribution.', tags: ['Java','Ghidra'], hasLaunch: true },
  frida: { name: 'Frida 17.8.2', desc: 'Runtime function hooking for Android. ARM + ARM64 server binaries ready.', tags: ['JavaScript','Android'], hasLaunch: false },
  wireshark: { name: 'Wireshark + Zeek + nDPI', desc: 'Packet capture, protocol dissection, JA3 fingerprinting, deep packet inspection.', tags: ['Network','WSL'], hasLaunch: false },
  'ghidra-scripts': { name: 'Ghidra Scripts', desc: '9 automated analysis scripts — decompilation, string extraction, import analysis, section mapping.', tags: ['Python','Ghidra'], hasLaunch: false },
  'frida-hooks': { name: 'Frida Hooks', desc: 'SSL pinning bypass, function tracing, memory dumping hook scripts.', tags: ['JavaScript','Frida'], hasLaunch: false },
  playbooks: { name: 'Playbooks', desc: '4 YAML automation playbooks — guardian-start, neural-sim-launch, WSL dep-check, WSL emergency-stop.', tags: ['YAML','Python'], hasLaunch: false },
  'ref-apks': { name: 'Reference APK Library', desc: '13 decompiled APK packages studied for architectural patterns and design principles.', tags: ['APK','Java','Smali'], hasLaunch: false },
};

function makeCanvasTexture(w, h, drawFn) {
  const canvas = document.createElement('canvas');
  canvas.width = w; canvas.height = h;
  const ctx = canvas.getContext('2d');
  drawFn(ctx, w, h);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function wallTexture() {
  return makeCanvasTexture(256, 256, (ctx, w, h) => {
    // Warm cream base
    ctx.fillStyle = '#e8e0d4';
    ctx.fillRect(0, 0, w, h);
    // Subtle noise
    for (let i = 0; i < 800; i++) {
      const x = Math.random() * w, y = Math.random() * h;
      const v = 200 + Math.random() * 40;
      ctx.fillStyle = `rgb(${v},${v-8},${v-16})`;
      ctx.fillRect(x, y, 2, 2);
    }
    // Faint horizontal line (drywall seam)
    ctx.strokeStyle = 'rgba(180,170,155,.15)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(0, h/2); ctx.lineTo(w, h/2); ctx.stroke();
  });
}

function floorTexture() {
  return makeCanvasTexture(512, 512, (ctx, w, h) => {
    // Dark industrial floor
    ctx.fillStyle = '#3a3832';
    ctx.fillRect(0, 0, w, h);
    // Tile grid
    const tileSize = 64;
    ctx.strokeStyle = 'rgba(80,76,68,.3)';
    ctx.lineWidth = 1;
    for (let x = 0; x <= w; x += tileSize) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y <= h; y += tileSize) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }
    // Subtle noise
    for (let i = 0; i < 2000; i++) {
      const x = Math.random() * w, y = Math.random() * h;
      const v = 50 + Math.random() * 20;
      ctx.fillStyle = `rgba(${v},${v-2},${v-4},.4)`;
      ctx.fillRect(x, y, 1, 1);
    }
  });
}

function ceilingTexture() {
  return makeCanvasTexture(256, 256, (ctx, w, h) => {
    ctx.fillStyle = '#f0ece4';
    ctx.fillRect(0, 0, w, h);
    // Ceiling tile grid
    ctx.strokeStyle = 'rgba(180,172,160,.2)';
    ctx.lineWidth = 1;
    const tile = 128;
    for (let x = 0; x <= w; x += tile) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y <= h; y += tile) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }
  });
}

function trimTexture() {
  return makeCanvasTexture(64, 64, (ctx, w, h) => {
    ctx.fillStyle = '#5a4a38';
    ctx.fillRect(0, 0, w, h);
    // Wood grain
    for (let y = 0; y < h; y += 2) {
      ctx.strokeStyle = `rgba(${70+Math.random()*20},${55+Math.random()*15},${40+Math.random()*10},.3)`;
      ctx.beginPath(); ctx.moveTo(0, y + Math.random()*2); ctx.lineTo(w, y + Math.random()*2); ctx.stroke();
    }
  });
}

function signTexture(text, accent = '#8a9aa8') {
  return makeCanvasTexture(512, 128, (ctx, w, h) => {
    // Dark background
    ctx.fillStyle = '#2a2824';
    ctx.fillRect(0,0,w,h);
    // Border
    ctx.strokeStyle = accent;
    ctx.lineWidth = 2;
    ctx.strokeRect(4,4,w-4,h-4);
    // Text
    ctx.font = 'bold 32px Segoe UI, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = accent;
    ctx.fillText(text, w/2, h/2);
  });
}

function monitorTexture(toolId) {
  const tool = TOOLS[toolId];
  if (!tool) return makeCanvasTexture(512, 384, (ctx,w,h) => { ctx.fillStyle='#111';ctx.fillRect(0,0,w,h); });

  return makeCanvasTexture(512, 384, (ctx, w, h) => {
    // Screen bg
    ctx.fillStyle = '#0c0e10';
    ctx.fillRect(0,0,w,h);

    // Subtle grid
    ctx.strokeStyle = 'rgba(100,140,160,.06)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 32) { ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke(); }
    for (let y = 0; y < h; y += 32) { ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke(); }

    // Header bar
    ctx.fillStyle = 'rgba(60,90,110,.15)';
    ctx.fillRect(0,0,w,48);
    ctx.strokeStyle = 'rgba(100,140,160,.2)';
    ctx.beginPath();ctx.moveTo(0,48);ctx.lineTo(w,48);ctx.stroke();

    // Title
    ctx.font = 'bold 20px Segoe UI, sans-serif';
    ctx.fillStyle = '#a0c0d0';
    ctx.textAlign = 'left';
    ctx.fillText(tool.name, 16, 32);

    // Status indicator
    const running = runningTools[toolId];
    ctx.beginPath();
    ctx.arc(w - 24, 24, 6, 0, Math.PI*2);
    ctx.fillStyle = running ? '#6a9a6a' : '#5a5a5a';
    ctx.fill();

    // Description
    ctx.font = '14px Segoe UI, sans-serif';
    ctx.fillStyle = '#7a8a90';
    const words = tool.desc.split(' ');
    let line = '', lineY = 80;
    for (const word of words) {
      const test = line + word + ' ';
      if (ctx.measureText(test).width > w - 32) {
        ctx.fillText(line.trim(), 16, lineY);
        line = word + ' '; lineY += 20;
        if (lineY > 160) break;
      } else { line = test; }
    }
    if (line.trim()) ctx.fillText(line.trim(), 16, lineY);

    // Tags
    let tagX = 16;
    const tagY = 200;
    ctx.font = '12px Cascadia Code, monospace';
    for (const tag of tool.tags) {
      const tw = ctx.measureText(tag).width + 16;
      ctx.strokeStyle = 'rgba(100,140,160,.25)';
      ctx.strokeRect(tagX, tagY, tw, 22);
      ctx.fillStyle = '#6a8a9a';
      ctx.fillText(tag, tagX + 8, tagY + 15);
      tagX += tw + 6;
      if (tagX > w - 40) break;
    }

    // Bottom status bar
    ctx.fillStyle = 'rgba(60,90,110,.1)';
    ctx.fillRect(0, h-36, w, 36);
    ctx.font = '11px Cascadia Code, monospace';
    ctx.fillStyle = running ? '#6a9a6a' : '#5a5a5a';
    ctx.fillText(running ? '● CONNECTED' : '○ RETAINED / UNAVAILABLE', 16, h-14);

    if (tool.hasLaunch) {
      ctx.fillStyle = '#4a6a7a';
      ctx.fillText('PRESS E TO MANAGE', w - 160, h-14);
    }

    // Scanline effect
    for (let y = 0; y < h; y += 4) {
      ctx.fillStyle = 'rgba(0,0,0,.04)';
      ctx.fillRect(0, y, w, 2);
    }
  });
}

function hubFloorTexture() {
  return makeCanvasTexture(512, 512, (ctx, w, h) => {
    // Dark floor base
    ctx.fillStyle = '#3a3832';
    ctx.fillRect(0, 0, w, h);
    // Compass rose / directional markers
    ctx.strokeStyle = 'rgba(160,150,130,.15)';
    ctx.lineWidth = 2;
    // Circle
    ctx.beginPath(); ctx.arc(w/2, h/2, 200, 0, Math.PI*2); ctx.stroke();
    ctx.beginPath(); ctx.arc(w/2, h/2, 140, 0, Math.PI*2); ctx.stroke();
    // Cross lines
    ctx.beginPath(); ctx.moveTo(w/2, 40); ctx.lineTo(w/2, h-40); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(40, h/2); ctx.lineTo(w-40, h/2); ctx.stroke();
    // ARTEMIS text
    ctx.font = 'bold 36px Segoe UI, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillStyle = 'rgba(160,150,130,.12)';
    ctx.fillText('ARTEMIS', w/2, h/2 + 12);
    // Direction labels
    ctx.font = '14px Segoe UI, sans-serif';
    ctx.fillStyle = 'rgba(160,150,130,.2)';
    ctx.fillText('AI SYSTEMS', w/2, 70);
    ctx.fillText('SCRIPTS', w/2, h - 56);
    ctx.save(); ctx.translate(w-56, h/2); ctx.rotate(-Math.PI/2); ctx.fillText('ANALYSIS', 0, 0); ctx.restore();
    ctx.save(); ctx.translate(56, h/2); ctx.rotate(Math.PI/2); ctx.fillText('TOOLS', 0, 0); ctx.restore();
  });
}

function buildMaterials() {
  const wallTex = wallTexture();
  wallTex.wrapS = wallTex.wrapT = THREE.RepeatWrapping;
  wallTex.repeat.set(2, 1);

  const floorTex = floorTexture();
  floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping;

  const ceilTex = ceilingTexture();
  ceilTex.wrapS = ceilTex.wrapT = THREE.RepeatWrapping;

  MAT = {
    wall: new THREE.MeshStandardMaterial({ map: wallTex, roughness: 0.85, metalness: 0.0 }),
    floor: new THREE.MeshStandardMaterial({ map: floorTex, roughness: 0.75, metalness: 0.1 }),
    ceiling: new THREE.MeshStandardMaterial({ map: ceilTex, roughness: 0.9, metalness: 0.0 }),
    trim: new THREE.MeshStandardMaterial({ map: trimTexture(), roughness: 0.6, metalness: 0.1 }),
    doorFrame: new THREE.MeshStandardMaterial({ color: 0x4a3a2a, roughness: 0.5, metalness: 0.1 }),
    monitorBezel: new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.3, metalness: 0.6 }),
    desk: new THREE.MeshStandardMaterial({ color: 0x5a5048, roughness: 0.55, metalness: 0.15 }),
    metal: new THREE.MeshStandardMaterial({ color: 0x8a8a8a, roughness: 0.35, metalness: 0.7 }),
    lightPanel: new THREE.MeshStandardMaterial({
      color: 0xfff8ee, emissive: 0xfff4e0, emissiveIntensity: 0.8, roughness: 1.0, metalness: 0.0
    }),
    lightPanelOff: new THREE.MeshStandardMaterial({
      color: 0xe0d8cc, roughness: 0.9, metalness: 0.0
    }),
  };
}

const ROOMS = [
  // Central Hub
  { name: 'Central Hub', x1:-4.5, z1:-4.5, x2:4.5, z2:4.5, color: '#a09888',
    openings: [
      { wall:'n', center:0 }, { wall:'e', center:0 },
      { wall:'s', center:0 }, { wall:'w', center:0 },
    ]
  },
  // North corridor
  { name: 'North Corridor', x1:-1.5, z1:4.5, x2:1.5, z2:9, color: '#8a9aa8', openings: [
    { wall:'s', center:0 }, { wall:'n', center:0 },
  ]},
  // AI Systems Lab
  { name: 'AI Systems Lab', x1:-5.5, z1:9, x2:5.5, z2:17, color: '#8aaab8', openings: [
    { wall:'s', center:0 },
  ], tools: ['artemis','ears','csm','neural-sim'] },
  // East corridor
  { name: 'East Corridor', x1:4.5, z1:-1.5, x2:9, z2:1.5, color: '#a0a888', openings: [
    { wall:'w', center:0 }, { wall:'e', center:0 },
  ]},
  // Analysis Lab
  { name: 'Analysis Lab', x1:9, z1:-5.5, x2:18, z2:5.5, color: '#a89a88', openings: [
    { wall:'w', center:0 },
  ], tools: ['ghidra','frida','wireshark'] },
  // South corridor
  { name: 'South Corridor', x1:-1.5, z1:-9, x2:1.5, z2:-4.5, color: '#9a8ab8', openings: [
    { wall:'n', center:0 }, { wall:'s', center:0 },
  ]},
  // Scripts & Automation
  { name: 'Scripts & Automation', x1:-5.5, z1:-17, x2:5.5, z2:-9, color: '#9a88b8', openings: [
    { wall:'n', center:0 },
  ], tools: ['ghidra-scripts','frida-hooks','playbooks','ref-apks'] },
  // West corridor
  { name: 'West Corridor', x1:-9, z1:-1.5, x2:-4.5, z2:1.5, color: '#88a898', openings: [
    { wall:'e', center:0 }, { wall:'w', center:0 },
  ]},
  // Built Tools Workshop
  { name: 'Built Tools Workshop', x1:-18, z1:-5.5, x2:-9, z2:5.5, color: '#88a888', openings: [
    { wall:'e', center:0 },
  ], tools: ['artemis-server','comms','converter-gui','gateway','mirror'] },
];

function addBox(w, h, d, x, y, z, mat, castShadow=false, receiveShadow=false) {
  const geo = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, y, z);
  mesh.castShadow = castShadow;
  mesh.receiveShadow = receiveShadow;
  scene.add(mesh);
  return mesh;
}

function addCollisionBox(x1, z1, x2, z2, y=0, h=CFG.CEILING_H) {
  collisionBoxes.push(new THREE.Box3(
    new THREE.Vector3(Math.min(x1,x2), y, Math.min(z1,z2)),
    new THREE.Vector3(Math.max(x1,x2), y+h, Math.max(z1,z2))
  ));
}

function buildWallSegment(x, z, w, h, d, mat) {
  const mesh = addBox(w, h, d, x, h/2, z, mat, false, true);
  return mesh;
}

function buildRoom(room) {
  const { x1, z1, x2, z2, openings = [], name } = room;
  const w = x2 - x1, d = z2 - z1;
  const cx = (x1 + x2) / 2, cz = (z1 + z2) / 2;
  const H = CFG.CEILING_H;
  const T = CFG.WALL_THICK;
  const DW = CFG.DOOR_W;
  const DH = CFG.DOOR_H;

  // Floor
  const floorMat = (name === 'Central Hub') ?
    new THREE.MeshStandardMaterial({ map: hubFloorTexture(), roughness: 0.7, metalness: 0.1 }) :
    MAT.floor.clone();
  floorMat.map = floorMat.map || MAT.floor.map;
  if (floorMat.map && name !== 'Central Hub') {
    floorMat.map = floorMat.map.clone();
    floorMat.map.repeat.set(w/4, d/4);
    floorMat.map.wrapS = floorMat.map.wrapT = THREE.RepeatWrapping;
  }
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(w, d), floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(cx, 0.001, cz);
  floor.receiveShadow = true;
  scene.add(floor);

  // Ceiling
  const ceilMat = MAT.ceiling.clone();
  if (ceilMat.map) {
    ceilMat.map = ceilMat.map.clone();
    ceilMat.map.repeat.set(w/3, d/3);
    ceilMat.map.wrapS = ceilMat.map.wrapT = THREE.RepeatWrapping;
  }
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(w, d), ceilMat);
  ceil.rotation.x = Math.PI / 2;
  ceil.position.set(cx, H, cz);
  scene.add(ceil);

  // Room zone for detection
  roomZones.push({ name, x1, z1, x2, z2 });

  // Walls — for each side, check if there's an opening
  const sides = [
    { wall: 'n', sx: x1, sz: z2, ex: x2, ez: z2, axis: 'x', normal: [0,0,-1] },
    { wall: 's', sx: x1, sz: z1, ex: x2, ez: z1, axis: 'x', normal: [0,0,1]  },
    { wall: 'e', sx: x2, sz: z1, ex: x2, ez: z2, axis: 'z', normal: [-1,0,0] },
    { wall: 'w', sx: x1, sz: z1, ex: x1, ez: z2, axis: 'z', normal: [1,0,0]  },
  ];

  for (const side of sides) {
    const opening = openings.find(o => o.wall === side.wall);

    if (side.axis === 'x') {
      // Wall runs along X
      const wallLen = Math.abs(side.ex - side.sx);
      const wallZ = side.sz;
      const wallCx = (side.sx + side.ex) / 2;

      if (opening) {
        const openCenter = wallCx + (opening.center || 0);
        const leftLen = openCenter - DW/2 - side.sx;
        const rightLen = side.ex - (openCenter + DW/2);

        // Left segment
        if (leftLen > 0.1) {
          const lx = side.sx + leftLen/2;
          buildWallSegment(lx, wallZ, leftLen, H, T, MAT.wall);
          addCollisionBox(side.sx, wallZ - T/2, side.sx + leftLen, wallZ + T/2);
        }
        // Right segment
        if (rightLen > 0.1) {
          const rx = side.ex - rightLen/2;
          buildWallSegment(rx, wallZ, rightLen, H, T, MAT.wall);
          addCollisionBox(side.ex - rightLen, wallZ - T/2, side.ex, wallZ + T/2);
        }
        // Lintel above door
        const lintelH = H - DH;
        if (lintelH > 0.1) {
          buildWallSegment(openCenter, wallZ, DW, lintelH, T, MAT.wall);
          // No collision for lintel (above player)
        }
        // Door frame
        addBox(0.08, DH, T+0.04, openCenter - DW/2, DH/2, wallZ, MAT.doorFrame);
        addBox(0.08, DH, T+0.04, openCenter + DW/2, DH/2, wallZ, MAT.doorFrame);
        addBox(DW+0.08, 0.08, T+0.04, openCenter, DH, wallZ, MAT.doorFrame);
      } else {
        // Solid wall
        buildWallSegment(wallCx, wallZ, wallLen, H, T, MAT.wall);
        addCollisionBox(side.sx, wallZ - T/2, side.ex, wallZ + T/2);
      }
    } else {
      // Wall runs along Z
      const wallLen = Math.abs(side.ez - side.sz);
      const wallX = side.sx;
      const wallCz = (side.sz + side.ez) / 2;

      if (opening) {
        const openCenter = wallCz + (opening.center || 0);
        const leftLen = openCenter - DW/2 - side.sz;
        const rightLen = side.ez - (openCenter + DW/2);

        if (leftLen > 0.1) {
          const lz = side.sz + leftLen/2;
          buildWallSegment(wallX, lz, T, H, leftLen, MAT.wall);
          addCollisionBox(wallX - T/2, side.sz, wallX + T/2, side.sz + leftLen);
        }
        if (rightLen > 0.1) {
          const rz = side.ez - rightLen/2;
          buildWallSegment(wallX, rz, T, H, rightLen, MAT.wall);
          addCollisionBox(wallX - T/2, side.ez - rightLen, wallX + T/2, side.ez);
        }
        const lintelH = H - DH;
        if (lintelH > 0.1) {
          buildWallSegment(wallX, openCenter, T, lintelH, DW, MAT.wall);
        }
        // Door frame
        addBox(T+0.04, DH, 0.08, wallX, DH/2, openCenter - DW/2, MAT.doorFrame);
        addBox(T+0.04, DH, 0.08, wallX, DH/2, openCenter + DW/2, MAT.doorFrame);
        addBox(T+0.04, 0.08, DW+0.08, wallX, DH, openCenter, MAT.doorFrame);
      } else {
        buildWallSegment(wallX, wallCz, T, H, wallLen, MAT.wall);
        addCollisionBox(wallX - T/2, side.sz, wallX + T/2, side.ez);
      }
    }
  }

  // Baseboards
  const baseH = 0.12, baseD = 0.03;
  const baseColor = new THREE.MeshStandardMaterial({ color: 0x4a3a2a, roughness: 0.6, metalness: 0.1 });
  // North baseboard
  if (!openings.find(o => o.wall === 'n'))
    addBox(w, baseH, baseD, cx, baseH/2, z2 - baseD/2, baseColor);
  // South baseboard
  if (!openings.find(o => o.wall === 's'))
    addBox(w, baseH, baseD, cx, baseH/2, z1 + baseD/2, baseColor);
  // East baseboard
  if (!openings.find(o => o.wall === 'e'))
    addBox(baseD, baseH, d, x2 - baseD/2, baseH/2, cz, baseColor);
  // West baseboard
  if (!openings.find(o => o.wall === 'w'))
    addBox(baseD, baseH, d, x1 + baseD/2, baseH/2, cz, baseColor);

  // Ceiling light panels
  buildCeilingLights(room);

  // Room sign above doorways (only for main rooms, not corridors)
  if (name.includes('Corridor') === false && name !== 'Central Hub') {
    buildRoomSign(room);
  }
}

function buildCeilingLights(room) {
  const { x1, z1, x2, z2 } = room;
  const w = x2 - x1, d = z2 - z1;
  const cx = (x1+x2)/2, cz = (z1+z2)/2;
  const H = CFG.CEILING_H;

  // Place lights in a grid pattern
  const spacing = 3.5;
  const panelW = 1.2, panelD = 0.4;

  for (let gx = cx - w/2 + spacing/2; gx < cx + w/2; gx += spacing) {
    for (let gz = cz - d/2 + spacing/2; gz < cz + d/2; gz += spacing) {
      // Light panel geometry
      addBox(panelW, 0.04, panelD, gx, H - 0.02, gz, MAT.lightPanel);

      // Recessed housing around it
      addBox(panelW + 0.1, 0.06, panelD + 0.1, gx, H - 0.04, gz, MAT.metal);

      // Actual light source
      const light = new THREE.PointLight(0xfff4e0, 0.6, 8, 1.5);
      light.position.set(gx, H - 0.1, gz);
      light.castShadow = false; // Performance
      scene.add(light);
    }
  }
}

function buildRoomSign(room) {
  // Find the room's entry opening
  const { openings, name, x1, z1, x2, z2 } = room;
  if (!openings || !openings.length) return;

  const opening = openings[0];
  const H = CFG.CEILING_H;
  const cx = (x1+x2)/2, cz = (z1+z2)/2;

  const tex = signTexture(name.toUpperCase(), room.color || '#8a9aa8');
  const signMat = new THREE.MeshStandardMaterial({
    map: tex, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.15,
    roughness: 0.8, metalness: 0.2
  });

  let signX, signZ, rotY;
  switch (opening.wall) {
    case 's': signX = cx; signZ = z1 + 0.2; rotY = 0; break;
    case 'n': signX = cx; signZ = z2 - 0.2; rotY = Math.PI; break;
    case 'w': signX = x1 + 0.2; signZ = cz; rotY = Math.PI/2; break;
    case 'e': signX = x2 - 0.2; signZ = cz; rotY = -Math.PI/2; break;
  }

  const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.0, 0.5), signMat);
  sign.position.set(signX, H - 0.5, signZ);
  sign.rotation.y = rotY;
  scene.add(sign);
}

function buildTerminal(toolId, x, y, z, rotY) {
  const group = new THREE.Group();
  group.position.set(x, y, z);
  group.rotation.y = rotY;

  // Monitor bezel
  const bezelW = 1.1, bezelH = 0.85, bezelD = 0.06;
  const bezel = new THREE.Mesh(new THREE.BoxGeometry(bezelW, bezelH, bezelD), MAT.monitorBezel);
  bezel.castShadow = true;
  group.add(bezel);

  // Screen face
  const screenTex = monitorTexture(toolId);
  const screenMat = new THREE.MeshStandardMaterial({
    map: screenTex, emissive: 0xffffff, emissiveMap: screenTex,
    emissiveIntensity: 0.5, roughness: 0.1, metalness: 0.0,
  });
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.72), screenMat);
  screen.position.z = bezelD/2 + 0.002;
  screen.userData = { toolId, type: 'terminal' };
  group.add(screen);
  interactiveObjects.push(screen);
  monitorMeshes[toolId] = screen;

  // Monitor glow light
  const hex = TOOLS[toolId] ? 0x405060 : 0x303030;
  const glow = new THREE.PointLight(hex, 0.15, 2.5, 2);
  glow.position.z = 0.15;
  group.add(glow);

  // Wall mount bracket
  const bracket = new THREE.Mesh(
    new THREE.BoxGeometry(0.15, 0.15, 0.08),
    MAT.metal
  );
  bracket.position.z = -bezelD/2 - 0.04;
  group.add(bracket);

  scene.add(group);
  return group;
}

function buildDesk(x, z, w, d, rotY = 0) {
  const group = new THREE.Group();
  group.position.set(x, 0, z);
  group.rotation.y = rotY;

  const topH = 0.04, legH = 0.72, topY = legH + topH/2;

  // Desktop surface
  const top = new THREE.Mesh(new THREE.BoxGeometry(w, topH, d), MAT.desk);
  top.position.y = topY;
  top.castShadow = true;
  top.receiveShadow = true;
  group.add(top);

  // Legs
  const legGeo = new THREE.BoxGeometry(0.04, legH, 0.04);
  const offX = w/2 - 0.06, offZ = d/2 - 0.06;
  [[-offX,-offZ],[offX,-offZ],[offX,offZ],[-offX,offZ]].forEach(([lx,lz]) => {
    const leg = new THREE.Mesh(legGeo, MAT.metal);
    leg.position.set(lx, legH/2, lz);
    group.add(leg);
  });

  scene.add(group);

  // Add collision
  const cos = Math.cos(rotY), sin = Math.sin(rotY);
  const halfW = w/2 + 0.1, halfD = d/2 + 0.1;
  // Simplified AABB (ignores rotation for small desks)
  addCollisionBox(x - halfW, z - halfD, x + halfW, z + halfD, 0, topY + topH/2);

  return group;
}

function buildRoomFurniture(room) {
  if (!room.tools || !room.tools.length) return;

  const { x1, z1, x2, z2, tools } = room;
  const cx = (x1+x2)/2, cz = (z1+z2)/2;
  const rw = x2 - x1, rd = z2 - z1;

  // Place terminals along walls
  const monitorY = 1.55; // Eye-level mounted
  const wallOffset = 0.05; // Distance from wall

  // Determine which wall is the "back" (opposite to the opening)
  const opening = room.openings[0];
  let backWall, sideWall1, sideWall2;

  switch (opening.wall) {
    case 's': // Entry from south, back wall is north
      backWall = { axis: 'x', z: z2, dir: Math.PI, xRange: [x1+1.2, x2-1.2] };
      sideWall1 = { axis: 'z', x: x1, dir: Math.PI/2, zRange: [z1+1.5, z2-1] };
      sideWall2 = { axis: 'z', x: x2, dir: -Math.PI/2, zRange: [z1+1.5, z2-1] };
      break;
    case 'n':
      backWall = { axis: 'x', z: z1, dir: 0, xRange: [x1+1.2, x2-1.2] };
      sideWall1 = { axis: 'z', x: x1, dir: Math.PI/2, zRange: [z1+1, z2-1.5] };
      sideWall2 = { axis: 'z', x: x2, dir: -Math.PI/2, zRange: [z1+1, z2-1.5] };
      break;
    case 'w':
      backWall = { axis: 'z', x: x2, dir: -Math.PI/2, zRange: [z1+1.2, z2-1.2] };
      sideWall1 = { axis: 'x', z: z1, dir: 0, xRange: [x1+1.5, x2-1] };
      sideWall2 = { axis: 'x', z: z2, dir: Math.PI, xRange: [x1+1.5, x2-1] };
      break;
    case 'e':
      backWall = { axis: 'z', x: x1, dir: Math.PI/2, zRange: [z1+1.2, z2-1.2] };
      sideWall1 = { axis: 'x', z: z1, dir: 0, xRange: [x1+1, x2-1.5] };
      sideWall2 = { axis: 'x', z: z2, dir: Math.PI, xRange: [x1+1, x2-1.5] };
      break;
  }

  // Distribute terminals
  const walls = [backWall, sideWall1, sideWall2];
  let toolIdx = 0;

  for (const wall of walls) {
    if (toolIdx >= tools.length) break;

    // How many monitors fit on this wall
    let available;
    if (wall.axis === 'x') {
      available = (wall.xRange[1] - wall.xRange[0]);
    } else {
      available = (wall.zRange[1] - wall.zRange[0]);
    }
    const maxOnWall = Math.min(Math.floor(available / 1.6), tools.length - toolIdx, 3);
    if (maxOnWall <= 0) continue;

    for (let i = 0; i < maxOnWall && toolIdx < tools.length; i++, toolIdx++) {
      const t = (i + 0.5) / maxOnWall; // 0..1 evenly distributed

      let mx, mz;
      if (wall.axis === 'x') {
        mx = wall.xRange[0] + t * (wall.xRange[1] - wall.xRange[0]);
        mz = wall.z + (wall.dir === Math.PI ? -wallOffset : wallOffset);
      } else {
        mz = wall.zRange[0] + t * (wall.zRange[1] - wall.zRange[0]);
        mx = wall.x + (wall.dir === -Math.PI/2 ? -wallOffset : wallOffset);
      }

      buildTerminal(tools[toolIdx], mx, monitorY, mz, wall.dir);

      // Desk below each terminal
      const deskOff = 0.6;
      let dx = mx, dz = mz;
      if (wall.axis === 'x') {
        dz += (wall.dir === Math.PI ? -deskOff : deskOff);
      } else {
        dx += (wall.dir === -Math.PI/2 ? -deskOff : deskOff);
      }
      buildDesk(dx, dz, 1.0, 0.6, wall.dir);
    }
  }
}

function buildLighting() {
  // Ambient — very subtle warm fill
  const ambient = new THREE.AmbientLight(0xfff4e0, 0.15);
  scene.add(ambient);

  // Hemisphere — warm sky, cool ground
  const hemi = new THREE.HemisphereLight(0xfff4e0, 0x3a3832, 0.2);
  scene.add(hemi);
}

function buildEnvironmentDetails() {
  // Central Hub — large overhead light fixture
  const hubLight = new THREE.SpotLight(0xfff4e0, 1.5, 12, Math.PI/4, 0.5, 1);
  hubLight.position.set(0, CFG.CEILING_H - 0.1, 0);
  hubLight.target.position.set(0, 0, 0);
  scene.add(hubLight);
  scene.add(hubLight.target);

  // Hub center floor emblem glow
  const emblLight = new THREE.PointLight(0xd4c5a9, 0.1, 5, 2);
  emblLight.position.set(0, 0.1, 0);
  scene.add(emblLight);

  // Directional arrow signs on hub walls
  buildDirectionSign(0, 1.6, 4.3, 0, '↑ AI SYSTEMS', '#8aaab8');
  buildDirectionSign(0, 1.6, -4.3, Math.PI, '↑ SCRIPTS', '#9a88b8');
  buildDirectionSign(4.3, 1.6, 0, -Math.PI/2, '↑ ANALYSIS', '#a89a88');
  buildDirectionSign(-4.3, 1.6, 0, Math.PI/2, '↑ TOOLS', '#88a888');

  // Fire extinguisher in corridor (environmental detail)
  buildFireExtinguisher(-1.3, 0, 6.5);

  // Potted plant in hub corner
  buildPlant(3.5, 0, 3.5);
  buildPlant(-3.5, 0, -3.5);

  // Water cooler
  buildWaterCooler(3.8, 0, -3);

  // Clock on hub wall
  buildWallClock(0, 2.5, -4.4);
}

function buildDirectionSign(x, y, z, rotY, text, color) {
  const tex = makeCanvasTexture(400, 80, (ctx, w, h) => {
    ctx.fillStyle = '#2a2824';
    ctx.fillRect(0,0,w,h);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.strokeRect(2,2,w-4,h-4);
    ctx.font = 'bold 22px Segoe UI, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = color;
    ctx.fillText(text, w/2, h/2);
  });
  const mat = new THREE.MeshStandardMaterial({
    map: tex, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.1,
    roughness: 0.8, metalness: 0.2
  });
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.24), mat);
  sign.position.set(x, y, z);
  sign.rotation.y = rotY;
  scene.add(sign);
}

function buildFireExtinguisher(x, y, z) {
  const group = new THREE.Group();
  group.position.set(x, y, z);
  // Body
  const body = new THREE.Mesh(
    new THREE.CylinderGeometry(0.06, 0.06, 0.35, 8),
    new THREE.MeshStandardMaterial({ color: 0xcc3333, roughness: 0.4, metalness: 0.3 })
  );
  body.position.y = 0.85;
  group.add(body);
  // Top
  const top = new THREE.Mesh(
    new THREE.CylinderGeometry(0.03, 0.06, 0.06, 8),
    new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.3, metalness: 0.6 })
  );
  top.position.y = 1.06;
  group.add(top);
  // Wall bracket
  const bracket = new THREE.Mesh(
    new THREE.BoxGeometry(0.15, 0.04, 0.08),
    MAT.metal
  );
  bracket.position.y = 0.9;
  bracket.position.z = -0.05;
  group.add(bracket);
  scene.add(group);
}

function buildPlant(x, y, z) {
  const group = new THREE.Group();
  group.position.set(x, y, z);
  // Pot
  const pot = new THREE.Mesh(
    new THREE.CylinderGeometry(0.15, 0.12, 0.25, 8),
    new THREE.MeshStandardMaterial({ color: 0x6a5a4a, roughness: 0.7, metalness: 0.1 })
  );
  pot.position.y = 0.125;
  group.add(pot);
  // Foliage (simple sphere cluster)
  const leafMat = new THREE.MeshStandardMaterial({ color: 0x4a7a4a, roughness: 0.8, metalness: 0.0 });
  for (let i = 0; i < 5; i++) {
    const leaf = new THREE.Mesh(new THREE.SphereGeometry(0.08 + Math.random()*0.06, 6, 6), leafMat);
    leaf.position.set((Math.random()-0.5)*0.12, 0.3 + Math.random()*0.15, (Math.random()-0.5)*0.12);
    group.add(leaf);
  }
  scene.add(group);
  addCollisionBox(x-0.2, z-0.2, x+0.2, z+0.2, 0, 0.5);
}

function buildWaterCooler(x, y, z) {
  const group = new THREE.Group();
  group.position.set(x, y, z);
  // Body
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(0.3, 0.9, 0.3),
    new THREE.MeshStandardMaterial({ color: 0xe8e0d8, roughness: 0.5, metalness: 0.2 })
  );
  body.position.y = 0.45;
  group.add(body);
  // Water bottle
  const bottle = new THREE.Mesh(
    new THREE.CylinderGeometry(0.08, 0.1, 0.35, 8),
    new THREE.MeshStandardMaterial({ color: 0x88bbdd, roughness: 0.1, metalness: 0.0, transparent: true, opacity: 0.6 })
  );
  bottle.position.y = 1.1;
  group.add(bottle);
  scene.add(group);
  addCollisionBox(x-0.2, z-0.2, x+0.2, z+0.2, 0, 1.3);
}

function buildWallClock(x, y, z) {
  // Simple clock face
  const tex = makeCanvasTexture(128, 128, (ctx, w, h) => {
    ctx.fillStyle = '#f0ece4';
    ctx.beginPath(); ctx.arc(w/2, h/2, 60, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = '#4a3a2a';
    ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(w/2, h/2, 60, 0, Math.PI*2); ctx.stroke();
    // Hour marks
    for (let i = 0; i < 12; i++) {
      const a = (i/12) * Math.PI * 2 - Math.PI/2;
      ctx.beginPath();
      ctx.moveTo(w/2 + Math.cos(a)*48, h/2 + Math.sin(a)*48);
      ctx.lineTo(w/2 + Math.cos(a)*55, h/2 + Math.sin(a)*55);
      ctx.stroke();
    }
    // Hands (static — shows ~10:10)
    ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(w/2, h/2); ctx.lineTo(w/2-20, h/2-30); ctx.stroke();
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(w/2, h/2); ctx.lineTo(w/2+18, h/2-35); ctx.stroke();
    ctx.fillStyle = '#4a3a2a';
    ctx.beginPath(); ctx.arc(w/2, h/2, 3, 0, Math.PI*2); ctx.fill();
  });
  const mat = new THREE.MeshStandardMaterial({ map: tex, roughness: 0.6, metalness: 0.1 });
  const clock = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.4), mat);
  clock.position.set(x, y, z);
  scene.add(clock);
}

const BRAIN = {
  N_HUMAN  : 8192,   // points for human brain
  N_AI     : 8192,   // points for AI brain
  N_SYNAPSES: 1200,  // synapse arc lines
  N_DUST   : 2000,   // floating particle dust
  SCALE    : 0.62,   // brain radius in world units
  SEPARATION: 1.65,  // horizontal offset from center (each brain)
  HEIGHT   : 2.5,    // y-position of brain center in room
  Z_OFFSET : 14.0,   // z-position in AI Systems Lab
};

const LOBE_COLORS = {
  frontal   : new THREE.Color(0.85, 0.55, 0.30),  // warm orange
  parietal  : new THREE.Color(0.45, 0.75, 0.55),  // mint green
  temporal  : new THREE.Color(0.40, 0.60, 0.90),  // cobalt blue
  occipital : new THREE.Color(0.80, 0.40, 0.75),  // violet
  limbic    : new THREE.Color(0.95, 0.80, 0.30),  // gold
  cerebellum: new THREE.Color(0.60, 0.85, 0.90),  // teal
  brainstem : new THREE.Color(0.70, 0.70, 0.70),  // silver
};

const AI_LAYER_COLORS = [
  new THREE.Color(0.10, 0.60, 1.00),   // deep blue — early layers
  new THREE.Color(0.20, 0.90, 0.80),   // cyan
  new THREE.Color(0.50, 0.30, 1.00),   // purple — mid layers
  new THREE.Color(0.80, 0.20, 0.80),   // magenta
  new THREE.Color(1.00, 0.55, 0.10),   // amber — late layers
];

function generateBrainPositions(N, seed) {
  // Deterministic seeded RNG (xorshift32)
  let s = seed >>> 0 || 0x1234ABCD;
  function rand() {
    s ^= s << 13; s ^= s >> 17; s ^= s << 5;
    return ((s >>> 0) / 0xFFFFFFFF);
  }

  const positions = new Float32Array(N * 3);
  const normals   = new Float32Array(N * 3); // for shading
  const lobes     = new Uint8Array(N);        // lobe id per point

  // Sample points on an anatomical brain surface via rejection sampling
  // on a deformed sphere
  let i = 0;
  let attempts = 0;

  while (i < N && attempts < N * 40) {
    attempts++;

    // Fibonacci sphere for uniform distribution base
    const theta = Math.acos(2.0 * rand() - 1.0);
    const phi   = 2.0 * Math.PI * rand();

    let x = Math.sin(theta) * Math.cos(phi);
    let y = Math.sin(theta) * Math.sin(phi);
    let z = Math.cos(theta);

    // ── BRAIN SHAPE DEFORMATION ──────────────────────────────────────────
    // 1. Overall brain ovoid (wider front-back than left-right)
    x *= 0.82;
    y *= 0.68;
    z *= 1.00;

    // 2. Flatten the bottom (brainstem area, negative y)
    if (y < -0.3) y *= 0.65;

    // 3. Bifurcation — left/right hemispheres (interhemispheric fissure)
    const hemiSign = x > 0 ? 1.0 : -1.0;
    if (Math.abs(x) < 0.08) {
      // Points near midline: clamp or remove most (keep only corpus callosum)
      if (rand() > 0.12) { attempts++; continue; }
    }
    // Push hemispheres apart slightly
    x += hemiSign * 0.04;

    // 4. Gyral folds (sulci & gyri) via multi-octave noise
    const nx = x, ny = y, nz = z;
    let sulcalR = 0.0;

    // Primary sulci (large folds)
    sulcalR += 0.055 * Math.sin(nx * 8.0 + 1.3) * Math.cos(ny * 6.5 + 0.7);
    sulcalR += 0.045 * Math.cos(nz * 7.5 + 2.1) * Math.sin(ny * 5.0 + 1.1);
    sulcalR += 0.038 * Math.sin(nz * 9.0 + ny * 6.0 + 0.5);
    // Secondary sulci
    sulcalR += 0.025 * Math.cos(nx * 15.0 + nz * 12.0 + 0.8);
    sulcalR += 0.020 * Math.sin(ny * 14.0 + nz * 11.0 + 1.6);
    // Tertiary (fine texture)
    sulcalR += 0.012 * Math.cos(nx * 22.0 + ny * 19.0 + 0.3);
    sulcalR += 0.010 * Math.sin(nz * 25.0 + nx * 18.0 + 2.0);

    // Apply sulcal deformation (radial)
    const r0 = Math.sqrt(x*x + y*y + z*z);
    const rDeformed = r0 + sulcalR;
    if (r0 > 1e-6) {
      x = x * rDeformed / r0;
      y = y * rDeformed / r0;
      z = z * rDeformed / r0;
    }

    // 5. Occipital pole — push back & narrow
    if (z < -0.4) { z *= 1.18; x *= 0.78; }

    // 6. Temporal lobes — bulge outward inferior-lateral
    if (y < -0.1 && Math.abs(x) > 0.3) {
      const tStrength = Math.max(0, (-y - 0.1) * (Math.abs(x) - 0.3));
      x += hemiSign * tStrength * 0.5;
      y -= tStrength * 0.3;
    }

    // 7. Frontal pole rounding
    if (z > 0.55) { z *= 0.92; }

    // 8. Scale to BRAIN.SCALE
    x *= BRAIN.SCALE;
    y *= BRAIN.SCALE;
    z *= BRAIN.SCALE;

    // Small jitter for pointcloud density variation
    x += (rand() - 0.5) * 0.008;
    y += (rand() - 0.5) * 0.008;
    z += (rand() - 0.5) * 0.008;

    // ── LOBE CLASSIFICATION ──────────────────────────────────────────────
    let lobe;
    const yn = y / BRAIN.SCALE;
    const zn = z / BRAIN.SCALE;
    const xn_abs = Math.abs(x) / BRAIN.SCALE;

    if (yn < -0.50 && zn < -0.55) {
      lobe = 5; // cerebellum (posterior-inferior)
    } else if (yn < -0.35 && xn_abs < 0.25) {
      lobe = 6; // brainstem (inferior midline)
    } else if (zn > 0.30) {
      lobe = 0; // frontal (anterior z)
    } else if (yn > 0.30 && zn < 0.10 && zn > -0.30) {
      lobe = 1; // parietal (superior mid)
    } else if (yn < -0.05 && xn_abs > 0.30) {
      lobe = 2; // temporal (lateral inferior)
    } else if (zn < -0.25) {
      lobe = 3; // occipital (posterior)
    } else {
      lobe = 4; // limbic / cingulate
    }

    // ── STORE ─────────────────────────────────────────────────────────────
    positions[i*3 + 0] = x;
    positions[i*3 + 1] = y;
    positions[i*3 + 2] = z;

    // Simple normal: radial outward from center
    const len = Math.sqrt(x*x+y*y+z*z)+1e-8;
    normals[i*3+0] = x/len; normals[i*3+1] = y/len; normals[i*3+2] = z/len;
    lobes[i] = lobe;
    i++;
  }

  return { positions, normals, lobes, count: i };
}
buildMaterials();for(const room of ROOMS){buildRoom(room);buildRoomFurniture(room);}buildLighting();buildEnvironmentDetails();
return {rooms:ROOMS,tools:TOOLS,collisionBoxes,interactiveObjects,monitorMeshes,brainPositions:generateBrainPositions,brain:BRAIN};
}
