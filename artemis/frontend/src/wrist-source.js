import * as THREE from 'three';
export function createWrist(scene,camera){let pipboy=null;
function initPipBoy() {
  const group = new THREE.Group();
  group.name = 'pipboy_arm';

  // Skin / sleeve / device materials
  const skinMat   = new THREE.MeshStandardMaterial({ color: 0xc9a884, roughness: 0.85 });
  const sleeveMat = new THREE.MeshStandardMaterial({ color: 0x2a3220, roughness: 0.95 });
  const pipMat    = new THREE.MeshStandardMaterial({ color: 0x3b4a2a, roughness: 0.7,  metalness: 0.25 });
  const knobMat   = new THREE.MeshStandardMaterial({ color: 0x7a6a4a, roughness: 0.4,  metalness: 0.6  });
  const screenMat = new THREE.MeshBasicMaterial({ color: 0x1eff5a });

  // Upper sleeve (rolled-up jumpsuit)
  const sleeve = new THREE.Mesh(new THREE.CylinderGeometry(0.062, 0.072, 0.30, 16), sleeveMat);
  sleeve.position.y = 0.25;
  group.add(sleeve);

  // Forearm — cylinder going from elbow toward wrist (group local +Y is toward shoulder)
  const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.054, 0.064, 0.38, 16), skinMat);
  forearm.position.y = -0.05;
  group.add(forearm);

  // Hand
  const hand = new THREE.Mesh(new THREE.BoxGeometry(0.10, 0.14, 0.06), skinMat);
  hand.position.y = -0.31;
  group.add(hand);

  // Pip-Boy body on inside of wrist (faces +Z so it points at camera when raised)
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.18, 0.13), pipMat);
  body.position.set(0, -0.10, 0.07);
  group.add(body);

  // Side knobs (3 dials on left edge)
  for (let i = 0; i < 3; i++) {
    const k = new THREE.Mesh(new THREE.CylinderGeometry(0.013, 0.013, 0.022, 12), knobMat);
    k.rotation.z = Math.PI / 2;
    k.position.set(-0.11, -0.15 + i * 0.05, 0.07);
    group.add(k);
  }

  // Antenna stub
  const ant = new THREE.Mesh(new THREE.CylinderGeometry(0.005, 0.005, 0.10, 8), knobMat);
  ant.position.set(0.09, -0.03, 0.07);
  ant.rotation.x = -0.35;
  group.add(ant);

  // Glowing screen face
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(0.13, 0.10), screenMat);
  screen.position.set(0, -0.09, 0.136);
  group.add(screen);

  // Soft green glow light
  const sLight = new THREE.PointLight(0x1eff5a, 0.55, 0.6);
  sLight.position.set(0, -0.09, 0.20);
  group.add(sLight);

  // Attach to camera so it follows the view
  camera.add(group);
  scene.add(camera); // ensure camera is in scene graph for camera-children to render

  pipboy = {
    group,
    screen,
    t: 0,
    target: 0,
    // Lowered: down at the player's left side, mostly out of frame
    posLow:  new THREE.Vector3(-0.45, -0.95, -0.25),
    rotLow:  new THREE.Euler(-1.55, 0.20, 0.10),
    // Raised: across the chest, screen tilted toward camera
    posHigh: new THREE.Vector3(-0.18, -0.22, -0.45),
    rotHigh: new THREE.Euler(-0.25, 0.55, 0.15),
  };
  group.position.copy(pipboy.posLow);
  group.rotation.copy(pipboy.rotLow);
}

function updatePipBoy(delta) {
  if (!pipboy) return;
  if (pipboy.t === pipboy.target) return;
  const speed = 3.0;
  const dir = pipboy.target > pipboy.t ? 1 : -1;
  pipboy.t = Math.max(0, Math.min(1, pipboy.t + dir * speed * delta));
  // ease-in-out cubic
  const x = pipboy.t;
  const e = x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  pipboy.group.position.lerpVectors(pipboy.posLow, pipboy.posHigh, e);
  pipboy.group.rotation.x = pipboy.rotLow.x + (pipboy.rotHigh.x - pipboy.rotLow.x) * e;
  pipboy.group.rotation.y = pipboy.rotLow.y + (pipboy.rotHigh.y - pipboy.rotLow.y) * e;
  pipboy.group.rotation.z = pipboy.rotLow.z + (pipboy.rotHigh.z - pipboy.rotLow.z) * e;
  // Reveal/hide UI when fully at end of travel


}


initPipBoy();return {update:(dt,open)=>{pipboy.target=open?1:0;updatePipBoy(dt);}};
}
