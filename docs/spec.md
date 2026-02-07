# SupplyChain Insight ETL + Query + Visualization

> Scope: Taiwan Top 50 + Global Top 500 company universe.

## 1) Project Name

**SupplyChain Insight ETL + Query + Visualization（台灣前50大 + 世界前500強）**  
**SupplyChain Insight ETL + Query + Visualization (Taiwan Top 50 + Global Top 500)**

## 2) Goals & Scope

- Daily refresh supply-chain data for Taiwan Top 50 and Global Top 500 companies.
- Persist normalized data into databases.
- Expose query APIs and interactive visualizations.
- Support per-company quarterly financial time-series (revenue, operating income, net income, EPS, etc.).

## 3) Non-Functional Requirements

- Horizontal scalability for large company coverage and daily updates.
- Full provenance per record (source, fetch time, version).
- Data-quality controls (missing/conflicting/duplicated/anomalous changes).
- Licensing and legal compliance (no unauthorized paid-content scraping, no ToS violations).

## 4) Definitions

**Supply-chain information** includes at minimum:

- company–supplier–customer relations,
- tier level (Tier 1/2/3),
- product/part mapping,
- geography,
- confidence score,
- provenance.

Taiwan Top 50 and Global Top 500 company lists must be configurable (static files or daily refreshed ranking sources).

## 5) Data Source Strategy (Must Read)

Supply-chain data is frequently premium/commercial. The system **must** support a multi-source abstraction layer to mix/swap open and licensed providers.

### MVP source strategy

1. Company disclosures (annual reports, sustainability reports, supplier lists, material announcements).
2. Taiwan public disclosures (e.g., MOPS/TWSE) for company metadata and financial fields.
3. News/announcements for risk events with source-tagging and confidence.

## 6) System Architecture Overview

Four layers:

1. Daily scheduled ETL/ELT
2. Normalized database
3. Query API
4. Frontend visualization

Recommended modules:

- Ingestion
- Normalization
- Storage
- API
- Visualization
- Monitoring

## 7) Recommended Tech Stack

- **Backend**: Python (data pipelines) + TypeScript/Node (API/BFF) or equivalent.
- **Scheduling**: Airflow or Prefect (MVP: cron + Docker).
- **Database**: PostgreSQL + optional Neo4j for graph queries.
- **Cache**: Redis.
- **Web**: React + D3 or Apache ECharts.

## 8) Core Data Model

### 8.1 `company`

- `id` UUID PK
- `name_zh`, `name_en`
- `country`, `region`
- `industry`, `sub_industry`
- `tw_ticker` nullable
- `isin`, `lei`, `figi` nullable
- `source`, `source_url`, `fetched_at`
- `updated_at`

### 8.2 `supply_chain_edge`

- `id` UUID PK
- `from_company_id` FK `company.id`
- `to_company_id` FK `company.id`
- `relation_type` ENUM: `supplier_to_customer` / `customer_to_supplier` / `peer` / `unknown`
- `tier` INT nullable
- `product_tag` TEXT nullable
- `confidence` float (0–1)
- `first_seen_at`, `last_seen_at`
- `source`, `source_url`, `fetched_at`
- `version_hash` (dedup/version key)

### 8.3 `financial_quarterly`

- `id` UUID PK
- `company_id` FK
- `fiscal_year` INT
- `fiscal_quarter` INT (1–4)
- `revenue` NUMERIC
- `operating_income` NUMERIC nullable
- `net_income` NUMERIC nullable
- `eps` NUMERIC nullable
- `currency` TEXT
- `source`, `source_url`, `fetched_at`
- `updated_at`
- Unique key: `(company_id, fiscal_year, fiscal_quarter, source)`

### 8.4 `risk_event` (optional but strongly recommended)

- `id` UUID PK
- `company_id` FK nullable
- `event_type` ENUM
- `title`, `summary`
- `happened_at` DATE/TIMESTAMP
- `geo` POINT/region code nullable
- `severity` INT (1–5)
- `source`, `source_url`, `fetched_at`

## 9) ETL Pipeline

### 9.1 Daily jobs

- Schedule: every day 02:30 Asia/Taipei.
- Modes: full refresh + incremental refresh.

Flow:

1. Fetch company universe lists (TW50 + Global500).
2. Pull supply-chain data for each company from multiple sources.
3. Pull/update quarterly financials.
4. Normalize identifiers/names/geo/industry.
5. Upsert with versioning.
6. Run DQ checks + alerts.

### 9.2 Dedup & versioning rules

- Preserve multi-source provenance for equivalent edges.
- Merge equivalent edges into weighted relationship at query time.
- Suggested `version_hash` input: `(from_id, to_id, relation_type, tier, product_tag)`.
- Suggested confidence model: source reliability × recurrence × recency.

## 10) Query API Spec

### 10.1 Company search

`GET /api/companies?query=TSMC`

Returns: `id`, names, ticker, country, industry.

### 10.2 Supply-chain view

`GET /api/companies/{id}/supply-chain?depth=3&direction=both&as_of=YYYY-MM-DD`

Returns nodes/edges with `tier`, `confidence`, `product_tag`, source summary.

Required filters:

- `depth`: 1–3 for MVP (future up to 5)
- `direction`: upstream/downstream/both
- `as_of`: snapshot date (versioned)

### 10.3 Quarterly financials

`GET /api/companies/{id}/financials/quarterly?from=2018Q1&to=2025Q4`

Returns a continuous time series suitable for line chart and YoY/QoQ.

### 10.4 Aggregations (for visualization)

`GET /api/companies/{id}/supply-chain/metrics`

Returns concentration (top-N share), geo distribution, industry distribution, risk-event stats.

## 11) Frontend Visualization Requirements

- Supply-chain network graph:
  - node size by revenue or degree,
  - edge thickness by confidence.
- Geographic distribution map:
  - heatmap or points,
  - toggle visibility for sensitivity.
- Time series:
  - quarterly revenue line,
  - YoY/QoQ toggle,
  - currency display.
- Dashboard:
  - company profile,
  - supply-chain summary,
  - risk timeline.

## 12) Auth & Security

- If licensed data is included, enforce API key/OAuth and plan-based limits.
- Store secrets in secret manager. Never hardcode API keys.

## 13) Monitoring & Alerts

Track and alert on:

- ETL success rate,
- per-source failure rate,
- data freshness/latency,
- missing-data rate,
- revenue spikes/drops,
- sudden mass edge disappearance/addition.

## 14) Testing & Acceptance Criteria

- TW50 + Global500 company master rows updated within 24h after daily run.
- For 10 sampled companies, depth=2 supply-chain API latency under 2s (cache hit under 500ms).
- Quarterly financials cover latest 5 years when source allows.
- Visualization remains smooth up to 500 nodes.

## 15) Codex Task Breakdown

### 15.1 Monorepo layout

- `/etl`
- `/api`
- `/web`
- `/infra`

### 15.2 ETL (Python)

- Source adapter interface:
  - `fetch_company_list()`
  - `fetch_supply_chain(company)`
  - `fetch_financials(company)`
- Implement at least two adapters:
  - `PublicTaiwanAdapter`
  - `DisclosureParserAdapter` (PDF/HTML parsing)
- Implement cleaning:
  - name normalization,
  - ID resolution,
  - dedup,
  - confidence scoring.

### 15.3 DB migrations

- Use Alembic (or Prisma) to create core tables and indexes:
  - `company.name`, ticker indexes
  - edge `(from_company_id, to_company_id)` index
  - financial unique key.

### 15.4 API (Node/TS or FastAPI)

- Endpoints:
  - company search
  - supply-chain view
  - financial quarterly
  - metrics
- Add Redis cache for hot queries.

### 15.5 Web (React)

- 3 pages:
  - Company Search
  - Company Dashboard
  - Supply Chain Explorer
- Explorer must support filters:
  - tier,
  - country,
  - confidence threshold.

### 15.6 Infra (Docker Compose)

- services:
  - postgres
  - redis
  - optional neo4j
  - api
  - etl
  - web
- daily scheduling via cron container or Airflow.

## 16) Key Risks & Fallbacks

- If supply-chain source coverage is limited, prioritize extensible architecture + fewer high-confidence sources, while clearly surfacing confidence/provenance in UI.
- If Global500 ranking source changes, support configurable list ingestion (CSV/admin config).

## 17) Remaining Inputs Required From Product/Business

1. Definition and source of Taiwan Top 50 and Global Top 500 lists.
2. Actual supply-chain source choice (licensed APIs vs public disclosures), which determines data completeness ceiling.
