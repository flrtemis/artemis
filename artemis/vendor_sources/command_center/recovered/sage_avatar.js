/**
 * sage_avatar.js — Sage's photoreal 3D body.
 *
 * Loads the avatar GLB and drives it live:
 *
 *   • Lip sync   — amplitude + viseme timeline → jaw/mouth morph weights
 *   • Expressions — emotion/PAD state → ARKit blendshape weights
 *   • Eyes        — eyeBlinkLeft/Right, eyeLookIn/Out/Up/Down morphs
 *   • Head        — spring-damped idle yaw/pitch/roll, listening lean, nods
 *   • Body        — breathing via spine bone scale, weight-shift sway
 *   • Lighting    — key/fill/rim PointLights parented to avatar group
 *   • Chat UI     — floating panel wired to /ws/sage-avatar WebSocket
 *
 * GLB load order (first success wins):
 *   1. /assets/sage_fallback.glb    — local offline fallback
 *   2. models.readyplayer.me primary RPM URL
 *   3. models.readyplayer.me fallback RPM URL
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// ─────────────────────────────────────────────────────────────────────────────
//  Constants
// ─────────────────────────────────────────────────────────────────────────────

const LOCAL_FALLBACK  = '/assets/sage_fallback.glb';

/**
 * Ready Player Me avatar ID.
 * This is a publicly documented female demo avatar — brown hair, warm skin.
 * Appending ?morphTargets=ARKit,Oculus Visemes gives 52+15 blend shapes.
 * The browser fetches this; no server-side proxy required.
 */
const RPM_AVATAR_ID   = '64bfa15f0e72c63d7c3934a6'; // female, medium skin, dark hair
const RPM_AVATAR_URL  = `https://models.readyplayer.me/${RPM_AVATAR_ID}.glb` +
  `?morphTargets=ARKit,Oculus%20Visemes` +
  `&textureAtlas=1024` +
  `&lod=0`;

// Fallback: a second known-good female avatar
const RPM_FALLBACK_ID = '638df693d72bffc6fa17943c';
const RPM_FALLBACK    = `https://models.readyplayer.me/${RPM_FALLBACK_ID}.glb` +
  `?morphTargets=ARKit,Oculus%20Visemes&textureAtlas=1024`;

// ─────────────────────────────────────────────────────────────────────────────
//  Utility
// ─────────────────────────────────────────────────────────────────────────────

function lerp(a, b, t)          { return a + (b - a) * t; }
function clamp(v, lo, hi)       { return Math.max(lo, Math.min(hi, v)); }
function smoothstep(t)          { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }

/** Critically-damped spring. Returns [newValue, newVelocity]. */
function spring(val, vel, target, stiffness, damping, dt) {
  const f    = (target - val) * stiffness - vel * damping;
  const nVel = vel + f * dt;
  const nVal = val + nVel * dt;
  return [nVal, nVel];
}

/** Find a Three.js SkinnedMesh inside a loaded GLTF scene by name fragment. */
function findMesh(root, nameFrag) {
  let found = null;
  root.traverse(o => {
    if (!found && o.isMesh && o.name.toLowerCase().includes(nameFrag.toLowerCase()))
      found = o;
  });
  return found;
}

/** Find a mesh with morph targets (blend shapes). */
function findMorphMesh(root, nameFrag) {
  let found = null;
  root.traverse(o => {
    if (!found && o.isMesh && o.morphTargetDictionary &&
        Object.keys(o.morphTargetDictionary).length > 0 &&
        o.name.toLowerCase().includes(nameFrag.toLowerCase()))
      found = o;
  });
  return found;
}

/** Find any mesh with morph targets. */
function findAnyMorphMesh(root) {
  let best = null;
  let bestCount = 0;
  root.traverse(o => {
    if (o.isMesh && o.morphTargetDictionary) {
      const n = Object.keys(o.morphTargetDictionary).length;
      if (n > bestCount) { best = o; bestCount = n; }
    }
  });
  return best;
}

/** Set a morph target by name, safely. */
function setMorph(mesh, name, value) {
  if (!mesh || !mesh.morphTargetDictionary || !mesh.morphTargetInfluences) return;
  const idx = mesh.morphTargetDictionary[name];
  if (idx !== undefined) mesh.morphTargetInfluences[idx] = clamp(value, 0, 1);
}

/** Get current morph value by name. */
function getMorph(mesh, name) {
  if (!mesh || !mesh.morphTargetDictionary || !mesh.morphTargetInfluences) return 0;
  const idx = mesh.morphTargetDictionary[name];
  return idx !== undefined ? mesh.morphTargetInfluences[idx] : 0;
}

/** Lerp a morph target toward a target. */
function lerpMorph(mesh, name, target, t) {
  const cur = getMorph(mesh, name);
  setMorph(mesh, name, lerp(cur, target, t));
}

// ─────────────────────────────────────────────────────────────────────────────
//  ARKit morph target names (Ready Player Me includes all of these)
// ─────────────────────────────────────────────────────────────────────────────

const ARKIT = {
  // Eyes
  eyeBlinkLeft:      'eyeBlinkLeft',
  eyeBlinkRight:     'eyeBlinkRight',
  eyeWideLeft:       'eyeWideLeft',
  eyeWideRight:      'eyeWideRight',
  eyeSquintLeft:     'eyeSquintLeft',
  eyeSquintRight:    'eyeSquintRight',
  eyeLookUpLeft:     'eyeLookUpLeft',
  eyeLookUpRight:    'eyeLookUpRight',
  eyeLookDownLeft:   'eyeLookDownLeft',
  eyeLookDownRight:  'eyeLookDownRight',
  eyeLookInLeft:     'eyeLookInLeft',
  eyeLookInRight:    'eyeLookInRight',
  eyeLookOutLeft:    'eyeLookOutLeft',
  eyeLookOutRight:   'eyeLookOutRight',
  // Brows
  browInnerUp:       'browInnerUp',
  browOuterUpLeft:   'browOuterUpLeft',
  browOuterUpRight:  'browOuterUpRight',
  browDownLeft:      'browDownLeft',
  browDownRight:     'browDownRight',
  // Cheeks
  cheekPuff:         'cheekPuff',
  cheekSquintLeft:   'cheekSquintLeft',
  cheekSquintRight:  'cheekSquintRight',
  // Jaw
  jawOpen:           'jawOpen',
  jawLeft:           'jawLeft',
  jawRight:          'jawRight',
  jawForward:        'jawForward',
  // Mouth
  mouthClose:        'mouthClose',
  mouthFunnel:       'mouthFunnel',
  mouthPucker:       'mouthPucker',
  mouthLeft:         'mouthLeft',
  mouthRight:        'mouthRight',
  mouthSmileLeft:    'mouthSmileLeft',
  mouthSmileRight:   'mouthSmileRight',
  mouthFrownLeft:    'mouthFrownLeft',
  mouthFrownRight:   'mouthFrownRight',
  mouthDimpleLeft:   'mouthDimpleLeft',
  mouthDimpleRight:  'mouthDimpleRight',
  mouthStretchLeft:  'mouthStretchLeft',
  mouthStretchRight: 'mouthStretchRight',
  mouthRollLower:    'mouthRollLower',
  mouthRollUpper:    'mouthRollUpper',
  mouthShrugLower:   'mouthShrugLower',
  mouthShrugUpper:   'mouthShrugUpper',
  mouthPressLeft:    'mouthPressLeft',
  mouthPressRight:   'mouthPressRight',
  mouthLowerDownLeft:'mouthLowerDownLeft',
  mouthLowerDownRight:'mouthLowerDownRight',
  mouthUpperUpLeft:  'mouthUpperUpLeft',
  mouthUpperUpRight: 'mouthUpperUpRight',
  // Nose
  noseSneerLeft:     'noseSneerLeft',
  noseSneerRight:    'noseSneerRight',
  // Tongue
  tongueOut:         'tongueOut',
};

// Oculus Viseme names (RPM)
const VISEME = {
  sil:  'viseme_sil',
  PP:   'viseme_PP',
  FF:   'viseme_FF',
  TH:   'viseme_TH',
  DD:   'viseme_DD',
  kk:   'viseme_kk',
  CH:   'viseme_CH',
  SS:   'viseme_SS',
  nn:   'viseme_nn',
  RR:   'viseme_RR',
  aa:   'viseme_aa',
  E:    'viseme_E',
  ih:   'viseme_ih',
  oh:   'viseme_oh',
  ou:   'viseme_ou',
};

// ─────────────────────────────────────────────────────────────────────────────
//  Emotion → ARKit blend shape targets
// ─────────────────────────────────────────────────────────────────────────────

const EMOTION_ARKIT = {
  neutral: {
    browInnerUp: 0, browOuterUpLeft: 0, browOuterUpRight: 0,
    browDownLeft: 0, browDownRight: 0,
    mouthSmileLeft: 0, mouthSmileRight: 0,
    mouthFrownLeft: 0, mouthFrownRight: 0,
    cheekSquintLeft: 0, cheekSquintRight: 0,
    eyeSquintLeft: 0, eyeSquintRight: 0,
    eyeWideLeft: 0, eyeWideRight: 0,
    noseSneerLeft: 0, noseSneerRight: 0,
  },
  happy: {
    browInnerUp: 0.1, browOuterUpLeft: 0.1, browOuterUpRight: 0.1,
    browDownLeft: 0, browDownRight: 0,
    mouthSmileLeft: 0.7, mouthSmileRight: 0.7,
    mouthFrownLeft: 0, mouthFrownRight: 0,
    cheekSquintLeft: 0.5, cheekSquintRight: 0.5,
    eyeSquintLeft: 0.3, eyeSquintRight: 0.3,
    eyeWideLeft: 0, eyeWideRight: 0,
    noseSneerLeft: 0, noseSneerRight: 0,
  },
  joy: {
    browInnerUp: 0.15, browOuterUpLeft: 0.2, browOuterUpRight: 0.2,
    browDownLeft: 0, browDownRight: 0,
    mouthSmileLeft: 0.95, mouthSmileRight: 0.95,
    mouthFrownLeft: 0, mouthFrownRight: 0,
    cheekSquintLeft: 0.7, cheekSquintRight: 0.7,
    eyeSquintLeft: 0.5, eyeSquintRight: 0.5,
    eyeWideLeft: 0, eyeWideRight: 0,
    noseSneerLeft: 0, noseSneerRight: 0,
  },
  content: {
    browInnerUp: 0.05, browOuterUpLeft: 0.05, browOuterUpRight: 0.05,
    browDownLeft: 0, browDownRight: 0,
    mouthSmileLeft: 0.35, mouthSmileRight: 0.35,
    mouthFrownLeft: 0, mouthFrownRight: 0,
    cheekSquintLeft: 0.2, cheekSquintRight: 0.2,
    eyeSquintLeft: 0.1, eyeSquintRight: 0.1,
    eyeWideLeft: 0, eyeWideRight: 0,
    noseSneerLeft: 0, noseSneerRight: 0,
  },
  sad: {
    browInnerUp: 0.6, browOuterUpLeft: 0, browOuterUpRight: 0,
    browDownLeft: 0.3, browDownRight: 0.3,
    mouthSmileLeft: 0, mouthSmileRight: 0,
    mouthFrownLeft: 0.6, mouthFrownRight: 0.6,
    cheekSquintLeft: 0, cheekSquintRight: 0,
    eyeSquintLeft: 0.2, eyeSquintRight: 0.2,
    eyeWideLeft: 0, eyeWideRight: 0,
    noseSneerLeft: 0, noseSneerRight: 0,
  },
  anger: {
    browInnerUp: 0, browOuterUpLeft: 0, browOuterUpRight: 0,
    browDownLeft: 0.8, browDownRight: 0.8,
    mouthSmileLeft: 0, mouthSmileRight: 0,
    mouthFrownLeft: 0.4, mouthFrownRight: 0.4,
    cheekSquintLeft: 0.3, cheekSquintRight: 0.3,
    eyeSquintLeft: 0.6, eyeSquintRight: 0.6,
    eyeWideLeft: 0, eyeWideRight: 0,
    noseSneerLeft: 0.4, noseSneerRight: 0.4,
  },
  fear: {
    browInnerUp: 0.8, browOuterUpLeft: 0.5, browOuterUpRight: 0.5,
    browDownLeft: 0, browDownRight: 0,
    mouthSmileLeft: 0, mouthSmileRight: 0,
    mouthFrownLeft: 0.3, mouthFrownRight: 0.3,
    cheekSquintLeft: 0, cheekSquintRight: 0,
    eyeSquintLeft: 0, eyeSquintRight: 0,
    eyeWideLeft: 0.7, eyeWideRight: 0.7,
    noseSneerLeft: 0, noseSneerRight: 0,
  },
  surprise: {
    browInnerUp: 0.9, browOuterUpLeft: 0.9, browOuterUpRight: 0.9,
    browDownLeft: 0, browDownRight: 0,
    mouthSmileLeft: 0.1, mouthSmileRight: 0.1,
    mouthFrownLeft: 0, mouthFrownRight: 0,
    cheekSquintLeft: 0, cheekSquintRight: 0,
    eyeSquintLeft: 0, eyeSquintRight: 0,
    eyeWideLeft: 0.9, eyeWideRight: 0.9,
    noseSneerLeft: 0, noseSneerRight: 0,
  },
};

// ─────────────────────────────────────────────────────────────────────────────
//  SageLipSync — drives jawOpen + Oculus Viseme morphs from server timeline
// ─────────────────────────────────────────────────────────────────────────────

class SageLipSync {
  constructor() {
    this.timeline  = [];
    this.startTime = 0;
    this.active    = false;
    this._curAmp   = 0;
    this._curVis   = 'sil';
    this._ampVel   = 0;
    // Track previous viseme for smooth crossfade
    this._prevVis  = 'sil';
    this._blendT   = 0;
  }

  load(visemes, audioStartSec) {
    this.timeline  = visemes || [];
    this.startTime = audioStartSec;
    this.active    = true;
    this._curVis   = 'sil';
    this._prevVis  = 'sil';
    this._blendT   = 0;
  }

  stop() {
    this.active  = false;
    this._curAmp = 0;
  }

  /** Call each frame. Returns {amp, viseme}. */
  tick(dt) {
    if (!this.active || !this.timeline.length) {
      this._curAmp = lerp(this._curAmp, 0, clamp(dt * 10, 0, 1));
      return { amp: this._curAmp, viseme: 'sil' };
    }

    const elapsed = performance.now() / 1000 - this.startTime;

    // Current frame
    let frame = this.timeline[0];
    for (const f of this.timeline) {
      if (f.t <= elapsed) frame = f;
      else break;
    }

    // Smooth amplitude with spring
    const [nAmp, nVel] = spring(this._curAmp, this._ampVel, frame.amp, 80, 12, dt);
    this._curAmp  = clamp(nAmp, 0, 1);
    this._ampVel  = nVel;

    if (frame.viseme !== this._curVis) {
      this._prevVis = this._curVis;
      this._curVis  = frame.viseme;
      this._blendT  = 0;
    }
    this._blendT = clamp(this._blendT + dt * 18, 0, 1); // fast crossfade

    const last = this.timeline[this.timeline.length - 1];
    if (elapsed > last.t + 0.5) this.active = false;

    return { amp: this._curAmp, viseme: this._curVis, prevVis: this._prevVis, blendT: this._blendT };
  }

  /** Apply to RPM head mesh morph targets. */
  apply(headMesh, teethMesh, { amp, viseme, prevVis, blendT = 1 }) {
    if (!headMesh) return;

    // Jaw open (primary amplitude driver)
    lerpMorph(headMesh, ARKIT.jawOpen,  amp * 0.65, 0.3);
    if (teethMesh) lerpMorph(teethMesh, ARKIT.jawOpen, amp * 0.65, 0.3);

    // Viseme cross-fade: fade out previous, fade in current
    const allVisemes = Object.values(VISEME);
    const curKey  = VISEME[viseme]  || VISEME.sil;
    const prevKey = VISEME[prevVis] || VISEME.sil;

    for (const vKey of allVisemes) {
      let target = 0;
      if (vKey === curKey)  target = amp * blendT;
      if (vKey === prevKey) target = amp * (1 - blendT);
      lerpMorph(headMesh, vKey, target, 0.25);
      if (teethMesh) lerpMorph(teethMesh, vKey, target, 0.25);
    }

    // Mouth stretch on louder phonemes
    const stretchAmt = amp > 0.5 ? (amp - 0.5) * 0.4 : 0;
    lerpMorph(headMesh, ARKIT.mouthStretchLeft,  stretchAmt, 0.2);
    lerpMorph(headMesh, ARKIT.mouthStretchRight, stretchAmt, 0.2);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
//  SageFacialFX — maps emotion to ARKit blend shape weights
// ─────────────────────────────────────────────────────────────────────────────

class SageFacialFX {
  constructor() {
    this._emotion = 'neutral';
    this._current = Object.fromEntries(
      Object.keys(EMOTION_ARKIT.neutral).map(k => [k, 0])
    );
    this._vel = Object.fromEntries(
      Object.keys(EMOTION_ARKIT.neutral).map(k => [k, 0])
    );
  }

  setEmotion(e) {
    if (EMOTION_ARKIT[e]) this._emotion = e;
    else this._emotion = 'neutral';
  }

  /** Update springs and write to mesh. */
  apply(headMesh, teethMesh, dt, isListening) {
    const target = EMOTION_ARKIT[this._emotion] || EMOTION_ARKIT.neutral;

    for (const k of Object.keys(this._current)) {
      let t = target[k] || 0;
      // Subtle attentive brow raise while listening
      if (isListening && k === 'browInnerUp') t = Math.max(t, 0.12);

      const [nv, nVel] = spring(this._current[k], this._vel[k], t, 6, 3.5, dt);
      this._current[k] = nv;
      this._vel[k]     = nVel;

      if (headMesh) lerpMorph(headMesh, ARKIT[k] || k, this._current[k], 1);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
//  SageEyes — blink, saccade, gaze via ARKit morph targets
// ─────────────────────────────────────────────────────────────────────────────

class SageEyes {
  constructor() {
    // Blink
    this._blinkL    = 0; this._blinkR = 0;
    this._blinkTimer = 0;
    this._nextBlink  = this._rndBlink();
    this._closing    = false;
    this._openTimer  = 0;

    // Gaze
    this._gazeH = 0; this._gazeHVel = 0;  // horizontal
    this._gazeV = 0; this._gazeVVel = 0;  // vertical
    this._gazeTargH = 0;
    this._gazeTargV = 0;

    // Saccade
    this._saccTimer = 0;
    this._saccIntvl = 1.5 + Math.random() * 2.5;

    this.listening = false;
    this.speaking  = false;
  }

  _rndBlink() { return 2.8 + Math.random() * 5.5; }

  setGazeTarget(h, v) { this._gazeTargH = h; this._gazeTargV = v; }

  tick(headMesh, dt) {
    if (!headMesh) return;

    // ── Blink ────────────────────────────────────────────────────────────────
    this._blinkTimer += dt;
    if (!this._closing && this._blinkTimer >= this._nextBlink) {
      this._closing   = true;
      this._blinkTimer = 0;
      this._nextBlink  = this._rndBlink() * (this.speaking ? 0.65 : 1);
      this._openTimer  = 0;
    }

    const CLOSE_SPEED = 14;
    const OPEN_SPEED  = 9;

    if (this._closing) {
      this._blinkL = clamp(this._blinkL + dt * CLOSE_SPEED, 0, 1);
      this._blinkR = clamp(this._blinkR + dt * CLOSE_SPEED * (0.95 + Math.random() * 0.1), 0, 1);
      if (this._blinkL >= 1) {
        this._closing   = false;
        this._openTimer = 0;
      }
    } else {
      this._openTimer += dt;
      if (this._openTimer > 0.04) { // tiny hold at closed
        this._blinkL = clamp(this._blinkL - dt * OPEN_SPEED, 0, 1);
        this._blinkR = clamp(this._blinkR - dt * OPEN_SPEED, 0, 1);
      }
    }

    setMorph(headMesh, ARKIT.eyeBlinkLeft,  this._blinkL);
    setMorph(headMesh, ARKIT.eyeBlinkRight, this._blinkR);

    // ── Saccades ─────────────────────────────────────────────────────────────
    this._saccTimer += dt;
    if (this._saccTimer >= this._saccIntvl) {
      this._saccTimer = 0;
      this._saccIntvl = 1.2 + Math.random() * 3;
      const mag = this.listening ? 0.03 : 0.08;
      this._gazeTargH = (Math.random() - 0.5) * mag;
      this._gazeTargV = (Math.random() - 0.5) * mag * 0.5;
    }

    // ── Gaze spring ──────────────────────────────────────────────────────────
    const [gH, gHv] = spring(this._gazeH, this._gazeHVel, this._gazeTargH, 14, 6, dt);
    const [gV, gVv] = spring(this._gazeV, this._gazeVVel, this._gazeTargV, 14, 6, dt);
    this._gazeH = gH; this._gazeHVel = gHv;
    this._gazeV = gV; this._gazeVVel = gVv;

    // Map gaze to ARKit morph targets
    const h = clamp(this._gazeH, -0.15, 0.15);
    const v = clamp(this._gazeV, -0.1, 0.1);

    // Horizontal
    setMorph(headMesh, ARKIT.eyeLookInLeft,   Math.max(0, -h));
    setMorph(headMesh, ARKIT.eyeLookOutLeft,  Math.max(0,  h));
    setMorph(headMesh, ARKIT.eyeLookInRight,  Math.max(0,  h));
    setMorph(headMesh, ARKIT.eyeLookOutRight, Math.max(0, -h));

    // Vertical
    setMorph(headMesh, ARKIT.eyeLookUpLeft,    Math.max(0, -v));
    setMorph(headMesh, ARKIT.eyeLookUpRight,   Math.max(0, -v));
    setMorph(headMesh, ARKIT.eyeLookDownLeft,  Math.max(0,  v));
    setMorph(headMesh, ARKIT.eyeLookDownRight, Math.max(0,  v));
  }
}

// ─────────────────────────────────────────────────────────────────────────────
//  SageIdleMotion — bone-driven breathing, sway, head idle
// ─────────────────────────────────────────────────────────────────────────────

class SageIdleMotion {
  constructor() {
    this._t = Math.random() * 1000;

    // Head rotation spring state
    this._headYaw   = 0; this._headYawVel   = 0;
    this._headPitch = 0; this._headPitchVel = 0;
    this._headRoll  = 0; this._headRollVel  = 0;

    // Body sway spring
    this._swayX = 0; this._swayXVel = 0;
    this._swayZ = 0; this._swayZVel = 0;

    // Weight shift
    this._weightTarget = 0.5;
    this._weightVal    = 0.5;
    this._weightVel    = 0;
    this._weightTimer  = 0;

    // Nod
    this._nodPhase  = 0;
    this._nodActive = false;

    // Breathing
    this._breathPhase = 0;

    this.listening = false;
    this.speaking  = false;
  }

  triggerNod() { this._nodActive = true; this._nodPhase = 0; }

  /** Returns {breathY, swayX} for use by parent. */
  tick(dt, bones) {
    this._t += dt;

    // ── Breathing ────────────────────────────────────────────────────────────
    this._breathPhase += dt * 0.24; // ~one breath per 4.2s
    const breathSin = Math.sin(this._breathPhase * Math.PI * 2);
    const breathY   = breathSin * 0.006;   // spine rise
    const breathS   = 1 + breathSin * 0.009; // chest scale

    if (bones.spine) {
      bones.spine.scale.y = breathS;
      bones.spine.position.y = (bones.spineBaseY || 0) + breathY;
    }

    // ── Weight shift ─────────────────────────────────────────────────────────
    this._weightTimer += dt;
    if (this._weightTimer > 5 + Math.random() * 9) {
      this._weightTimer  = 0;
      this._weightTarget = 0.25 + Math.random() * 0.5;
    }
    const [wv, wVel] = spring(this._weightVal, this._weightVel, this._weightTarget, 0.4, 1.2, dt);
    this._weightVal = wv; this._weightVel = wVel;
    const sway = (this._weightVal - 0.5) * 0.022;

    if (bones.hips) bones.hips.position.x = sway;

    // ── Arms rest pose + subtle sway ──────────────────────────────────────────
    // T-pose has arms at ~90° out. Bring them down to a natural rest (~65° from vertical)
    // then layer micro-sway on top for life-like idle motion.
    const armRestZ = 1.1;  // radians inward from T-pose (~63° down from horizontal)
    const shoulderSway = Math.sin(this._t * 0.11) * 0.018;
    if (bones.upperArmL) bones.upperArmL.rotation.z =  armRestZ + shoulderSway;
    if (bones.upperArmR) bones.upperArmR.rotation.z = -armRestZ - shoulderSway;

    // Forearms: slight bend at elbow for natural resting pose
    const elbowBend = 0.25; // ~14° bend
    if (bones.foreArmL) bones.foreArmL.rotation.z =  elbowBend;
    if (bones.foreArmR) bones.foreArmR.rotation.z = -elbowBend;

    // ── Head idle ─────────────────────────────────────────────────────────────
    const n = (f, p) => Math.sin(this._t * f + p);
    const targetYaw   = n(0.12, 1.3) * 0.05 + (this.listening ? sway * 0.4 : 0);
    const targetPitch = n(0.09, 2.8) * 0.035 + (this.listening ? 0.05 : -0.015);
    const targetRoll  = sway * 0.35 + n(0.08, 0.6) * 0.012;

    const stiff = this.speaking ? 8 : 3.5;
    const damp  = this.speaking ? 5 : 2.8;

    const [hY, hYv]   = spring(this._headYaw,   this._headYawVel,   targetYaw,   stiff, damp, dt);
    const [hP, hPv]   = spring(this._headPitch, this._headPitchVel, targetPitch, stiff, damp, dt);
    const [hR, hRv]   = spring(this._headRoll,  this._headRollVel,  targetRoll,  stiff, damp, dt);

    this._headYaw   = hY; this._headYawVel   = hYv;
    this._headPitch = hP; this._headPitchVel = hPv;
    this._headRoll  = hR; this._headRollVel  = hRv;

    // ── Nod ───────────────────────────────────────────────────────────────────
    let nodExtra = 0;
    if (this._nodActive) {
      this._nodPhase += dt * 3.5;
      nodExtra = Math.sin(this._nodPhase * Math.PI) * 0.09;
      if (this._nodPhase >= 2) this._nodActive = false;
    }

    if (bones.head) {
      bones.head.rotation.y = this._headYaw;
      bones.head.rotation.x = this._headPitch + nodExtra;
      bones.head.rotation.z = this._headRoll;
    } else if (bones.neck) {
      bones.neck.rotation.y = this._headYaw;
      bones.neck.rotation.x = this._headPitch + nodExtra;
      bones.neck.rotation.z = this._headRoll;
    }

    // Listening lean — slightly forward head + neck
    if (this.listening && bones.neck) {
      bones.neck.rotation.x = lerp(bones.neck.rotation.x, 0.06, dt * 2);
    }

    return { breathY, sway };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
//  SageChatUI — floating panel wired to /ws/sage-avatar
// ─────────────────────────────────────────────────────────────────────────────

class SageChatUI {
  constructor(onSend, onMic) {
    this.onSend = onSend;
    this.onMic  = onMic;

    this._panel     = null;
    this._log       = null;
    this._input     = null;
    this._micBtn    = null;
    this._statusEl  = null;
    this._visible   = false;
    this._recording = false;
    this._recorder  = null;
    this._chunks    = [];

    this._build();
  }

  _build() {
    // ── Styles ───────────────────────────────────────────────────────────────
    const style = document.createElement('style');
    style.textContent = `
      #sage-panel {
        position: fixed;
        bottom: 28px;
        left: 50%;
        transform: translateX(-50%);
        width: 500px;
        max-width: 95vw;
        background: rgba(14,12,10,0.96);
        border: 1px solid rgba(212,197,169,0.16);
        border-radius: 8px;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: 0 12px 48px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.03);
        display: none;
        flex-direction: column;
        z-index: 600;
        font-family: 'Segoe UI', system-ui, sans-serif;
        overflow: hidden;
      }
      #sage-panel.open { display: flex; }
      #sage-panel-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 11px 16px;
        border-bottom: 1px solid rgba(212,197,169,0.07);
      }
      #sage-panel-name {
        font-size: 0.78rem;
        font-weight: 600;
        color: #d4c5a9;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        flex: 1;
      }
      #sage-panel-status {
        font-size: 0.65rem;
        color: #6a9a6a;
        letter-spacing: 0.08em;
        transition: color 0.3s;
      }
      #sage-panel-status.busy { color: #c4a070; }
      #sage-panel-status.speaking { color: #a070c4; }
      #sage-panel-close {
        background: none;
        border: none;
        color: #6a6058;
        cursor: pointer;
        font-size: 1rem;
        line-height: 1;
        padding: 2px 6px;
        border-radius: 3px;
        transition: color 0.2s;
      }
      #sage-panel-close:hover { color: #d4c5a9; }
      #sage-log {
        flex: 1;
        overflow-y: auto;
        padding: 12px 14px;
        max-height: 240px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        scrollbar-width: thin;
        scrollbar-color: rgba(212,197,169,0.1) transparent;
      }
      .sage-msg {
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        line-height: 1.5;
        max-width: 88%;
        word-break: break-word;
      }
      .sage-msg.user {
        align-self: flex-end;
        background: rgba(196,160,112,0.1);
        border: 1px solid rgba(196,160,112,0.18);
        color: #d4c5a9;
      }
      .sage-msg.sage {
        align-self: flex-start;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        color: #b8a88a;
      }
      #sage-input-row {
        display: flex;
        gap: 8px;
        padding: 10px 14px;
        border-top: 1px solid rgba(212,197,169,0.07);
      }
      #sage-input {
        flex: 1;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(212,197,169,0.1);
        border-radius: 5px;
        color: #d4c5a9;
        font-size: 0.82rem;
        font-family: inherit;
        padding: 8px 12px;
        outline: none;
        transition: border-color 0.2s;
      }
      #sage-input:focus { border-color: rgba(212,197,169,0.35); }
      #sage-input::placeholder { color: rgba(212,197,169,0.3); }
      .sage-btn {
        padding: 8px 14px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(212,197,169,0.12);
        border-radius: 5px;
        color: #a09080;
        font-family: inherit;
        font-size: 0.82rem;
        cursor: pointer;
        transition: all 0.2s;
        white-space: nowrap;
      }
      .sage-btn:hover { background: rgba(255,255,255,0.08); color: #d4c5a9; }
      .sage-btn.active { background: rgba(180,60,60,0.2); border-color: rgba(180,60,60,0.4); color: #e08080; }
      #sage-name-badge {
        position: fixed;
        z-index: 601;
        pointer-events: none;
        display: none;
        flex-direction: column;
        align-items: center;
        gap: 4px;
      }
      #sage-name-badge.visible { display: flex; }
      #sage-name-badge .snb-name {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #d4c5a9;
        text-shadow: 0 1px 8px rgba(0,0,0,0.9);
      }
      #sage-name-badge .snb-sub {
        font-size: 0.58rem;
        color: #8a7e6a;
        letter-spacing: 0.1em;
      }
      #sage-state-ring {
        position: fixed;
        pointer-events: none;
        z-index: 599;
        border-radius: 50%;
        transition: opacity 0.4s;
        display: none;
      }
    `;
    document.head.appendChild(style);

    // ── Panel ─────────────────────────────────────────────────────────────────
    const panel = document.createElement('div');
    panel.id = 'sage-panel';

    const header = document.createElement('div');
    header.id = 'sage-panel-header';

    const name = document.createElement('div');
    name.id = 'sage-panel-name';
    name.textContent = 'Sage';

    this._statusEl = document.createElement('div');
    this._statusEl.id = 'sage-panel-status';
    this._statusEl.textContent = 'ready';

    const closeBtn = document.createElement('button');
    closeBtn.id = 'sage-panel-close';
    closeBtn.textContent = '✕';
    closeBtn.onclick = () => this.hide();

    header.appendChild(name);
    header.appendChild(this._statusEl);
    header.appendChild(closeBtn);

    const log = document.createElement('div');
    log.id = 'sage-log';
    this._log = log;

    const inputRow = document.createElement('div');
    inputRow.id = 'sage-input-row';

    const input = document.createElement('input');
    input.id = 'sage-input';
    input.type = 'text';
    input.placeholder = 'Talk to Sage…';
    input.autocomplete = 'off';

    input.addEventListener('keydown', e => {
      e.stopPropagation();
      if (e.key === 'Enter' && input.value.trim()) {
        this.onSend(input.value.trim());
        input.value = '';
      }
    });
    input.addEventListener('focus',  () => { window.__sage_typing = true; });
    input.addEventListener('blur',   () => { window.__sage_typing = false; });
    this._input = input;

    const sendBtn = document.createElement('button');
    sendBtn.className = 'sage-btn';
    sendBtn.textContent = 'Send';
    sendBtn.onclick = () => {
      if (input.value.trim()) { this.onSend(input.value.trim()); input.value = ''; }
    };

    const micBtn = document.createElement('button');
    micBtn.className = 'sage-btn';
    micBtn.id = 'sage-mic-btn';
    micBtn.textContent = '🎙 Hold';
    micBtn.title = 'Hold to speak — release to send';
    micBtn.addEventListener('mousedown',  () => this._startRec());
    micBtn.addEventListener('mouseup',    () => this._stopRec());
    micBtn.addEventListener('mouseleave', () => { if (this._recording) this._stopRec(); });
    micBtn.addEventListener('touchstart', e => { e.preventDefault(); this._startRec(); }, { passive: false });
    micBtn.addEventListener('touchend',   e => { e.preventDefault(); this._stopRec(); });
    this._micBtn = micBtn;

    inputRow.appendChild(input);
    inputRow.appendChild(sendBtn);
    inputRow.appendChild(micBtn);

    panel.appendChild(header);
    panel.appendChild(log);
    panel.appendChild(inputRow);
    document.body.appendChild(panel);
    this._panel = panel;

    // Close on Escape
    document.addEventListener('keydown', e => {
      if (this._visible && e.code === 'Escape') {
        this.hide();
      }
    });
  }

  show() {
    this._panel.classList.add('open');
    this._visible = true;
    setTimeout(() => this._input?.focus(), 60);
  }

  hide() {
    this._stopRec();
    this._panel.classList.remove('open');
    this._visible = false;
    window.__sage_typing = false;
  }

  toggle() { this._visible ? this.hide() : this.show(); }
  isVisible() { return this._visible; }

  setStatus(text, cls = '') {
    if (!this._statusEl) return;
    this._statusEl.textContent = text;
    this._statusEl.className = 'sage-panel-status' + (cls ? ` ${cls}` : '');
  }

  addMessage(role, text) {
    const el = document.createElement('div');
    el.className = `sage-msg ${role === 'user' ? 'user' : 'sage'}`;
    el.textContent = text;
    this._log.appendChild(el);
    this._log.scrollTop = this._log.scrollHeight;
  }

  // ── Mic ───────────────────────────────────────────────────────────────────

  async _startRec() {
    if (this._recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this._chunks  = [];
      this._recorder = new MediaRecorder(stream);
      this._recorder.ondataavailable = e => { if (e.data.size > 0) this._chunks.push(e.data); };
      this._recorder.onstop = async () => {
        const blob = new Blob(this._chunks, { type: 'audio/webm' });
        const ab   = await blob.arrayBuffer();
        this.onMic(new Uint8Array(ab));
        stream.getTracks().forEach(t => t.stop());
      };
      this._recorder.start();
      this._recording = true;
      if (this._micBtn) this._micBtn.classList.add('active');
    } catch (e) {
      console.warn('[Sage] Mic error:', e);
    }
  }

  _stopRec() {
    if (!this._recording || !this._recorder) return;
    this._recorder.stop();
    this._recording = false;
    if (this._micBtn) this._micBtn.classList.remove('active');
  }
}

// ─────────────────────────────────────────────────────────────────────────────
//  SageAvatar — the whole thing
// ─────────────────────────────────────────────────────────────────────────────

export class SageAvatar {
  /**
   * @param {THREE.Scene}  scene
   * @param {THREE.Camera} camera
   * @param {object}       opts
   * @param {THREE.Vector3} opts.position  — where to place her
   * @param {number}        opts.rotationY — y rotation in radians
   */
  constructor(scene, camera, opts = {}) {
    this.scene  = scene;
    this.camera = camera;

    // Root group
    this.group = new THREE.Group();
    this.group.name = 'SageAvatar';
    this.group.position.copy(opts.position || new THREE.Vector3(0, 0, 0));
    this.group.rotation.y = opts.rotationY ?? 0;
    scene.add(this.group);

    // Sub-systems (instantiated before GLB loads so they accept state changes)
    this.lipSync   = new SageLipSync();
    this.facialFX  = new SageFacialFX();
    this.eyes      = new SageEyes();
    this.idle      = new SageIdleMotion();

    // State
    this._state    = 'idle'; // idle | listening | speaking | thinking
    this._emotion  = 'neutral';
    this._bones    = {};     // named bone references extracted from GLB
    this._headMesh = null;   // mesh with ARKit morphs (Wolf3D_Head)
    this._teethMesh= null;   // mesh with tooth morphs
    this._loaded   = false;

    // Audio
    this._audioCtx = null;
    this._audioQueue = [];
    this._audioPlaying = false;

    // WebSocket
    this._ws    = null;
    this._wsUrl = `${location.origin.replace(/^http/, 'ws')}/ws/sage-avatar`;

    // UI
    this._ui = new SageChatUI(
      text => this._sendText(text),
      buf  => this._sendAudio(buf),
    );

    // Lighting
    this._addLighting();

    // Name badge (world-space label above head)
    this._badge = null;
    this._buildBadge();

    // Loading placeholder
    this._placeholder = this._buildPlaceholder();
    this.group.add(this._placeholder);

    // Load GLB
    this._loadAvatar();

    // Connect WS
    this._connect();
  }

  // ── Lighting ─────────────────────────────────────────────────────────────

  _addLighting() {
    // Key — warm from upper-front
    const key = new THREE.PointLight(0xFFE8CC, 2.2, 4);
    key.position.set(0.4, 2.2, 1.0);
    this.group.add(key);

    // Fill — cool blue-grey from left
    const fill = new THREE.PointLight(0xCCDDFF, 0.7, 4);
    fill.position.set(-1.2, 1.8, 0.5);
    this.group.add(fill);

    // Rim — warm from behind
    const rim = new THREE.PointLight(0xFFDDCC, 1.1, 3);
    rim.position.set(0, 2.0, -1.2);
    this.group.add(rim);

    // Bounce — subtle from floor
    const bounce = new THREE.PointLight(0xFFE8A0, 0.3, 3);
    bounce.position.set(0, 0.1, 0.6);
    this.group.add(bounce);
  }

  // ── Name badge ────────────────────────────────────────────────────────────

  _buildBadge() {
    const badge = document.createElement('div');
    badge.id = 'sage-name-badge';
    badge.innerHTML = `
      <div class="snb-name">Sage</div>
      <div class="snb-sub">ARTEMIS · AI Entity</div>
    `;
    document.body.appendChild(badge);
    this._badge = badge;
  }

  _updateBadge() {
    if (!this._badge || !this.camera) return;
    // Project head position to screen
    const headPos = new THREE.Vector3(0, 2.05, 0);
    headPos.applyMatrix4(this.group.matrixWorld);
    const projected = headPos.clone().project(this.camera);
    if (projected.z > 1) { this._badge.classList.remove('visible'); return; }

    const x = (projected.x * 0.5 + 0.5) * window.innerWidth;
    const y = (1 - (projected.y * 0.5 + 0.5)) * window.innerHeight;

    // Only show if within reasonable distance
    const dist = this.group.position.distanceTo(this.camera.position);
    if (dist > 5) { this._badge.classList.remove('visible'); return; }

    this._badge.style.left = `${x}px`;
    this._badge.style.top  = `${y - 20}px`;
    this._badge.style.transform = 'translateX(-50%)';
    this._badge.classList.add('visible');
  }

  // ── Loading placeholder ───────────────────────────────────────────────────

  _buildPlaceholder() {
    const g = new THREE.Group();
    g.name = 'SagePlaceholder';

    // Glowing orb while loading
    const geo = new THREE.SphereGeometry(0.12, 32, 24);
    const mat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(0xC4A070),
      transparent: true,
      opacity: 0.6,
    });
    const orb = new THREE.Mesh(geo, mat);
    orb.position.y = 1.6;
    g.add(orb);

    // Pulsing ring
    const ringGeo = new THREE.RingGeometry(0.18, 0.22, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xC4A070,
      transparent: true,
      opacity: 0.25,
      side: THREE.DoubleSide,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.02;
    g.add(ring);

    this._placeholderOrb  = orb;
    this._placeholderRing = ring;
    this._placeholderMat  = mat;
    this._placeholderRingMat = ringMat;

    return g;
  }

  _animatePlaceholder(t) {
    if (!this._placeholder.visible) return;
    const pulse = Math.sin(t * 2.4) * 0.5 + 0.5;
    if (this._placeholderMat) this._placeholderMat.opacity = 0.3 + pulse * 0.4;
    if (this._placeholderOrb) this._placeholderOrb.position.y = 1.6 + Math.sin(t * 1.8) * 0.04;
    if (this._placeholderRingMat) this._placeholderRingMat.opacity = 0.1 + pulse * 0.2;
    if (this._placeholderRing) {
      this._placeholderRing.rotation.y = t * 0.5;
    }
  }

  // ── GLB loading ──────────────────────────────────────────────────────────

  _loadAvatar() {
    const loader = new GLTFLoader();
    const urls   = [LOCAL_FALLBACK, RPM_AVATAR_URL, RPM_FALLBACK];
    let   attempt = 0;

    const tryLoad = () => {
      const url = urls[attempt];
      if (!url) {
        console.error('[Sage] All avatar URLs failed — check sage_fallback.glb');
        this._ui.setStatus('avatar load failed', 'busy');
        return;
      }

      const label = attempt === 0 ? 'local fallback' : `rpm ${attempt}`;
      console.log(`[Sage] Loading avatar (${label}):`, url);
      this._ui.setStatus(attempt === 0 ? 'loading local avatar…' : 'loading avatar…', 'busy');

      loader.load(
        url,
        (gltf) => this._onAvatarLoaded(gltf),
        (xhr)  => {
          const pct = Math.round(xhr.loaded / (xhr.total || 1) * 100);
          this._ui.setStatus(`loading ${pct}%…`, 'busy');
        },
        (err) => {
          console.warn(`[Sage] Avatar load attempt ${attempt + 1} failed:`, err);
          attempt++;
          tryLoad();
        },
      );
    };

    tryLoad();
  }

  _onAvatarLoaded(gltf) {
    const model = gltf.scene;
    model.name  = 'SageModel';

    // Scale to human height (~1.75m in local units)
    // RPM avatars are typically ~1.8m, adjust as needed
    model.scale.setScalar(1.0);
    model.position.y = 0;

    // Enable shadows on all meshes + improve material quality
    model.traverse(o => {
      if (o.isMesh) {
        o.castShadow    = true;
        o.receiveShadow = true;

        if (o.material) {
          const mats = Array.isArray(o.material) ? o.material : [o.material];
          mats.forEach(m => {
            if (m.isMeshStandardMaterial) {
              m.envMapIntensity = 0.5;
              // Boost skin material quality
              if (m.name && m.name.toLowerCase().includes('skin')) {
                m.roughness = 0.65;
                m.metalness = 0.0;
              }
            }
          });
        }
      }
    });

    // ── Extract key meshes ─────────────────────────────────────────────────
    // RPM names: Wolf3D_Head, Wolf3D_Teeth, Wolf3D_Body, Wolf3D_Hair, etc.
    this._headMesh  = findMorphMesh(model, 'head') ||
                      findMorphMesh(model, 'Head') ||
                      findAnyMorphMesh(model);
    this._teethMesh = findMorphMesh(model, 'teeth') ||
                      findMorphMesh(model, 'Teeth');

    // Log what we have for debugging
    if (this._headMesh) {
      console.log('[Sage] Head mesh:', this._headMesh.name);
      console.log('[Sage] Morph targets:', Object.keys(this._headMesh.morphTargetDictionary || {}));
    }

    // ── Extract bones ─────────────────────────────────────────────────────
    model.traverse(o => {
      if (!o.isBone && !o.isSkinnedMesh) {
        // RPM uses Object3D nodes as bones
      }
      // Standard humanoid bone names (RPM uses Mixamo rig naming)
      const n = o.name.toLowerCase();
      if (n === 'hips'       || n === 'mixamorigHips')      { this._bones.hips = o; }
      if (n === 'spine'      || n === 'mixamorigSpine')     { this._bones.spine = o; if (!this._bones.spineBaseY) this._bones.spineBaseY = o.position.y; }
      if (n === 'spine1'     || n === 'mixamorigSpine1')    { this._bones.spine1 = o; }
      if (n === 'spine2'     || n === 'mixamorigSpine2')    { this._bones.spine2 = o; }
      if (n === 'neck'       || n === 'mixamorigNeck')      { this._bones.neck = o; }
      if (n === 'head'       || n === 'mixamorigHead')      { this._bones.head = o; }
      if (n === 'leftarm'    || n === 'mixamorigleftarm'    || n === 'leftupperarm' || n.includes('leftarm'))   { this._bones.upperArmL = o; }
      if (n === 'rightarm'   || n === 'mixamorigrightarm'   || n === 'rightupperarm'|| n.includes('rightarm'))  { this._bones.upperArmR = o; }
      if (n === 'leftforearm'  || n === 'mixamorigleftforearm'  || n.includes('leftforearm'))  { this._bones.foreArmL = o; }
      if (n === 'rightforearm' || n === 'mixamorigrightforearm' || n.includes('rightforearm')) { this._bones.foreArmR = o; }
    });

    console.log('[Sage] Bones found:', Object.keys(this._bones));

    // ── Add to scene ──────────────────────────────────────────────────────
    this.group.add(model);
    this._model = model;

    // Hide placeholder
    this._placeholder.visible = false;
    this._loaded = true;
    this._ui.setStatus('ready');

    console.log('[Sage] Avatar ready.');
  }

  // ── WebSocket ─────────────────────────────────────────────────────────────

  _connect() {
    try {
      this._ws = new WebSocket(this._wsUrl);
      this._ws.onopen = () => {
        this._ws.send(JSON.stringify({ type: 'config' }));
      };
      this._ws.onmessage = e => this._onMsg(JSON.parse(e.data));
      this._ws.onclose   = () => setTimeout(() => this._connect(), 3000);
      this._ws.onerror   = () => {};
    } catch (_) {}
  }

  _onMsg(msg) {
    switch (msg.type) {
      case 'status':
        this._ui.setStatus(msg.text || '', msg.text === 'ready' ? '' : 'busy');
        break;
      case 'transcript':
        this._ui.addMessage(msg.role, msg.text);
        break;
      case 'sage_audio':
        this._queueAudio(msg);
        break;
      case 'sage_state':
        if (msg.emotion) this._setEmotion(msg.emotion);
        if (msg.speaking) this._setState('speaking');
        else if (msg.listening) this._setState('listening');
        else this._setState('idle');
        break;
      case 'error':
        this._ui.setStatus(`⚠ ${msg.text}`, 'busy');
        break;
    }
  }

  _sendText(text) {
    if (!this._ws || this._ws.readyState !== WebSocket.OPEN) {
      this._ui.addMessage('assistant', '[offline demo] Backend disconnected; running local lip-sync preview.');
      this._speakDemo(text);
      return;
    }
    this._ws.send(JSON.stringify({ type: 'text', text }));
    this._setState('thinking');
    this._ui.setStatus('thinking…', 'busy');
  }

  _sendAudio(buf) {
    if (!this._ws || this._ws.readyState !== WebSocket.OPEN) return;
    const b64 = btoa(String.fromCharCode(...buf));
    this._ws.send(JSON.stringify({ type: 'audio', data: b64 }));
    this._setState('thinking');
  }

  // ── State machine ─────────────────────────────────────────────────────────

  _setState(s) {
    this._state = s;
    this.idle.listening = (s === 'listening');
    this.idle.speaking  = (s === 'speaking');
    this.eyes.listening = (s === 'listening');
    this.eyes.speaking  = (s === 'speaking');
  }

  _setEmotion(e) {
    this._emotion = e;
    this.facialFX.setEmotion(e);
    // Trigger a nod on positive emotions while speaking
    if (['happy', 'joy', 'content'].includes(e) && this._state === 'speaking') {
      this.idle.triggerNod();
    }
  }

  _speakDemo(text) {
    const words = Math.max(1, String(text || '').trim().split(/\s+/).length);
    const duration = clamp(words * 0.26, 1.2, 7.0);
    const steps = Math.max(16, Math.floor(duration / 0.06));
    const visChoices = ['PP', 'FF', 'TH', 'DD', 'kk', 'CH', 'SS', 'nn', 'RR', 'aa', 'E'];
    const timeline = [];

    for (let i = 0; i < steps; i++) {
      const t = i * (duration / steps);
      const voiced = (i % 6 !== 0);
      timeline.push({
        t,
        amp: voiced ? (0.35 + Math.random() * 0.55) : (0.05 + Math.random() * 0.08),
        viseme: voiced ? visChoices[i % visChoices.length] : 'sil',
      });
    }

    this._setState('speaking');
    this._setEmotion('content');
    this.lipSync.load(timeline, performance.now() / 1000);
    this._ui.setStatus('speaking…', 'speaking');

    setTimeout(() => {
      this.lipSync.stop();
      this._setState('idle');
      this._ui.setStatus('ready');
    }, Math.round((duration + 0.15) * 1000));
  }

  // ── Audio playback + viseme sync ─────────────────────────────────────────

  _queueAudio(msg) {
    this._audioQueue.push(msg);
    if (!this._audioPlaying) this._playNext();
  }

  async _playNext() {
    if (!this._audioQueue.length) { this._audioPlaying = false; return; }
    this._audioPlaying = true;
    const msg = this._audioQueue.shift();

    const binary = atob(msg.audio_b64);
    const buf    = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) buf[i] = binary.charCodeAt(i);

    if (!this._audioCtx) {
      this._audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (this._audioCtx.state === 'suspended') await this._audioCtx.resume();

    try {
      const decoded = await this._audioCtx.decodeAudioData(buf.buffer.slice());
      const src     = this._audioCtx.createBufferSource();
      src.buffer    = decoded;

      // Route through scene master gain if available
      const dest = window.__artemis_master_gain || this._audioCtx.destination;
      src.connect(dest);

      const startSec = this._audioCtx.currentTime;
      src.start(startSec);

      // Sync visemes to audio clock
      this._setState('speaking');
      this._setEmotion(msg.emotion || 'neutral');
      this.lipSync.load(msg.visemes || [], performance.now() / 1000);
      this._ui.setStatus('speaking…', 'speaking');

      src.onended = () => {
        this.lipSync.stop();
        this._setState('idle');
        this._ui.setStatus('ready');
        this._playNext();
      };
    } catch (err) {
      console.warn('[Sage] Audio decode error:', err);
      this._audioPlaying = false;
      this._setState('idle');
    }
  }

  // ── Public API ────────────────────────────────────────────────────────────

  openChat()   { this._ui.show(); }
  closeChat()  { this._ui.hide(); }
  toggleChat() { this._ui.toggle(); }
  isChatOpen() { return this._ui.isVisible(); }
  isLoaded()   { return this._loaded; }

  setPosition(x, y, z) { this.group.position.set(x, y, z); }
  setRotationY(r)       { this.group.rotation.y = r; }

  /** Set gaze target in world space (e.g. camera position). */
  setGazeWorldPos(worldPos) {
    if (!this._bones.head && !this._bones.neck) return;
    const local = worldPos.clone().sub(this.group.position);
    local.normalize();
    const yaw   = Math.atan2(local.x, local.z) * 0.25;
    const pitch = -Math.asin(clamp(local.y - 1.55, -1, 1)) * 0.18;
    this.eyes.setGazeTarget(yaw, pitch);
  }

  // ── Per-frame update ──────────────────────────────────────────────────────

  update(dt, clock) {
    const t = clock ? clock.getElapsedTime() : performance.now() / 1000;

    if (!this._loaded) {
      this._animatePlaceholder(t);
      return;
    }

    // ── Gaze tracks camera ────────────────────────────────────────────────
    if (this.camera) this.setGazeWorldPos(this.camera.position);

    // ── Lip sync ─────────────────────────────────────────────────────────
    const lipData = this.lipSync.tick(dt);
    this.lipSync.apply(this._headMesh, this._teethMesh, lipData);

    // ── Facial expression ─────────────────────────────────────────────────
    this.facialFX.apply(this._headMesh, this._teethMesh, dt, this._state === 'listening');

    // ── Eyes ─────────────────────────────────────────────────────────────
    this.eyes.tick(this._headMesh, dt);

    // ── Idle / body motion ────────────────────────────────────────────────
    this.idle.tick(dt, this._bones);

    // ── Name badge ────────────────────────────────────────────────────────
    this._updateBadge();
  }

  /** Clean up when removing Sage from the scene. */
  dispose() {
    this.scene.remove(this.group);
    if (this._ws) this._ws.close();
    if (this._badge) this._badge.remove();
    const panel = document.getElementById('sage-panel');
    if (panel) panel.remove();
    window.__sage_typing = false;
  }
}
