# SSE Streaming for Multi-Agent Feedback Design Spec

## Goal
Implement Server-Sent Events (SSE) to stream the real-time execution status of the LangGraph multi-agent workflow to the frontend. This will provide users with a "typewriter" style log terminal and glowing step highlights, solving the current "blind waiting" UX problem during resource generation.

## Architecture & Data Flow

1. **Backend (FastAPI)**
   - **Endpoint**: `POST /generation/stream`
   - **Mechanism**: Instead of `_GRAPH.invoke()`, the backend uses `_GRAPH.stream()`. For each node execution, it yields a JSON string wrapped in SSE format (`data: {"node": "...", "message": "..."}\n\n`).
   - **Caching**: The backend still checks `target_node` in the SQLite `Session` table. If a cached result exists, it yields a simulated fast stream or a single success event to maintain the UI animation pattern before returning the cached JSON.
   
2. **Frontend (Vue3 + Pinia)**
   - **API Transport**: Replace Axios with native `fetch` and `ReadableStream`.
   - **State (generation.ts)**:
     - `activeNode`: `string | null` (The currently running Agent).
     - `streamLogs`: `Array<{id: number, text: string, type: 'info' | 'warning' | 'success'}>`.
     - `isStreaming`: `boolean`.
   - **UI (DashboardView.vue)**:
     - Use `activeNode` to dynamically apply a CSS `.active-pulse` class to the corresponding Agent step icon.
     - Add a scrollable terminal container (`<div class="terminal-logs">`) bound to `streamLogs`. Automatically scroll to the bottom upon new log entries.

## Error Handling & Fallbacks
- If the SSE connection drops prematurely, an error log is pushed to the terminal and `isStreaming` is set to false.
- The `try-catch` block catches backend crashes and alerts the user cleanly.
- Re-triggering generation will utilize backend SQLite cache, so no LLM tokens are wasted on network disconnects.
