# Large-Scale Multi-Agent System for Aesthetic and Compliance-Aware Web Design Generation

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Protocol%20Enabled-8A2BE2.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade, modular, closed-loop multi-agent research architecture for synthesizing, evaluating, and iteratively refining web designs across aesthetic, accessibility (WCAG 2.1 AA), usability, ethics/compliance (dark pattern detection), and originality dimensions.

---

## 🏗️ Architecture Overview

The system implements a continuous critique-aggregation-refinement loop that moves beyond simple chain-of-thought or monolithic generation.

```mermaid
flowchart TD
    UserPrompt([User Prompt]) --> PromptStructurer[Prompt Structurer Agent]
    PromptStructurer --> StructuredPrompt[Structured Specification JSON (14 Fields)]
    StructuredPrompt --> WebGen[Web Generator Agent]
    WebGen --> SiteCandidate[Website Candidate (HTML/CSS/JS)]
    
    subgraph EvaluationPipeline [Specialized Evaluation Layer / Baseline Critic]
        SiteCandidate --> Aesthetic[Aesthetic Agent]
        SiteCandidate --> Accessibility[Accessibility Agent + Static WCAG Engine]
        SiteCandidate --> Usability[Usability Agent]
        SiteCandidate --> Ethics[Ethics & Compliance Agent]
        SiteCandidate --> Originality[Originality & Diversity Agent]
        SiteCandidate --> GeneralCritic[General Critic Agent (Baseline Mode)]
    end

    Aesthetic --> Aggregator[Feedback Aggregator]
    Accessibility --> Aggregator
    Usability --> Aggregator
    Ethics --> Aggregator
    Originality --> Aggregator
    GeneralCritic --> Aggregator
    
    Aggregator --> PrioritizedPlan[Prioritized Refinement Plan & Conflict Resolution]
    PrioritizedPlan --> Refiner[Design Refiner Agent]
    SiteCandidate --> Refiner
    Refiner --> RefinedSite[Refined Website Candidate]
    
    RefinedSite --> EvalGate{Evaluation Gate}
    EvalGate -- Quality Threshold Met OR Max Iterations --> FinalSite[Final Website + Evaluation Report]
    EvalGate -- Quality Threshold Not Met & Iterations Left --> EvaluationPipeline
```

---

## 🔬 Experimental Modes & Research Hypothesis

The platform is designed to rigorously test whether distributing evaluation across specialized agents yields superior web design artifacts compared to standard generation pipelines:

1. **`SYSTEM_MODE=generator_only` (Baseline A)**:
   - Single-pass generation from structured specification without feedback loops.
2. **`SYSTEM_MODE=general_critic` (Baseline B)**:
   - Iterative refinement guided by a single generalist reviewer.
3. **`SYSTEM_MODE=specialized_multi_agent` (Proposed Architecture)**:
   - Full closed-loop collaboration among 5 domain specialists, static deterministic AST/DOM analyzers, conflict-resolving aggregator, and surgical refiner.
4. **Agent Ablation Support**:
   - Deactivate any combination of agents (e.g. `--ablate aesthetic,ethics`) to evaluate marginal value and investigate where diminishing returns appear.

---

## 🤖 The Specialist Agents

| Agent | Responsibility | Key Evaluation Dimensions |
| :--- | :--- | :--- |
| **Prompt Structurer** | Formalizes raw prompts | 14-field research JSON schema specifying functional, visual, WCAG, UX, compliance, and originality acceptance criteria. |
| **Web Generator** | Synthesizes full website | Semantic HTML5 landmarks, modern responsive CSS3 variables, and vanilla ES6+ interactive features. |
| **Aesthetic Agent** | Visual polish & harmony | Visual hierarchy, typography scales, spacing rhythm, color harmony, card elevation, and composition balance. |
| **Accessibility Agent** | WCAG 2.1 AA conformance | Blends LLM review with deterministic static checks (image `alt` tags, heading hierarchy, form `label` associations, contrast ratios, and `:focus-visible` rings). |
| **Usability Agent** | UX journeys & conversion | Navigation discoverability, CTA prominence, mobile touch targets, micro-interaction feedback, and cognitive load. |
| **Ethics & Compliance Agent** | Deceptive design audit | Dark pattern detection (fake countdowns, confirm-shaming, pre-checked opt-ins, disguised ads, hidden fees, and data consent transparency). |
| **Originality & Diversity Agent** | Creative distinction | Evaluates visual distinctness, layout variety, bespoke widgets, and avoidance of generic template clichés. |
| **General Critic Agent** | Holistic baseline critic | Single monolithic review used for Baseline Mode B evaluation. |
| **Feedback Aggregator** | Strategic synthesis | Normalizes scores, isolates blocking issues, resolves conflicting advice (e.g. minimalism vs boundary clarity), and establishes preservation directives. |
| **Design Refiner** | Surgical code revision | Implements targeted improvements across HTML/CSS/JS with explicit issue-to-action mappings while preserving intact features. |

---

## 🔌 Provider-Agnostic LLM Layer

The system decouples agent logic from LLM SDKs through `providers.base.LLMProvider`.

- **Supported Providers**: `OpenAIProvider`, `AnthropicProvider`, `MockProvider`.
- **Zero-Dependency Mock Fallback**: When API keys are absent or during offline testing, the system automatically falls back to `MockProvider` which generates realistic, valid HTML/CSS/JS, rich critiques, and surgical refinements.
- **Per-Agent Model Routing**: Configure provider and model independently for every agent via `.env` or `config/default_config.yaml`.

```bash
# Example .env configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

PROMPT_STRUCTURER_PROVIDER=openai
PROMPT_STRUCTURER_MODEL=gpt-4o-mini

GENERATOR_PROVIDER=anthropic
GENERATOR_MODEL=claude-3-5-sonnet-20241022

AESTHETIC_AGENT_PROVIDER=openai
AESTHETIC_AGENT_MODEL=gpt-4o

ACCESSIBILITY_AGENT_PROVIDER=openai
ACCESSIBILITY_AGENT_MODEL=gpt-4o

REFINER_PROVIDER=anthropic
REFINER_MODEL=claude-3-5-sonnet-20241022
```

---

## 🚀 Quickstart & Usage

### 1. Installation

```bash
git clone <repo-url>
cd vibrant-faraday
pip install -r requirements.txt
```

### 2. Interactive CLI Generation

```bash
# Run multi-agent generation in terminal
python -m app --prompt "Create a modern sustainable fashion website with organic earth tones."

# Run with baseline modes
python -m app --mode generator_only --prompt "Minimalist architect portfolio"
python -m app --mode general_critic --prompt "SaaS analytics platform"
python -m app --mode specialized_multi_agent --ablate aesthetic,ethics --prompt "Pediatric clinic portal"
```

### 3. Launch Web Server & Visual Sandbox Dashboard

```bash
python -m app --server
```
Visit **http://localhost:8000** to access the interactive web sandbox:
- Live rendered responsive preview (Desktop / Tablet / Mobile).
- Step-by-step iteration switcher (Iter 1, Iter 2, Final).
- Real-time radar/score quickbar across all 5 dimensions.
- Specialist critique inspector & issue tracker.
- Aggregated plan, preserve directives, and surgical change logs.
- Interactive source code viewer (HTML / CSS / JavaScript).

---

## 📊 Benchmark Suite & Research Experiments

The platform includes a 10-task diverse domain benchmark (`datasets/benchmark.json`) covering E-Commerce, SaaS, Healthcare, Fintech, Hospitality, Non-Profit, Portfolio, EdTech, Civic Portals, and Consumer Electronics.

### Running Comparative Research Experiments

```bash
# Run comprehensive 3-mode comparison sweep
python run_experiment.py --all-modes --tasks 3 --output results/

# Run specific mode
python run_experiment.py --mode specialized_multi_agent --tasks 5

# Run ablation study
python run_experiment.py --mode specialized_multi_agent --ablate aesthetic,ethics --tasks 5
```

All runs produce structured JSON and CSV reports in `results/` logging composite scores, dimensional scores, WCAG pass rates, dark pattern counts, iterations, latency, and token costs.

---

## 🌐 API & Protocols

### REST Endpoints (FastAPI)
- `POST /api/generate` - Trigger generation pipeline.
- `GET /api/run/{run_id}` - Fetch full run state and artifacts.
- `GET /api/run/{run_id}/evaluation` - Fetch evaluation report and breakdown.
- `GET /api/run/{run_id}/iterations` - Fetch iteration history with diffs.
- `GET /api/run/{run_id}/website` - Get raw HTML, CSS, JS.
- `GET /api/preview/{run_id}/{iteration_or_final}` - Sandboxed preview endpoint with CSP security headers.
- `GET /api/runs` - List historical runs.
- OpenAPI docs: `http://localhost:8000/docs`

### OpenAI-Compatible Universal Endpoints
- `POST /v1/generate` - Generate website via standard JSON payload.
- `POST /v1/evaluate` - Evaluate external HTML/CSS/JS with 5 specialist agents.
- `POST /v1/refine` - Refine external HTML/CSS/JS with feedback.

### Model Context Protocol (MCP) Server
External AI agents (Claude Code, Cursor, AI assistants) can connect directly:

```bash
# Start MCP server on stdio
python -m app --mcp
# or
python mcp_server/server.py
```

**Exposed MCP Tools**:
- `generate_website(prompt, max_iterations)`
- `evaluate_website(html, css, js, prompt)`
- `refine_website(html, css, js, feedback)`
- `run_multi_agent_pipeline(prompt, system_mode, ablated_agents, max_iterations)`
- `get_run_status(run_id)`
- `get_evaluation_report(run_id)`
- `get_iteration_history(run_id)`

---

## 📁 Versioned Artifact Workspace

Every run produces an isolated, reproducible workspace structure:

```
runs/
  run_20260907_120000_a1b2c3/
    structured_prompt.json
    iteration_01/
      prompt.json
      website/
        index.html
        styles.css
        script.js
        metadata.json
      critiques/
        aesthetic.json
        accessibility.json
        usability.json
        ethics.json
        originality.json
      aggregate.json
      refinement.json
      evaluation.json
    iteration_02/
      ...
    final_website/
      index.html
      styles.css
      script.js
    final_report.json
    telemetry.jsonl
```

---

## 🧪 Testing

Run the full automated test suite:

```bash
pytest -v
```

Tests cover:
- Provider abstraction & JSON recovery
- Static WCAG & Dark Pattern Analysis
- Individual specialist agent lifecycles
- Multi-agent orchestration, modes, and ablations
- REST API & OpenAI compatibility routes
- Experiment runner & summary aggregation

---

## 📜 License
MIT License. Developed for research in multi-agent web design and automated software engineering.
