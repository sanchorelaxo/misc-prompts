#!/usr/bin/env python3

import argparse
import datetime as _dt
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, Optional

import requests


API_URL = "https://ytscribe.ai/api/transcripts"


def fetch_transcript(*, youtube_url: str, api_key: str, timeout_s: int = 60) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    resp = requests.post(API_URL, headers=headers, json={"url": youtube_url}, timeout=timeout_s)

    try:
        data = resp.json()
    except Exception:
        data = None

    if not resp.ok:
        detail = ""
        if isinstance(data, dict):
            detail = data.get("error") or data.get("message") or str(data)
        raise RuntimeError(f"HTTP {resp.status_code} from ytscribe: {detail or resp.text}")

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected response from ytscribe (not JSON object).")

    return data


def _extract_transcript_text(data: Dict[str, Any]) -> Optional[str]:
    candidates: list[Any] = []

    if isinstance(data.get("transcript"), str):
        return data.get("transcript")

    if isinstance(data.get("transcript"), list):
        candidates.append(data.get("transcript"))

    if isinstance(data.get("segments"), list):
        candidates.append(data.get("segments"))

    if isinstance(data.get("data"), dict):
        inner = data.get("data")
        if isinstance(inner.get("transcript"), str):
            return inner.get("transcript")
        if isinstance(inner.get("transcript"), list):
            candidates.append(inner.get("transcript"))
        if isinstance(inner.get("segments"), list):
            candidates.append(inner.get("segments"))

    for segs in candidates:
        parts: list[str] = []
        for seg in segs:
            if isinstance(seg, dict) and isinstance(seg.get("text"), str):
                t = seg.get("text").strip()
                if t:
                    parts.append(t)
        joined = "\n".join(parts).strip()
        if joined:
            return joined

    return None


def _get_video_title(data: Dict[str, Any]) -> Optional[str]:
    meta = data.get("metadata")
    if isinstance(meta, dict):
        video = meta.get("video")
        if isinstance(video, dict) and isinstance(video.get("title"), str):
            t = video.get("title").strip()
            return t or None

    inner = data.get("data")
    if isinstance(inner, dict):
        meta2 = inner.get("metadata")
        if isinstance(meta2, dict):
            video2 = meta2.get("video")
            if isinstance(video2, dict) and isinstance(video2.get("title"), str):
                t = video2.get("title").strip()
                return t or None

    return None


def _slugify_filename(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^a-z0-9._-]+", "", s)
    s = re.sub(r"-+", "-", s).strip("-._")
    return s or "transcript"


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch YouTube transcript via ytscribe.ai")
    p.add_argument("--url", required=True, help="YouTube URL")
    p.add_argument(
        "--api-key",
        default=os.environ.get("YTSCRIBE_API_KEY"),
        help="YTScribe API key (or set YTSCRIBE_API_KEY env var)",
    )
    p.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds")
    p.add_argument(
        "--out-dir",
        default=".",
        help="Directory to write transcript file into (default: current directory)",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Do not print the output file path",
    )
    p.add_argument(
        "--raw-json",
        action="store_true",
        help="Print full JSON response instead of transcript field",
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

    if not args.api_key:
        print("Missing API key. Pass --api-key or set YTSCRIBE_API_KEY.", file=sys.stderr)
        return 2

    try:
        data = fetch_transcript(youtube_url=args.url, api_key=args.api_key, timeout_s=args.timeout)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.raw_json:
        print(data)
        return 0

    transcript = _extract_transcript_text(data)
    if not transcript:
        print("No transcript content found in response.", file=sys.stderr)
        return 1

    title = _get_video_title(data) or args.url
    base = _slugify_filename(title)
    ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{base}_{ts}.txt"

    out_path.write_text(transcript, encoding="utf-8")

    if not args.quiet:
        print(str(out_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
