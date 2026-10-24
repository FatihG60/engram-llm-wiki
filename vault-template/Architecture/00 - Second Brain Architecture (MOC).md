---
title: "00 - Second Brain Architecture (MOC)"
tags: [moc, architecture, second-brain, ikinci-beyin, engram, karpathy, llm-wiki]
aliases: [Second Brain MOC, Architecture MOC, Mimari MOC]
created: 2026-10-24
---

# 🏛️ Second Brain Architecture / İkinci Beyin Mimarisi (MOC)

**Root Index / Ana İndeks:** [[Hoş geldiniz]] · **Chronological Log / Günlük:** [[log]]

## Core Notes / Temel Notlar
- 📚 [[01 - Karpathy LLM Wiki and Engram Synthesis]] — Full architectural blueprint uniting Karpathy's 3-layer compiled Markdown Wiki with Engram's vectorless SQLite FTS5 BM25 + Recency Weighting engine.

```mermaid
flowchart LR
    RAW["raw/ (Immutable Sources)"] -->|"Ingest"| WIKI["Obsidian Wiki (MOC + Pages)"]
    WIKI -->|"Lint (100/100)"| LOG["log.md (Chronological Log)"]
    WIKI & RAW -->|"Delta Sync"| DB["engram.db (SQLite FTS5 BM25 + Recency)"]
    DB <-->|"MCP (7 Tools)"| AGENTS["Claude Code · Antigravity · Cursor · Hermes"]
```

Back / Geri: [[Hoş geldiniz]]
