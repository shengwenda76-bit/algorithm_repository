# Algorithm Platform Design (Draft)

Date: 2026-03-05
Status: Approved in brainstorming session
Scope: Build algorithm platform that integrates with business platform where business side does visual flow authoring and algorithm platform executes full flow asynchronously.

## 1. Confirmed Constraints

- Integration pattern: async submit + callback/polling.
- Execution model: built-in execution in algorithm platform (no per-algorithm container at this stage).
- IO definition: manually registered JSON Schema with versioning.
- Flow authoring ownership: business platform.
- Runtime ownership: business platform submits full DSL once; algorithm platform orchestrates and executes entire flow.
- Scale target (phase 1): small scale, fewer than 50 concurrent flow instances.
- Failure policy: fail-fast; if any node fails, whole flow fails; manual full-flow retry supported.

## 2. Architecture Choice

Chosen approach: modular monolith with task-queue abstraction.

Why:
- Fast enough for phase-1 delivery.
- Clean module boundaries for future split-out.
- Native fit for async execution and callback/polling.
- Lower operational complexity than microservices.

Alternatives considered:
- Pure monolith direct execution: faster start but weak evolution path.
- Full microservices + MQ: strongest scalability but over-designed for current scope.

## 3. System Boundaries

Business platform responsibilities:
- Visual flow authoring and editing.
- Build and submit Flow DSL.
- Receive callback and/or poll execution status.

Algorithm platform responsibilities:
- Algorithm library and version management.
- Input/output JSON Schema version management.
- DSL validation and DAG orchestration.
- Node execution, runtime state persistence, logs, callback.

## 4. Core Components

- Algorithm Registry
  - Stores algorithm metadata, versions, entrypoint, schema.
- DSL Validator
  - Validates schema, dependency graph, node references, mapping rules.
- Orchestrator
  - DAG topological scheduling, execution state machine.
- Executor
  - Runs built-in algorithm entrypoints with timeout/error normalization.
- Task Store
  - Persists flow and node runtime state, snapshots, errors.
- Callback/Query API
  - Push completion event to business platform and provide polling endpoints.

## 5. Runtime Data Flow

1. Business platform optionally queries algorithm catalog and target version schemas.
2. Business platform calls POST /v1/executions?validate_only=true with full Flow DSL.
3. Algorithm platform validates DSL structure, algorithm version references, mapping rules, and DAG acyclic constraint.
4. If pre-validation passes, business platform calls POST /v1/executions with Idempotency-Key.
5. Algorithm platform creates execution_id and returns immediately (async accept).
6. Orchestrator resolves ready nodes and enqueues execution tasks.
7. Workers execute nodes and persist node output snapshots.
8. On first node failure: mark node FAILED, mark execution FAILED, stop downstream scheduling.
9. On completion (SUCCEEDED or FAILED): send signed callback; polling remains available as fallback.

## 6. External API Contract (Algorithm Platform)

- GET /v1/algorithms
  - Return grouped catalog: categories[].algorithms[] with category/status/latest_version.
- GET /v1/algorithms/{algo_code}/versions/{version}
  - Return input_schema/output_schema and runtime defaults.
- POST /v1/executions?validate_only=true
  - Validate-only endpoint; returns validation result without creating execution.
- POST /v1/executions
  - Submit full Flow DSL for async execution; return execution_id and initial status.
  - Idempotency-Key required for client retry safety; semantic conflict returns 409 IDEMPOTENCY_CONFLICT.
- GET /v1/executions/{execution_id}
  - Return flow-level status and summary.
- GET /v1/executions/{execution_id}/nodes
  - Return node-level status and snapshots summary.
- POST /v1/executions/{execution_id}/retry
  - Manual full-flow retry for FAILED execution only; returns new execution_id and parent_execution_id.
  - Non-FAILED retry returns 409 RETRY_NOT_ALLOWED.

Callback endpoint on business side:
- POST <business_callback_url>
  - Signed payload with execution_id, final status, summary, and timestamps.
  - Headers: X-Signature (HMAC-SHA256), X-Timestamp, X-Trace-Id.
  - Timestamp tolerance window: 5 minutes (anti-replay).

## 7. Flow DSL Minimum Schema

- meta
  - flow_code, flow_version, trace_id, callback_url.
- nodes[]
  - node_id, algo_code, algo_version, params, timeout_sec.
- edges[]
  - from_node, to_node, mapping_rules.
- inputs
  - run-level initial data reference or inline parameters.

## 8. Data Model (Phase 1)

- algorithm_def
  - algo_code, name, category, owner, status.
- algorithm_version
  - algo_code, version, input_schema_json, output_schema_json, entrypoint, default_timeout_sec, is_active.
- execution
  - execution_id, parent_execution_id, flow_code, flow_version, trace_id, status, dsl_snapshot_json, run_context_json, idempotency_key, started_at, ended_at, error_summary.
- execution_node
  - execution_id, node_id, algo_code, algo_version, status, input_snapshot_json, output_snapshot_json, started_at, ended_at, error_detail.
- callback_delivery (recommended)
  - execution_id, callback_url, signature, timestamp, attempt_no, status, response_code, next_retry_at.
- execution_event (recommended)
  - append-only lifecycle and transition events.

## 9. Error Handling and Reliability

- Validation-stage errors: 400 with machine-readable error codes (DSL_SCHEMA_INVALID, FLOW_GRAPH_CYCLE, ALGO_VERSION_NOT_FOUND).
- Runtime node errors: normalized error type and stack capture.
- Timeout: convert to NODE_TIMEOUT and fail flow.
- Callback security: HMAC-SHA256 signature + timestamp verification (5-minute window).
- Callback failure: async retry (3 retries with exponential backoff) and keep polling fallback.
- Idempotency: support Idempotency-Key on submission with a 24-hour dedup window.
- Idempotency semantic mismatch: return 409 IDEMPOTENCY_CONFLICT.
- Retry guard: only FAILED execution can be retried, otherwise 409 RETRY_NOT_ALLOWED.

## 10. Observability Baseline

- Correlation: trace_id propagated across API, orchestration, workers, callback.
- Metrics:
  - flow_success_rate
  - flow_duration
  - node_failure_topn
  - callback_success_rate
- Logs:
  - flow lifecycle logs
  - node input/output summary logs (avoid full large payload)
  - structured error logs

## 11. Testing Baseline

- Unit tests:
  - DSL validator
  - DAG topological scheduling
  - mapping resolution
  - state transitions
- Integration tests:
  - full success path
  - mid-node failure -> fail-fast
  - callback retry path
- Contract tests:
  - validate_only pre-check then formal submit flow
  - idempotency conflict behavior (409 IDEMPOTENCY_CONFLICT)
  - retry restriction (only FAILED) and parent_execution_id linkage
  - callback payload/signature validation with business platform.
- Non-functional checks:
  - POST /v1/executions returns execution_id within 1 second (accept latency only).
- Regression samples:
  - missing-value-processing -> anomaly-detection -> standardization chain.

## 12. Non-goals (Phase 1)

- No dual-authoring source of truth.
- No compensation/skip/degrade strategy.
- No high-scale distributed scheduling yet.

## 13. Evolution Path

- Replace in-process queue abstraction with MQ with minimal API changes.
- Split executor and orchestrator into independent services when concurrency target grows.
- Add advanced failure policies after stable phase-1 operations.
