# Ambiguity-Labs-Project-Tracker

A real-time monitoring and task tracking dashboard for benchmark task submissions and reviews across Snorkel AI / Starfish projects.

## Features

- **Multi-Project Support**: Seamlessly switch between projects:
  - `CDG_Starfish_Pilot_uTYAV_Coding_V3` (Task Reviewing & QC pipeline)
  - `CDG_Starfish_Pilot_uTYAV_Coding` (Benchmark Task Authoring)
  - `[Asimov - General] Workflows Assessment`
- **Live Status Tracking**: Displays real-time assignment states (`OFFERED`, `IN_PROGRESS`, `ACCEPTED`, `REVIEW_PENDING`, `EVALUATION_PENDING`, `NEEDS_REVISION`).
- **Direct Feedback Inspection**: One-click modal to view reviewer notes, accept notes, rebuttal notes, and prior QC / audit feedback without needing command-line tools.
- **Search & Filter Controls**: Quickly filter by state or search by task name and submission UUID.
- **Fast Lightweight Backend**: Python-based HTTP server with caching and direct integration with `snorkelai-stb`.

## Quick Start

1. Start the server:
   ```bash
   python3 server.py
   ```
2. Open your browser at:
   ```
   http://localhost:8088
   ```
