"""ARTEMIS Video Generation — HeyGen Avatar 6 / Kling class (video: AI video).

Providers: kling, heygen avatar, command, placeholder. 8K preset.
generate_video tool (approval-gated, media category). /api/media/video/* endpoints.
"""
from __future__ import annotations

import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VideoJob:
    id: str
    ts: float
    prompt: str
    provider: str
    preset: str
    width: int
    height: int
    duration_s: int
    status: str  # queued|rendering|done|failed
    video_url: str | None = None
    avatar_id: str | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


PRESETS = {
    "8k": {"width": 7680, "height": 4320},
    "4k": {"width": 3840, "height": 2160},
    "1080p": {"width": 1920, "height": 1080},
}

HEYGEN_AVATARS = [
    "avatar-01", "avatar-02", "avatar-03", "avatar-04", "avatar-05",
    "avatar-06", "avatar-07", "avatar-08",
]


class VideoGenerationService:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.output_dir = data_dir / "media" / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.jobs: dict[str, VideoJob] = {}
        self.provider = "placeholder"  # kling | heygen | command | placeholder
        self.base_url = ""
        self.api_key = ""

    def generate(self, prompt: str, preset: str = "1080p",
                 provider: str | None = None, avatar_id: str | None = None,
                 width: int | None = None, height: int | None = None,
                 duration_s: int = 5) -> VideoJob:
        p = PRESETS.get(preset, PRESETS["1080p"])
        w = width or p["width"]
        h = height or p["height"]
        prov = provider or self.provider
        job = VideoJob(
            id=uuid.uuid4().hex, ts=time.time(), prompt=prompt,
            provider=prov, preset=preset, width=w, height=h,
            duration_s=duration_s, status="queued", avatar_id=avatar_id,
        )
        with self._lock:
            self.jobs[job.id] = job
        self._run(job)
        return job

    def _run(self, job: VideoJob):
        job.status = "rendering"
        try:
            if job.provider == "heygen":
                result = self._heygen(job)
            elif job.provider == "kling":
                result = self._kling(job)
            elif job.provider == "command":
                result = self._command(job)
            else:
                result = self._placeholder(job)
            job.status = "done"
            job.video_url = result["video_url"]
            job.metadata = result.get("metadata", {})
        except Exception as exc:  # noqa: BLE001
            job.status = "failed"
            job.error = str(exc)[:500]

    def _placeholder(self, job: VideoJob) -> dict:
        # Placeholder: write a tiny valid MP4-like stub + metadata manifest.
        path = self.output_dir / f"{job.id}.mp4"
        path.write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42")
        manifest = {
            "id": job.id, "prompt": job.prompt, "provider": job.provider,
            "preset": job.preset, "size": [job.width, job.height],
            "duration_s": job.duration_s, "avatar": job.avatar_id,
            "placeholder": True,
        }
        (self.output_dir / f"{job.id}.json").write_text(
            __import__("json").dumps(manifest, indent=2))
        return {"video_url": f"/media/videos/{job.id}.mp4",
                "metadata": {"placeholder": True, "size": [job.width, job.height],
                             "duration_s": job.duration_s}}

    def _heygen(self, job: VideoJob) -> dict:
        if not self.base_url:
            return self._placeholder(job)
        import httpx
        headers = {"Authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        payload = {
            "video_input": [{"character": job.avatar_id or "avatar-01",
                             "voice_text": job.prompt}],
            "dimension": {"width": job.width, "height": job.height},
        }
        with httpx.Client(timeout=120) as c:
            r = c.post(f"{self.base_url.rstrip('/')}/v1/video/generate",
                       headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return {"video_url": data.get("video_url", ""),
                    "metadata": {"provider": "heygen", "avatar": job.avatar_id,
                                 "size": [job.width, job.height]}}

    def _kling(self, job: VideoJob) -> dict:
        if not self.base_url:
            return self._placeholder(job)
        import httpx
        with httpx.Client(timeout=120) as c:
            r = c.post(f"{self.base_url.rstrip('/')}/v1/videos/generations",
                       headers={"Authorization": f"Bearer {self.api_key}",
                                "Content-Type": "application/json"},
                       json={"prompt": job.prompt, "width": job.width,
                             "height": job.height, "duration": job.duration_s,
                             "model": "kling-video"})
            r.raise_for_status()
            data = r.json()
            return {"video_url": data.get("data", [{}])[0].get("url", ""),
                    "metadata": {"provider": "kling", "size": [job.width, job.height]}}

    def _command(self, job: VideoJob) -> dict:
        return self._placeholder(job)

    def get(self, job_id: str) -> VideoJob | None:
        return self.jobs.get(job_id)

    def configure(self, provider: str | None = None,
                  base_url: str | None = None, api_key: str | None = None):
        if provider:
            self.provider = provider
        if base_url is not None:
            self.base_url = base_url
        if api_key is not None:
            self.api_key = api_key
        return {"provider": self.provider, "base_url": self.base_url,
                "api_key_set": bool(self.api_key)}

    def status(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "base_url": self.base_url,
            "presets": PRESETS,
            "avatars": HEYGEN_AVATARS,
            "jobs": len(self.jobs),
            "output_dir": str(self.output_dir),
        }

    def close(self):
        pass
