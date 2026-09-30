// Geometry/texture functions from pinned command-center/dashboard_3d.html.
import * as THREE from "three";
function galMakeStarTex(size) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(size/2, size/2, 0, size/2, size/2, size/2);
  g.addColorStop(0.0, 'rgba(255,255,255,0.9)');
  g.addColorStop(0.08,'rgba(255,255,255,0.6)');
  g.addColorStop(0.25,'rgba(200,220,255,0.15)');
  g.addColorStop(0.5, 'rgba(100,140,255,0.03)');
  g.addColorStop(1.0, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(c); tex.needsUpdate = true;
  return tex;
}

function galRemapToSpiral(files) {
  const n = files.length;
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity, minZ = Infinity, maxZ = -Infinity;
  for (const f of files) {
    if (f.x < minX) minX = f.x; if (f.x > maxX) maxX = f.x;
    if (f.y < minY) minY = f.y; if (f.y > maxY) maxY = f.y;
    if (f.z < minZ) minZ = f.z; if (f.z > maxZ) maxZ = f.z;
  }
  const rangeX = maxX - minX || 1;
  const rangeY = maxY - minY || 1;
  const rangeZ = maxZ - minZ || 1;
  const ARMS = 4, ARM_SEP = (2 * Math.PI) / ARMS;
  const WIND = 0.15, DISK_R = 65, DISK_H = 4;
  const positions = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const f = files[i];
    const nx = (f.x - minX) / rangeX;
    const ny = (f.y - minY) / rangeY;
    const nz = (f.z - minZ) / rangeZ;
    const cx = nx - 0.5, cz = nz - 0.5;
    const dist = Math.sqrt(cx*cx + cz*cz) * 2;
    const angle = Math.atan2(cz, cx);
    const armIdx = Math.round((angle / ARM_SEP) % ARMS);
    const armBase = armIdx * ARM_SEP;
    const spiralAngle = armBase + dist * WIND * 20 + (angle - armBase) * 0.3;
    const r = Math.pow(dist, 0.8) * DISK_R;
    const yScale = Math.exp(-dist * 2) * DISK_H;
    const yPos = (ny - 0.5) * yScale;
    positions[i*3]   = Math.cos(spiralAngle) * r;
    positions[i*3+1] = yPos;
    positions[i*3+2] = Math.sin(spiralAngle) * r;
  }
  return positions;
}

// ── Nebulae (drifting dust clouds) ─────────────────────
export { galMakeStarTex, galRemapToSpiral };
