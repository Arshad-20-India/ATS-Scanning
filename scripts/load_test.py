"""
Load test client for the /analyses/sync endpoint.

Usage:
    python3 scripts/benchmark_server.py &          # start the benchmark server
    python3 scripts/load_test.py                    # run this against it

Reports p50/p95/p99 latency and throughput at a few concurrency
levels, using a real generated DOCX resume and real JD text sent over
real HTTP -- not a synthetic in-process timer. Every number this
script prints is measured, not estimated.
"""

from __future__ import annotations

import io
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import docx
import requests

BASE_URL = "http://127.0.0.1:8010"
JD_TEXT = """Backend Engineer

Required
- Python
- Docker
- 3+ years of experience

Preferred
- Kubernetes
- AWS
"""


def _build_sample_resume() -> bytes:
    document = docx.Document()
    for line in [
        "Jane Smith",
        "jane.smith@example.com | 555-123-4567",
        "",
        "Experience",
        "Backend Engineer, Acme Corp",
        "Jan 2021 - Jun 2023",
        "- Built a scalable REST API serving 10k requests per second",
        "- Reduced database query latency by 40 percent through indexing",
        "",
        "Software Engineer, Beta Inc",
        "Aug 2023 - Present",
        "- Migrated monolith to microservices architecture",
        "",
        "Education",
        "Bachelor of Science in Computer Science",
        "State University",
        "2020",
        "",
        "Skills",
        "Python, JavaScript, Docker, Kubernetes",
        "",
        "Projects",
        "Open Source CLI Tool",
        "A CLI tool for automating deployments",
        "Technologies: Python, Docker",
        "- Adopted by 500 users",
        "",
        "Certifications",
        "AWS Certified Developer - Amazon - 2022",
    ]:
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def _one_request(resume_bytes: bytes) -> tuple[float, int]:
    start = time.perf_counter()
    response = requests.post(
        f"{BASE_URL}/api/v1/analyses/sync",
        files={"resume_file": ("resume.docx", resume_bytes, "application/octet-stream")},
        data={"job_description_text": JD_TEXT},
        timeout=30,
    )
    elapsed = time.perf_counter() - start
    return elapsed, response.status_code


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * p
    f, c = int(k), min(int(k) + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def run_benchmark(n_requests: int, concurrency: int) -> None:
    resume_bytes = _build_sample_resume()
    latencies: list[float] = []
    status_codes: dict[int, int] = {}

    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(_one_request, resume_bytes) for _ in range(n_requests)]
        for future in as_completed(futures):
            elapsed, status = future.result()
            latencies.append(elapsed)
            status_codes[status] = status_codes.get(status, 0) + 1
    wall_elapsed = time.perf_counter() - wall_start

    latencies.sort()
    throughput = n_requests / wall_elapsed

    print(f"\n=== concurrency={concurrency}, n={n_requests} ===")
    print(f"status codes: {status_codes}")
    print(f"wall time: {wall_elapsed:.2f}s | throughput: {throughput:.2f} req/s")
    print(f"latency p50: {_percentile(latencies, 0.50) * 1000:.1f}ms")
    print(f"latency p95: {_percentile(latencies, 0.95) * 1000:.1f}ms")
    print(f"latency p99: {_percentile(latencies, 0.99) * 1000:.1f}ms")
    print(f"latency min/max: {min(latencies) * 1000:.1f}ms / {max(latencies) * 1000:.1f}ms")
    print(f"latency mean/stdev: {statistics.mean(latencies) * 1000:.1f}ms / {statistics.stdev(latencies) * 1000:.1f}ms")


if __name__ == "__main__":
    try:
        requests.get(f"{BASE_URL}/health", timeout=3)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: no server running at {BASE_URL}. Start it first:")
        print("  python3 scripts/benchmark_server.py &")
        raise SystemExit(1)

    for concurrency in (1, 5, 10):
        run_benchmark(n_requests=30, concurrency=concurrency)
