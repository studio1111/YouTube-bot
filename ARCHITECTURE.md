# Architecture map

## Principle

Build a durable, versioned workflow rather than one unrestricted agent loop. An episode is a state machine with immutable inputs, typed artifacts, resumable stages, and approval gates.

```text
Topic / source video
        |
        v
Research + source ledger + rights checks
        |
        v
Idea -> outline -> script -> SEO package
        |
        v
Scene plan -> asset requests -> TTS/STT -> captions
        |
        v
Render plan -> FFmpeg/MoviePy -> thumbnails
        |
        v
Automated media QA + provenance manifest
        |
        v
Human approval -> private YouTube upload
        |
        v
Human release approval -> schedule/publication
        |
        v
Analytics feedback -> next research cycle
```

## Core components

- `domain/`: typed contracts, episode states, manifest and provenance models.
- `agent/`: orchestration, policies, prompts, and provider interfaces.
- `media/`: render plans, captions, audio/video validation.
- `apps/`: API, reviewer UI, and workers to be added after the vertical slice.
- `infra/`: optional Docker services. Start with SQLite and local files; add PostgreSQL/Temporal only when needed.
- `docs/`: architecture decisions, research evidence, and operations notes.

## Episode states

`IDEA -> RESEARCHED -> SCRIPT_DRAFT -> SCRIPT_APPROVAL -> ASSET_PRODUCTION -> RENDERED -> QA -> PUBLISH_APPROVAL -> PRIVATE_UPLOADED -> RELEASED`

Every transition is recorded. Rejection creates a new version; it never mutates an approved artifact.

## Provider boundary

```text
LLMProvider
ResearchProvider
SpeechToTextProvider
TextToSpeechProvider
ImageProvider
VideoProvider
Renderer
Publisher
```

The workflow depends on these interfaces, not vendor-specific SDKs. Each provider returns an artifact plus metadata: model, revision, prompt/input digest, timestamps, and license/provenance.

## Storage

MVP: SQLite metadata plus `runtime/` content-addressed files. Production: PostgreSQL for metadata and an S3-compatible store such as SeaweedFS. Store SHA-256 digests for every artifact. Never overwrite approved outputs.

## Scaling path

1. Local Python state machine.
2. Docker Compose with workers.
3. Temporal OSS for durable timers/retries and approval signals.
4. Separate CPU/GPU queues and object storage.
5. OpenTelemetry, Prometheus, Grafana, backups, and restore tests.

Do not start with Kubernetes, Kafka, or a vector database. They solve scale problems before this channel has validated its editorial process.
