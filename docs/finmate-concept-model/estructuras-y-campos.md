# Anexo: estructuras y campos del conocimiento actual

> Estado: inventario estático generado para el corte de 2026-10-17.
> Autoridad: declaraciones de los archivos enlazados; no inspecciona una base desplegada.

Complementa el [informe conceptual](modelo-conocimiento-actual.md). Incluye campos declarados, bases, restricciones SQL declaradas y nombres de validadores; el informe explica su significado y recorrido. Las expresiones son código de declaración, no valores de usuarios ni resultados de una ejecución.

Los campos heredados deben leerse en su clase base. Una declaración Column sin anotación utiliza su expresión SQLAlchemy como autoridad de tipo. Los campos de dataclasses describen memoria/proyecciones, no tablas. Los Literal enumeran valores aceptados, no capacidades completas entregadas. El inventario no expande diccionarios de catálogo ni copia implementaciones de métodos.

Comando histórico desde la raíz de FinMate (el script de `artifacts/` no se distribuye con este repositorio): `.\.venv\Scripts\python.exe artifacts/knowledge-archaeology/2026-10-17/generar_inventario.py`. Regenerar actualiza las huellas al árbol del momento; para comparar cortes, conservar el manifiesto anterior en Git.

## 1. Modelos físicos del dominio privado

### Analysis

Fuente: [finmate/state/models/analysis.py](../../../FinMate/finmate/state/models/analysis.py), línea 11. Bases: `Base`.

Tabla: `domain_analyses`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str &#124; None]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=True, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `type` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `event_id` | `Mapped[str &#124; None]` | `mapped_column(ForeignKey('domain_events.id', ondelete='CASCADE'), index=True)` |
| `content` | `Mapped[object]` | `mapped_column(JSON, nullable=False)` |
| `created_by` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(CheckConstraint("type IN ('fundamental', 'technical', 'sectorial', 'competitive', 'event_briefing')", name='ck_domain_analyses_type'), CheckConstraint("created_by IN ('agent', 'user')", name='ck_domain_analyses_created_by'), CheckConstraint("(type = 'event_briefing' AND event_id IS NOT NULL) OR (type <> 'event_briefing' AND event_id IS NULL)", name='ck_domain_analyses_event_binding'), Index('uq_domain_analyses_user_event_briefing', 'user_id', 'event_id', unique=True, sqlite_where=text("type = 'event_briefing'"), postgresql_where=text("type = 'event_briefing'")))
```

### DeliberationJob

Fuente: [finmate/state/models/deliberation.py](../../../FinMate/finmate/state/models/deliberation.py), línea 11. Bases: `Base`.

Tabla: `domain_deliberation_jobs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `task_type` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `status` | `Mapped[str]` | `mapped_column(String(20), nullable=False, default='queued')` |
| `input_context` | `Mapped[dict]` | `mapped_column(JSON, nullable=False, default=dict)` |
| `output_delta` | `Mapped[dict &#124; None]` | `mapped_column(JSON)` |
| `error_message` | `Mapped[str &#124; None]` | `mapped_column(Text)` |
| `created_by` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(CheckConstraint("task_type IN ('analyze', 'build_thesis', 'explore_gap', 'reconsider', 'value', 'scan_events', 'screen', 'deliberate', 'open_thesis', 'characterize_company', 'investigate_need')", name='ck_domain_deliberation_jobs_task_type'), CheckConstraint("status IN ('queued', 'running', 'completed', 'failed', 'awaiting_input')", name='ck_domain_deliberation_jobs_status'), CheckConstraint("created_by IN ('agent', 'user')", name='ck_domain_deliberation_jobs_created_by'))
```

### Event

Fuente: [finmate/state/models/event.py](../../../FinMate/finmate/state/models/event.py), línea 11. Bases: `Base`.

Tabla: `domain_events`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `event_type` | `Mapped[str]` | `mapped_column(String(30), nullable=False)` |
| `title` | `Mapped[str]` | `mapped_column(String(240), nullable=False)` |
| `content` | `Mapped[str]` | `mapped_column(Text, nullable=False)` |
| `event_date` | `Mapped[date]` | `mapped_column(Date, nullable=False)` |
| `source_url` | `Mapped[str &#124; None]` | `mapped_column(Text)` |
| `created_by` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(Index('ix_domain_events_symbol_recency', 'symbol', 'event_date', 'created_at', 'id'), CheckConstraint("event_type IN ('earnings_call', 'sec_filing', 'regulatory', 'news', 'analyst_report', 'macro')", name='ck_domain_events_event_type'), CheckConstraint("created_by IN ('connector', 'agent', 'user')", name='ck_domain_events_created_by'))
```

### Evidence

Fuente: [finmate/state/models/evidence.py](../../../FinMate/finmate/state/models/evidence.py), línea 11. Bases: `Base`.

Tabla: `domain_evidence`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `content` | `Mapped[str]` | `mapped_column(Text, nullable=False)` |
| `structured_content` | `Mapped[dict &#124; None]` | `mapped_column(JSON)` |
| `source` | `Mapped[str]` | `mapped_column(String(30), nullable=False)` |
| `origin` | `Mapped[str]` | `mapped_column(String(40), nullable=False)` |
| `source_ref` | `Mapped[str &#124; None]` | `mapped_column(Text)` |
| `timestamp` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `links` | `Mapped[list['EvidenceLink']]` | `relationship(back_populates='evidence', cascade='all, delete-orphan')` |

Restricciones/índices declarados:

```python
(CheckConstraint("source IN ('findata', 'event', 'web_search', 'user_input', 'agent_inference')", name='ck_domain_evidence_source'), CheckConstraint("origin IN ('initial_characterization', 'investigation', 'event', 'user_contribution', 'metric_probe', 'document_extraction', 'financial_snapshot', 'financial_observation', 'financial_comparison')", name='ck_domain_evidence_origin'))
```

### EvidenceLink

Fuente: [finmate/state/models/evidence.py](../../../FinMate/finmate/state/models/evidence.py), línea 43. Bases: `Base`.

Tabla: `domain_evidence_links`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `evidence_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_evidence.id', ondelete='CASCADE'), index=True)` |
| `dimension_key` | `Mapped[str]` | `mapped_column(String(40))` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `evidence` | `Mapped['Evidence']` | `relationship(back_populates='links')` |

Restricciones/índices declarados:

```python
(Index('uq_domain_evidence_links_dimension', 'evidence_id', 'dimension_key', unique=True),)
```

### MetricProbe

Fuente: [finmate/state/models/metric_probe.py](../../../FinMate/finmate/state/models/metric_probe.py), línea 11. Bases: `Base`.

Tabla: `domain_metric_probes`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `probe_kind` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `metric_key` | `Mapped[str]` | `mapped_column(String(80), nullable=False)` |
| `probe_spec` | `Mapped[dict]` | `mapped_column(JSON, nullable=False)` |
| `result` | `Mapped[dict]` | `mapped_column(JSON, nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, index=True)` |

Restricciones/índices declarados:

```python
(CheckConstraint("probe_kind IN ('trend', 'compare')", name='ck_domain_metric_probes_kind'), Index('ix_domain_metric_probes_user_symbol_created_at', 'user_id', 'symbol', 'created_at'))
```

### UserProfile

Fuente: [finmate/state/models/profile.py](../../../FinMate/finmate/state/models/profile.py), línea 13. Bases: `Base`.

Tabla: `domain_user_profiles`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), primary_key=True)` |
| `revision` | `Mapped[int]` | `mapped_column(Integer, nullable=False, default=1)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(CheckConstraint('revision >= 1', name='ck_user_profiles_revision'),)
```

### UserProfileFact

Fuente: [finmate/state/models/profile.py](../../../FinMate/finmate/state/models/profile.py), línea 24. Bases: `Base`.

Tabla: `domain_user_profile_facts`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_user_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)` |
| `key` | `Mapped[str]` | `mapped_column(String(64), nullable=False)` |
| `value` | `Mapped[object]` | `mapped_column(JSON, nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('user_id', 'key', name='uq_user_profile_fact_key'),)
```

### UserGoal

Fuente: [finmate/state/models/profile.py](../../../FinMate/finmate/state/models/profile.py), línea 37. Bases: `Base`.

Tabla: `domain_user_goals`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_user_profiles.user_id', ondelete='CASCADE'), nullable=False, index=True)` |
| `kind` | `Mapped[str]` | `mapped_column(String(32), nullable=False)` |
| `title` | `Mapped[str]` | `mapped_column(String(160), nullable=False)` |
| `description` | `Mapped[str &#124; None]` | `mapped_column(Text)` |
| `status` | `Mapped[str]` | `mapped_column(String(20), nullable=False, default='active')` |
| `priority` | `Mapped[int &#124; None]` | `mapped_column(Integer)` |
| `target_date` | `Mapped[date &#124; None]` | `mapped_column(Date)` |
| `target_amount` | `Mapped[Decimal &#124; None]` | `mapped_column(Numeric(20, 2))` |
| `currency` | `Mapped[str &#124; None]` | `mapped_column(String(3))` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('user_id', 'priority', name='uq_user_goal_priority'), CheckConstraint("kind IN ('growth','income','capital_preservation','retirement','major_purchase','other')", name='ck_user_goals_kind'), CheckConstraint("status IN ('active','achieved','abandoned')", name='ck_user_goals_status'), CheckConstraint("(status = 'active' AND priority IS NOT NULL AND priority >= 1) OR (status <> 'active' AND priority IS NULL)", name='ck_user_goals_priority'), CheckConstraint('(target_amount IS NULL AND currency IS NULL) OR (target_amount > 0 AND currency IS NOT NULL)', name='ck_user_goals_target'))
```

### ProfileMutationRequest

Fuente: [finmate/state/models/profile.py](../../../FinMate/finmate/state/models/profile.py), línea 60. Bases: `Base`.

Tabla: `domain_profile_mutation_requests`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `request_id` | `Mapped[str]` | `mapped_column(String(128), nullable=False)` |
| `request_hash` | `Mapped[str]` | `mapped_column(String(64), nullable=False)` |
| `resulting_revision` | `Mapped[int]` | `mapped_column(Integer, nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('user_id', 'request_id', name='uq_profile_mutation_request'),)
```

### ResearchDirective

Fuente: [finmate/state/models/research_directive.py](../../../FinMate/finmate/state/models/research_directive.py), línea 10. Bases: `Base`.

Tabla: `domain_research_directives`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `kind` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `dimension_key` | `Mapped[str &#124; None]` | `mapped_column(String(40), index=True)` |
| `statement` | `Mapped[str &#124; None]` | `mapped_column(Text)` |
| `status` | `Mapped[str]` | `mapped_column(String(20), nullable=False, default='active')` |
| `resolution_evidence_ids` | `Mapped[list[str]]` | `mapped_column(JSON, nullable=False, default=list)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |
| `addressed_at` | `Mapped[datetime &#124; None]` | `mapped_column(DateTime(timezone=True))` |

Restricciones/índices declarados:

```python
(CheckConstraint("kind IN ('emphasis', 'question')", name='ck_domain_research_directives_kind'), CheckConstraint("status IN ('active', 'addressed', 'dismissed')", name='ck_domain_research_directives_status'), CheckConstraint("((kind = 'emphasis' AND dimension_key IS NOT NULL AND statement IS NULL AND status <> 'addressed') OR (kind = 'question' AND statement IS NOT NULL AND trim(statement) <> ''))", name='ck_domain_research_directives_shape'), CheckConstraint("((status = 'addressed' AND addressed_at IS NOT NULL) OR (status <> 'addressed' AND addressed_at IS NULL))", name='ck_domain_research_directives_addressed'), CheckConstraint("dimension_key IS NULL OR dimension_key IN ('business_economics', 'competitive_advantage', 'growth', 'profitability', 'balance_sheet', 'valuation', 'risks', 'catalysts')", name='ck_domain_research_directives_dimension'))
```

### SavedScreen

Fuente: [finmate/state/models/saved_screen.py](../../../FinMate/finmate/state/models/saved_screen.py), línea 11. Bases: `Base`.

Tabla: `domain_saved_screens`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `name` | `Mapped[str &#124; None]` | `mapped_column(String(120))` |
| `screen_params` | `Mapped[dict]` | `mapped_column(JSON, nullable=False)` |
| `result_snapshot` | `Mapped[dict]` | `mapped_column(JSON, nullable=False)` |
| `interpretation` | `Mapped[str &#124; None]` | `mapped_column(Text)` |
| `last_run_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |
| `user` | `Mapped['User']` | `relationship(back_populates='saved_screens')` |

### InvestmentSelection

Fuente: [finmate/state/models/selection.py](../../../FinMate/finmate/state/models/selection.py), línea 10. Bases: `Base`.

Tabla: `domain_investment_selections`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False)` |
| `title` | `Mapped[str]` | `mapped_column(String(120), nullable=False)` |
| `purpose` | `Mapped[str]` | `mapped_column(Text, nullable=False)` |
| `horizon` | `Mapped[str]` | `mapped_column(String(16), nullable=False, default='long')` |
| `criteria` | `Mapped[dict]` | `mapped_column(JSON, nullable=False)` |
| `status` | `Mapped[str]` | `mapped_column(String(16), nullable=False, default='active')` |
| `revision` | `Mapped[int]` | `mapped_column(Integer, nullable=False, default=1)` |
| `comparison_sequence` | `Mapped[int]` | `mapped_column(Integer, nullable=False, default=0)` |
| `creation_request_id` | `Mapped[str]` | `mapped_column(String(128), nullable=False)` |
| `creation_request_hash` | `Mapped[str]` | `mapped_column(String(64), nullable=False)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(CheckConstraint("horizon = 'long'", name='ck_domain_investment_selections_horizon'), CheckConstraint("status IN ('active','archived')", name='ck_domain_investment_selections_status'), CheckConstraint('revision >= 1', name='ck_domain_investment_selections_revision'), UniqueConstraint('user_id', 'creation_request_id', name='uq_selection_creation_request'), Index('ix_selection_user_status_updated', 'user_id', 'status', 'updated_at'))
```

### SelectionCandidate

Fuente: [finmate/state/models/selection.py](../../../FinMate/finmate/state/models/selection.py), línea 34. Bases: `Base`.

Tabla: `domain_selection_candidates`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `selection_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_investment_selections.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(32), nullable=False)` |
| `ordinal` | `Mapped[int]` | `mapped_column(Integer, nullable=False)` |
| `active` | `Mapped[bool]` | `mapped_column(nullable=False, default=True)` |
| `decision_revision` | `Mapped[int]` | `mapped_column(Integer, nullable=False, default=0)` |
| `added_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `removed_at` | `Mapped[datetime &#124; None]` | `mapped_column(DateTime(timezone=True))` |

Restricciones/índices declarados:

```python
(UniqueConstraint('selection_id', 'symbol', name='uq_selection_candidate_symbol'), UniqueConstraint('selection_id', 'ordinal', name='uq_selection_candidate_ordinal'))
```

### SelectionComparison

Fuente: [finmate/state/models/selection.py](../../../FinMate/finmate/state/models/selection.py), línea 50. Bases: `Base`.

Tabla: `domain_selection_comparisons`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `selection_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_investment_selections.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `selection_revision` | `Mapped[int]` | `mapped_column(Integer, nullable=False)` |
| `sequence` | `Mapped[int]` | `mapped_column(Integer, nullable=False)` |
| `input_fingerprint` | `Mapped[str]` | `mapped_column(String(64), nullable=False)` |
| `input_snapshot` | `Mapped[dict]` | `mapped_column(JSON, nullable=False)` |
| `result` | `Mapped[dict]` | `mapped_column(JSON, nullable=False)` |
| `schema_version` | `Mapped[str]` | `mapped_column(String(32), nullable=False)` |
| `prompt_version` | `Mapped[str]` | `mapped_column(String(64), nullable=False)` |
| `comparison_policy_version` | `Mapped[str]` | `mapped_column(String(32), nullable=False)` |
| `model_id` | `Mapped[str &#124; None]` | `mapped_column(String(120))` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('selection_id', 'sequence', name='uq_selection_comparison_sequence'), UniqueConstraint('selection_id', 'selection_revision', 'input_fingerprint', name='uq_selection_comparison_input'))
```

### SelectionDecision

Fuente: [finmate/state/models/selection.py](../../../FinMate/finmate/state/models/selection.py), línea 70. Bases: `Base`.

Tabla: `domain_selection_decisions`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `candidate_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_selection_candidates.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `comparison_id` | `Mapped[str &#124; None]` | `mapped_column(ForeignKey('domain_selection_comparisons.id', ondelete='SET NULL'))` |
| `selection_revision` | `Mapped[int]` | `mapped_column(Integer, nullable=False)` |
| `sequence` | `Mapped[int]` | `mapped_column(Integer, nullable=False)` |
| `decision` | `Mapped[str]` | `mapped_column(String(24), nullable=False)` |
| `reason` | `Mapped[str]` | `mapped_column(String(500), nullable=False)` |
| `review_condition` | `Mapped[str &#124; None]` | `mapped_column(String(500))` |
| `request_id` | `Mapped[str]` | `mapped_column(String(128), nullable=False)` |
| `request_hash` | `Mapped[str]` | `mapped_column(String(64), nullable=False)` |
| `origin` | `Mapped[str]` | `mapped_column(String(16), nullable=False)` |
| `interaction_ref` | `Mapped[str &#124; None]` | `mapped_column(String(128))` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

Restricciones/índices declarados:

```python
(CheckConstraint("decision IN ('undecided','investigate','wait','discard','select')", name='ck_selection_decision_value'), CheckConstraint("origin IN ('ui','conversation')", name='ck_selection_decision_origin'), UniqueConstraint('candidate_id', 'sequence', name='uq_selection_decision_sequence'), UniqueConstraint('candidate_id', 'request_id', name='uq_selection_decision_request'))
```

### Thesis

Fuente: [finmate/state/models/thesis.py](../../../FinMate/finmate/state/models/thesis.py), línea 8. Bases: `Base`.

Tabla: `domain_theses`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), index=True)` |
| `contract_version` | `Mapped[str]` | `mapped_column(String(40), default='investment-case-v2')` |
| `input_revision` | `Mapped[int]` | `mapped_column(Integer, default=0)` |
| `knowledge_revision_id` | `Mapped[str &#124; None]` | `mapped_column(String(36))` |
| `current_evaluation_id` | `Mapped[str &#124; None]` | `mapped_column(String(36))` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('user_id', 'symbol', name='uq_case_user_symbol'),)
```

### ThesisDocument

Fuente: [finmate/state/models/thesis_inputs.py](../../../FinMate/finmate/state/models/thesis_inputs.py), línea 9. Bases: `Base`.

Tabla: `domain_thesis_documents`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True)` |
| `thesis_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_theses.id', ondelete='CASCADE'), index=True)` |
| `payload` | `Mapped[dict]` | `mapped_column(JSON)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

### CaseJob

Fuente: [finmate/state/models/thesis_inputs.py](../../../FinMate/finmate/state/models/thesis_inputs.py), línea 18. Bases: `Base`.

Tabla: `domain_case_jobs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `thesis_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_theses.id', ondelete='CASCADE'), index=True)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), index=True)` |
| `request_id` | `Mapped[str]` | `mapped_column(String(128))` |
| `request_hash` | `Mapped[str]` | `mapped_column(String(64))` |
| `status` | `Mapped[str]` | `mapped_column(String(30), default='running')` |
| `lease_token` | `Mapped[str &#124; None]` | `mapped_column(String(36))` |
| `lease_until` | `Mapped[datetime &#124; None]` | `mapped_column(DateTime(timezone=True))` |
| `payload` | `Mapped[dict]` | `mapped_column(JSON)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('user_id', 'request_id', name='uq_case_job_request'),)
```

### ThesisKnowledgeRevision

Fuente: [finmate/state/models/thesis_review.py](../../../FinMate/finmate/state/models/thesis_review.py), línea 8. Bases: `Base`.

Tabla: `domain_thesis_knowledge_revisions`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `thesis_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_theses.id', ondelete='CASCADE'), index=True)` |
| `sequence` | `Mapped[int]` | `mapped_column(Integer)` |
| `payload` | `Mapped[dict]` | `mapped_column(JSON)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('thesis_id', 'sequence'),)
```

### ThesisFinancialSnapshot

Fuente: [finmate/state/models/thesis_review.py](../../../FinMate/finmate/state/models/thesis_review.py), línea 17. Bases: `Base`.

Tabla: `domain_thesis_financial_snapshots`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `thesis_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_theses.id', ondelete='CASCADE'), index=True)` |
| `payload` | `Mapped[dict]` | `mapped_column(JSON)` |
| `provenance` | `Mapped[str]` | `mapped_column(String(500))` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

### ThesisEvaluation

Fuente: [finmate/state/models/thesis_review.py](../../../FinMate/finmate/state/models/thesis_review.py), línea 25. Bases: `Base`.

Tabla: `domain_thesis_evaluations`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `thesis_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_theses.id', ondelete='CASCADE'), index=True)` |
| `input_fingerprint` | `Mapped[str]` | `mapped_column(String(64))` |
| `payload` | `Mapped[dict]` | `mapped_column(JSON)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

### CaseAnalysisAssessment

Fuente: [finmate/state/models/thesis_review.py](../../../FinMate/finmate/state/models/thesis_review.py), línea 33. Bases: `Base`.

Tabla: `domain_case_analysis_assessments`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `thesis_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_theses.id', ondelete='CASCADE'), index=True)` |
| `job_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_case_jobs.id', ondelete='CASCADE'), index=True)` |
| `revision_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_thesis_knowledge_revisions.id', ondelete='CASCADE'))` |
| `objective_fingerprint` | `Mapped[str]` | `mapped_column(String(64))` |
| `payload` | `Mapped[dict]` | `mapped_column(JSON)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |

### User

Fuente: [finmate/state/models/user.py](../../../FinMate/finmate/state/models/user.py), línea 11. Bases: `Base`.

Tabla: `domain_users`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `external_id` | `Mapped[str &#124; None]` | `mapped_column(String(255), unique=True, index=True, nullable=True)` |
| `portfolio_name` | `Mapped[str]` | `mapped_column(String(120), nullable=False, default='Principal', server_default='Principal')` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |
| `positions` | `Mapped[list['Position']]` | `relationship(back_populates='user', cascade='all, delete-orphan')` |
| `watchlist_items` | `Mapped[list['WatchlistItem']]` | `relationship(back_populates='user', cascade='all, delete-orphan')` |
| `saved_screens` | `Mapped[list['SavedScreen']]` | `relationship(back_populates='user', cascade='all, delete-orphan')` |

### Position

Fuente: [finmate/state/models/user.py](../../../FinMate/finmate/state/models/user.py), línea 37. Bases: `Base`.

Tabla: `domain_positions`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `shares` | `Mapped[float]` | `mapped_column(Numeric(20, 6), nullable=False)` |
| `avg_cost` | `Mapped[float]` | `mapped_column(Numeric(20, 6), nullable=False)` |
| `opened_at` | `Mapped[date]` | `mapped_column(Date, nullable=False)` |
| `closed_at` | `Mapped[date &#124; None]` | `mapped_column(Date)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |
| `user` | `Mapped[User]` | `relationship(back_populates='positions')` |

### WatchlistItem

Fuente: [finmate/state/models/user.py](../../../FinMate/finmate/state/models/user.py), línea 57. Bases: `Base`.

Tabla: `domain_watchlist_items`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `user_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_users.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `symbol` | `Mapped[str]` | `mapped_column(String(20), nullable=False, index=True)` |
| `status` | `Mapped[str]` | `mapped_column(String(20), nullable=False, default='watching')` |
| `added_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `notes` | `Mapped[str &#124; None]` | `mapped_column(Text)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |
| `user` | `Mapped[User]` | `relationship(back_populates='watchlist_items')` |

Restricciones/índices declarados:

```python
(CheckConstraint("status IN ('watching', 'exploring', 'archived')", name='ck_domain_watchlist_items_status'),)
```

### Valuation

Fuente: [finmate/state/models/valuation.py](../../../FinMate/finmate/state/models/valuation.py), línea 11. Bases: `Base`.

Tabla: `domain_valuations`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `Mapped[str]` | `mapped_column(String(36), primary_key=True, default=uuid)` |
| `thesis_id` | `Mapped[str]` | `mapped_column(ForeignKey('domain_theses.id', ondelete='CASCADE'), nullable=False, index=True)` |
| `method` | `Mapped[str]` | `mapped_column(String(20), nullable=False)` |
| `intrinsic_value_low` | `Mapped[float]` | `mapped_column(Numeric(20, 6), nullable=False)` |
| `intrinsic_value_high` | `Mapped[float]` | `mapped_column(Numeric(20, 6), nullable=False)` |
| `currency` | `Mapped[str]` | `mapped_column(String(10), nullable=False)` |
| `base_date` | `Mapped[date]` | `mapped_column(Date, nullable=False)` |
| `assumptions` | `Mapped[dict]` | `mapped_column(JSON, nullable=False, default=dict)` |
| `created_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow)` |
| `updated_at` | `Mapped[datetime]` | `mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)` |

Restricciones/índices declarados:

```python
(CheckConstraint("method IN ('dcf', 'comparables', 'sum_of_parts')", name='ck_domain_valuations_method'),)
```

## 2. Modelos financieros v2

### Instrument

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 26. Bases: `Base`.

Tabla: `instruments`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `status` | `según declaración SQL` | `Column(String(16), nullable=False, default='pending', index=True)` |
| `tracked_at` | `según declaración SQL` | `Column(DateTime(timezone=True), nullable=False, default=_utcnow)` |
| `last_observed_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |

### InstrumentObservation

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 35. Bases: `Base`.

Tabla: `instrument_observations`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `según declaración SQL` | `Column(BigInteger, primary_key=True, autoincrement=True)` |
| `provider` | `según declaración SQL` | `Column(String(32), nullable=False)` |
| `symbol` | `según declaración SQL` | `Column(String(32), nullable=False, index=True)` |
| `name` | `según declaración SQL` | `Column(String)` |
| `description` | `según declaración SQL` | `Column(Text)` |
| `exchange` | `según declaración SQL` | `Column(String)` |
| `currency` | `según declaración SQL` | `Column(String)` |
| `country` | `según declaración SQL` | `Column(String)` |
| `sector` | `según declaración SQL` | `Column(String, index=True)` |
| `industry` | `según declaración SQL` | `Column(String)` |
| `market_capitalization` | `según declaración SQL` | `Column(BigInteger)` |
| `shares_outstanding` | `según declaración SQL` | `Column(BigInteger)` |
| `beta` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `pe_ratio` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `forward_pe` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `eps` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `profit_margin` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `return_on_equity_ttm` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `ev_to_ebitda` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `peg` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `quarterly_earnings_growth_yoy` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `quarterly_revenue_growth_yoy` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `provider_published_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |
| `ingested_at` | `según declaración SQL` | `Column(DateTime(timezone=True), nullable=False, default=_utcnow)` |
| `payload_hash` | `según declaración SQL` | `Column(String(64), nullable=False)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('provider', 'symbol', 'payload_hash', name='uq_instrument_observation_payload'),)
```

### PriceBar

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 69. Bases: `Base`.

Tabla: `price_bars`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `provider` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `symbol` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `trade_date` | `según declaración SQL` | `Column(Date, primary_key=True, index=True)` |
| `open_price` | `según declaración SQL` | `Column(Numeric)` |
| `high_price` | `según declaración SQL` | `Column(Numeric)` |
| `low_price` | `según declaración SQL` | `Column(Numeric)` |
| `close_price` | `según declaración SQL` | `Column(Numeric)` |
| `volume` | `según declaración SQL` | `Column(BigInteger)` |
| `provider_published_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |
| `ingested_at` | `según declaración SQL` | `Column(DateTime(timezone=True), nullable=False, default=_utcnow)` |
| `payload_hash` | `según declaración SQL` | `Column(String(64), nullable=False)` |

### FinancialFact

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 85. Bases: `Base`.

Tabla: `financial_facts`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `provider` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `symbol` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `fiscal_period` | `según declaración SQL` | `Column(Date, primary_key=True)` |
| `period_type` | `según declaración SQL` | `Column(String(16), primary_key=True)` |
| `item` | `según declaración SQL` | `Column(String(64), primary_key=True)` |
| `value` | `según declaración SQL` | `Column(Numeric)` |
| `currency` | `según declaración SQL` | `Column(String(8))` |
| `provider_published_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |
| `ingested_at` | `según declaración SQL` | `Column(DateTime(timezone=True), nullable=False, default=_utcnow)` |
| `payload_hash` | `según declaración SQL` | `Column(String(64), nullable=False)` |

### MacroObservation

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 100. Bases: `Base`.

Tabla: `macro_observations`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `provider` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `series` | `según declaración SQL` | `Column(String(64), primary_key=True)` |
| `observation_date` | `según declaración SQL` | `Column(Date, primary_key=True)` |
| `value` | `según declaración SQL` | `Column(Numeric, nullable=False)` |
| `provider_published_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |
| `ingested_at` | `según declaración SQL` | `Column(DateTime(timezone=True), nullable=False, default=_utcnow)` |
| `payload_hash` | `según declaración SQL` | `Column(String(64), nullable=False)` |

### _DerivedColumns

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 112. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `formula_version` | `según declaración SQL` | `Column(String(32), nullable=False)` |
| `derived_at` | `según declaración SQL` | `Column(DateTime(timezone=True), nullable=False)` |
| `source_max_ingested_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |
| `batch_id` | `según declaración SQL` | `Column(String(36), nullable=False, index=True)` |

### CompanyProfile

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 119. Bases: `_DerivedColumns`, `Base`.

Tabla: `company_profiles`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `name` | `según declaración SQL` | `Column(String)` |
| `description` | `según declaración SQL` | `Column(Text)` |
| `exchange` | `según declaración SQL` | `Column(String)` |
| `currency` | `según declaración SQL` | `Column(String)` |
| `country` | `según declaración SQL` | `Column(String)` |
| `sector` | `según declaración SQL` | `Column(String, index=True)` |
| `industry` | `según declaración SQL` | `Column(String)` |
| `market_capitalization` | `según declaración SQL` | `Column(BigInteger, index=True)` |
| `shares_outstanding` | `según declaración SQL` | `Column(BigInteger)` |
| `beta` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `pe_ratio` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `forward_pe` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `eps` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `profit_margin` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `return_on_equity_ttm` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `ev_to_ebitda` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `peg` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `quarterly_earnings_growth_yoy` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `quarterly_revenue_growth_yoy` | `según declaración SQL` | `Column(Numeric(20, 8))` |
| `source_provider` | `según declaración SQL` | `Column(String(32), nullable=False)` |

### FundamentalsPeriod

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 145. Bases: `_DerivedColumns`, `Base`.

Tabla: `fundamentals_periods`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `fiscal_period` | `según declaración SQL` | `Column(Date, primary_key=True)` |
| `period_type` | `según declaración SQL` | `Column(String(16), primary_key=True)` |
| `currency` | `según declaración SQL` | `Column(String(8))` |
| `total_revenue` | `según declaración SQL` | `Column(Numeric)` |
| `gross_profit` | `según declaración SQL` | `Column(Numeric)` |
| `operating_income` | `según declaración SQL` | `Column(Numeric)` |
| `net_income` | `según declaración SQL` | `Column(Numeric)` |
| `ebitda` | `según declaración SQL` | `Column(Numeric)` |
| `interest_expense` | `según declaración SQL` | `Column(Numeric)` |
| `income_before_tax` | `según declaración SQL` | `Column(Numeric)` |
| `income_tax_expense` | `según declaración SQL` | `Column(Numeric)` |
| `total_assets` | `según declaración SQL` | `Column(Numeric)` |
| `total_liabilities` | `según declaración SQL` | `Column(Numeric)` |
| `total_shareholder_equity` | `según declaración SQL` | `Column(Numeric)` |
| `total_debt` | `según declaración SQL` | `Column(Numeric)` |
| `cash_and_short_term_investments` | `según declaración SQL` | `Column(Numeric)` |
| `operating_cashflow` | `según declaración SQL` | `Column(Numeric)` |
| `capital_expenditures` | `según declaración SQL` | `Column(Numeric)` |
| `free_cash_flow` | `según declaración SQL` | `Column(Numeric)` |
| `dividends_paid` | `según declaración SQL` | `Column(Numeric)` |
| `gross_margin` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `operating_margin` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `net_margin` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `rev_cagr_3y` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `fcf_margin` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `debt_to_equity` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `roe_std_5y` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `accruals_ratio` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `op_margin_std_5y` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `fcf_div_cover` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `effective_tax_rate` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `normalized_fcff` | `según declaración SQL` | `Column(Numeric)` |

### SymbolMetric

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 183. Bases: `_DerivedColumns`, `Base`.

Tabla: `symbol_metrics_v2`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `market_as_of` | `según declaración SQL` | `Column(Date)` |
| `fundamentals_as_of` | `según declaración SQL` | `Column(Date)` |
| `return_on_equity_ttm` | `según declaración SQL` | `Column(Numeric(24, 10), index=True)` |
| `fcf_margin` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `debt_to_equity` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `accruals_ratio` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `op_margin_std_5y` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `roe_std_5y` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `fcf_div_cover` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `rev_cagr_3y` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `yoy_growth_pct` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `eps_yoy_growth` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `effective_pe` | `según declaración SQL` | `Column(Numeric(24, 10), index=True)` |
| `pe_pctl_in_sector` | `según declaración SQL` | `Column(Numeric(24, 10), index=True)` |
| `above_200d` | `según declaración SQL` | `Column(Boolean)` |
| `above_50d` | `según declaración SQL` | `Column(Boolean)` |
| `mom_12_1` | `según declaración SQL` | `Column(Numeric(24, 10), index=True)` |
| `sharpe` | `según declaración SQL` | `Column(Numeric(24, 10), index=True)` |
| `max_drawdown` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `dist_to_52w_high` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `return_1m` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `return_3m` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `return_12m` | `según declaración SQL` | `Column(Numeric(24, 10))` |

### SymbolCoverage

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 212. Bases: `_DerivedColumns`, `Base`.

Tabla: `symbol_coverage`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `según declaración SQL` | `Column(String(32), primary_key=True)` |
| `has_profile` | `según declaración SQL` | `Column(Boolean, nullable=False, default=False)` |
| `has_prices` | `según declaración SQL` | `Column(Boolean, nullable=False, default=False)` |
| `has_income` | `según declaración SQL` | `Column(Boolean, nullable=False, default=False)` |
| `has_balance` | `según declaración SQL` | `Column(Boolean, nullable=False, default=False)` |
| `has_cashflow` | `según declaración SQL` | `Column(Boolean, nullable=False, default=False)` |
| `first_price_date` | `según declaración SQL` | `Column(Date)` |
| `last_price_date` | `según declaración SQL` | `Column(Date, index=True)` |
| `latest_close` | `según declaración SQL` | `Column(Numeric)` |
| `latest_fiscal_period` | `según declaración SQL` | `Column(Date)` |
| `aligned_period_count` | `según declaración SQL` | `Column(Integer, nullable=False, default=0)` |
| `dcf_ready` | `según declaración SQL` | `Column(Boolean, nullable=False, default=False)` |

### SectorStat

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 229. Bases: `_DerivedColumns`, `Base`.

Tabla: `sector_stats`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `sector` | `según declaración SQL` | `Column(String, primary_key=True)` |
| `metric` | `según declaración SQL` | `Column(String(64), primary_key=True)` |
| `sample_count` | `según declaración SQL` | `Column(Integer, nullable=False)` |
| `median` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `q1` | `según declaración SQL` | `Column(Numeric(24, 10))` |
| `q3` | `según declaración SQL` | `Column(Numeric(24, 10))` |

### BenchmarkIndexDaily

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 240. Bases: `_DerivedColumns`, `Base`.

Tabla: `benchmark_index_daily`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `trade_date` | `según declaración SQL` | `Column(Date, primary_key=True)` |
| `level` | `según declaración SQL` | `Column(Numeric(24, 10), nullable=False)` |
| `constituent_count` | `según declaración SQL` | `Column(Integer, nullable=False)` |

### MacroLatest

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 248. Bases: `_DerivedColumns`, `Base`.

Tabla: `macro_latest`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `series` | `según declaración SQL` | `Column(String(64), primary_key=True)` |
| `observation_date` | `según declaración SQL` | `Column(Date, nullable=False)` |
| `value` | `según declaración SQL` | `Column(Numeric, nullable=False)` |
| `provider` | `según declaración SQL` | `Column(String(32), nullable=False)` |

### DerivationQueue

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 257. Bases: `Base`.

Tabla: `derivation_queue`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `según declaración SQL` | `Column(BigInteger, primary_key=True, autoincrement=True)` |
| `scope` | `según declaración SQL` | `Column(String(16), nullable=False)` |
| `key` | `según declaración SQL` | `Column(String(64), nullable=False)` |
| `reasons` | `según declaración SQL` | `Column(JSON, nullable=False, default=list)` |
| `dirty_from` | `según declaración SQL` | `Column(Date)` |
| `enqueued_at` | `según declaración SQL` | `Column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)` |
| `attempts` | `según declaración SQL` | `Column(Integer, nullable=False, default=0)` |
| `last_error` | `según declaración SQL` | `Column(Text)` |

Restricciones/índices declarados:

```python
(UniqueConstraint('scope', 'key', name='uq_derivation_queue_scope_key'),)
```

### DerivationState

Fuente: [findata/models/v2.py](../../../FinMate/findata/models/v2.py), línea 272. Bases: `Base`.

Tabla: `derivation_state`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `dataset` | `según declaración SQL` | `Column(String(64), primary_key=True)` |
| `formula_version` | `según declaración SQL` | `Column(String(32), nullable=False)` |
| `batch_id` | `según declaración SQL` | `Column(String(36))` |
| `source_max_ingested_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |
| `completed_at` | `según declaración SQL` | `Column(DateTime(timezone=True))` |
| `status` | `según declaración SQL` | `Column(String(16), nullable=False, default='empty')` |
| `detail` | `según declaración SQL` | `Column(JSON, nullable=False, default=dict)` |

## 3. Contratos conceptuales del expediente

### Argument

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 23. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `Field(min_length=1)` |
| `explanation` | `str` | `Field(min_length=1)` |
| `relevance` | `str` | `Field(min_length=1)` |
| `relation` | `Literal['supports', 'questions']` | `sin valor declarado` |
| `evidence_refs` | `tuple[str, ...]` | `()` |
| `argument_refs` | `tuple[str, ...]` | `()` |

### Question

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 32. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `text` | `str` | `Field(min_length=1)` |
| `decisive` | `bool` | `sin valor declarado` |
| `status` | `Literal['open', 'answered', 'unanswerable']` | `'open'` |
| `explanation` | `str` | `''` |
| `argument_refs` | `tuple[str, ...]` | `()` |

### Hypothesis

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 41. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `Field(min_length=1)` |
| `statement` | `str` | `Field(min_length=1)` |
| `status` | `Literal['supported', 'questioned', 'uncertain']` | `sin valor declarado` |
| `explanation` | `str` | `Field(min_length=1)` |
| `arguments` | `tuple[Argument, ...]` | `()` |
| `questions` | `tuple[Question, ...]` | `()` |
| `consequences` | `str` | `''` |
| `antecedents` | `tuple[str, ...]` | `()` |
| `retired` | `bool` | `False` |

### ReasoningTarget

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 53. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `kind` | `Literal['hypothesis', 'premise', 'inference']` | `sin valor declarado` |
| `id` | `str` | `Field(min_length=1, description='Hypothesis ID for hypothesis; owning structured argument ID for inference or premise. Never a premise ID.')` |
| `premise_id` | `str &#124; None` | `Field(default=None, description='Local premise ID inside the argument identified by id; required only for kind=premise.')` |

Validadores declarados: `part`.

### Premise

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 65. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `Field(min_length=1)` |
| `statement` | `str` | `Field(min_length=1)` |
| `evidence_refs` | `tuple[str, ...]` | `()` |
| `hypothesis_id` | `str &#124; None` | `Field(default=None, description="Null for evidence or assumption premises. Only set when using another argument's shared conclusion.")` |
| `argument_refs` | `tuple[str, ...]` | `Field(default=(), description='Selected arguments concluding hypothesis_id; empty when hypothesis_id is null. Never the argument containing this premise.')` |
| `assumption` | `str &#124; None` | `Field(default=None, min_length=1)` |
| `antecedents` | `tuple[str, ...]` | `()` |

Validadores declarados: `foundation`.

### HistoricalArgumentReference

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 83. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `revision_id` | `str` | `Field(min_length=1)` |
| `argument_id` | `str` | `Field(min_length=1)` |

### StructuredArgument

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 88. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `Field(min_length=1)` |
| `premises` | `tuple[Premise, ...]` | `Field(min_length=1)` |
| `inference` | `str` | `Field(min_length=1)` |
| `conclusion` | `str` | `Field(min_length=1)` |
| `hypothesis_id` | `str &#124; None` | `None` |
| `relevance` | `str` | `Field(min_length=1)` |
| `antecedents` | `tuple[str, ...]` | `()` |
| `retired` | `bool` | `False` |
| `historical_refs` | `tuple[HistoricalArgumentReference, ...]` | `()` |

### DebateRelation

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 100. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `Field(min_length=1)` |
| `source_argument_id` | `str` | `Field(min_length=1)` |
| `target` | `ReasoningTarget` | `sin valor declarado` |
| `relation` | `Literal['supports', 'questions']` | `sin valor declarado` |
| `explanation` | `str` | `Field(min_length=1)` |
| `material` | `bool` | `True` |
| `antecedents` | `tuple[str, ...]` | `()` |
| `retired` | `bool` | `False` |

### ObjectionTreatment

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 111. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `relation_id` | `str` | `Field(min_length=1)` |
| `status` | `Literal['open', 'addressed', 'accepted_limit']` | `sin valor declarado` |
| `explanation` | `str` | `Field(min_length=1)` |
| `effect` | `str` | `Field(min_length=1)` |
| `evidence_refs` | `tuple[str, ...]` | `()` |
| `argument_refs` | `tuple[str, ...]` | `()` |

Validadores declarados: `addressed_basis`.

### Conditions

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 126. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `horizon_years` | `int` | `Field(ge=1, le=30)` |
| `required_valuation_upside` | `float &#124; None` | `Field(default=None, ge=0, le=5)` |
| `price` | `float &#124; None` | `Field(default=None, gt=0)` |
| `price_as_of` | `datetime &#124; None` | `None` |
| `currency` | `str &#124; None` | `None` |

Validadores declarados: `price_context`.

### Assumption

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 142. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `parameter` | `Literal['initial_revenue_growth', 'decay_rate', 'target_fcff_margin', 'terminal_growth']` | `sin valor declarado` |
| `value` | `float` | `sin valor declarado` |
| `explanation` | `str` | `Field(min_length=1)` |
| `hypothesis_refs` | `tuple[str, ...]` | `()` |
| `argument_refs` | `tuple[str, ...]` | `()` |
| `evidence_refs` | `tuple[str, ...]` | `()` |
| `kind` | `Literal['supported', 'exploratory']` | `sin valor declarado` |

### Scenario

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 152. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `name` | `str` | `Field(min_length=1)` |
| `explanation` | `str` | `Field(min_length=1)` |
| `assumptions` | `tuple[Assumption, ...]` | `sin valor declarado` |

Validadores declarados: `parameters`.

### Revision

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 165. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `reasoning_version` | `Literal['argumentation-v1'] &#124; None` | `None` |
| `arguments` | `tuple[StructuredArgument, ...]` | `()` |
| `relations` | `tuple[DebateRelation, ...]` | `()` |
| `numeric_evidence_refs` | `tuple[str, ...]` | `()` |
| `hypotheses` | `tuple[Hypothesis, ...]` | `()` |
| `conditions` | `Conditions &#124; None` | `None` |
| `scenarios` | `tuple[Scenario, ...]` | `()` |
| `change` | `str` | `Field(min_length=1)` |
| `review_conditions` | `tuple[str, ...]` | `()` |
| `financial_snapshot_id` | `str &#124; None` | `None` |
| `valid_until` | `datetime &#124; None` | `None` |

Validadores declarados: `graph`.

### Observation

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 221. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `text` | `str` | `''` |
| `document_id` | `str` | `sin valor declarado` |
| `fragment_id` | `str` | `sin valor declarado` |
| `quote` | `str` | `Field(min_length=1)` |
| `period` | `str &#124; None` | `None` |

### AnalysisGap

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 230. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `Field(min_length=1)` |
| `question_id` | `str &#124; None` | `None` |
| `hypothesis_refs` | `tuple[str, ...]` | `()` |
| `argument_refs` | `tuple[str, ...]` | `()` |
| `materiality` | `str` | `Field(min_length=1)` |
| `limited_conclusion` | `str` | `Field(min_length=1)` |
| `resolution` | `Literal['research', 'calculation', 'user', 'declare']` | `sin valor declarado` |
| `acceptance` | `str` | `Field(min_length=1)` |
| `blocking` | `bool` | `False` |

### Finding

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 242. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `conclusion` | `str` | `Field(min_length=1)` |
| `evidence_refs` | `tuple[str, ...]` | `Field(min_length=1)` |
| `argument_refs` | `tuple[str, ...]` | `()` |
| `hypothesis_refs` | `tuple[str, ...]` | `()` |

### ActionArguments

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 249. Bases: `Contract`.

Shared financial choice; execution identity is supplied by the server.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `step` | `Literal['collect', 'interpret', 'research', 'read_candidate', 'value', 'publish', 'close']` | `sin valor declarado` |
| `question_id` | `str &#124; None` | `None` |
| `gap_id` | `str &#124; None` | `None` |
| `reasoning_target` | `ReasoningTarget &#124; None` | `None` |
| `target_revision` | `int &#124; None` | `Field(default=None, ge=0)` |
| `query` | `str &#124; None` | `None` |
| `research_question` | `str &#124; None` | `None` |
| `rationale` | `str` | `Field(min_length=1)` |
| `expected_contribution` | `str` | `Field(min_length=1)` |
| `scenarios` | `tuple[Scenario, ...]` | `()` |
| `stop_reason` | `Literal['objective_resolved', 'no_information', 'irreducible_uncertainty', 'user_input', 'budget', 'no_progress'] &#124; None` | `None` |

### NextAction

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 264. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `operator_id` | `Literal['case_step', 'valuation_dcf']` | `sin valor declarado` |
| `arguments` | `ActionArguments` | `sin valor declarado` |

Validadores declarados: `capability`.

### Continuation

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 275. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `question` | `str` | `Field(min_length=1)` |
| `rationale` | `str` | `Field(min_length=1)` |
| `completion_condition` | `str` | `Field(min_length=1)` |
| `requires_dcf` | `bool` | `False` |

### ProblemConsideration

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 282. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `statement` | `str` | `Field(min_length=1)` |
| `kind` | `Literal['supported', 'assumption', 'uncertainty']` | `sin valor declarado` |
| `financial_consequence` | `str` | `Field(min_length=1)` |
| `evidence_refs` | `tuple[str, ...]` | `()` |
| `hypothesis_refs` | `tuple[str, ...]` | `()` |
| `argument_refs` | `tuple[str, ...]` | `()` |

Validadores declarados: `support`.

### ProblemFraming

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 297. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `contract_version` | `Literal['problem-framing-v1']` | `'problem-framing-v1'` |
| `objective` | `str` | `Field(min_length=1)` |
| `economic_relevance` | `str` | `Field(min_length=1)` |
| `considerations` | `tuple[ProblemConsideration, ...]` | `Field(default=(), max_length=4)` |
| `priority_question` | `str &#124; None` | `Field(default=None, min_length=1)` |
| `revision_reason` | `str` | `Field(min_length=1)` |

### AnalysisAssessment

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 306. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `problem_framing` | `ProblemFraming &#124; None` | `None` |
| `objections` | `tuple[ObjectionTreatment, ...]` | `()` |
| `continuation` | `Continuation &#124; None` | `None` |
| `answer` | `str` | `Field(min_length=1)` |
| `status` | `Literal['grounded', 'conditional', 'insufficient']` | `sin valor declarado` |
| `objective_resolved` | `bool` | `sin valor declarado` |
| `gaps` | `tuple[AnalysisGap, ...]` | `()` |
| `limitations` | `tuple[str, ...]` | `()` |
| `next_step` | `str` | `Field(min_length=1)` |
| `findings` | `tuple[Finding, ...]` | `()` |
| `key_data_refs` | `tuple[str, ...]` | `()` |
| `evaluation_relation` | `Literal['not_addressed', 'consistent', 'review_suggested', 'reevaluation_required']` | `'not_addressed'` |
| `next_action` | `NextAction &#124; None` | `None` |
| `dcf_impediment` | `str &#124; None` | `Field(default=None, min_length=1)` |

### Analysis

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 323. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `revision` | `Revision` | `sin valor declarado` |
| `observations` | `tuple[Observation, ...]` | `()` |
| `next_question_id` | `str &#124; None` | `None` |
| `stop_reason` | `Literal['sufficient', 'no_information', 'user_input', 'budget', 'investigate']` | `sin valor declarado` |
| `assessment` | `AnalysisAssessment &#124; None` | `None` |

### Synthesis

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 331. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `contract_version` | `Literal['case-synthesis-v3', 'case-synthesis-v4']` | `'case-synthesis-v4'` |
| `argument_refs` | `tuple[str, ...]` | `()` |
| `relation_refs` | `tuple[str, ...]` | `()` |
| `conclusion_status` | `Literal['grounded', 'conditional', 'insufficient'] &#124; None` | `None` |
| `evidence_refs` | `tuple[str, ...]` | `()` |
| `continuation` | `Continuation &#124; None` | `None` |
| `direction` | `Literal['long', 'neutral'] &#124; None` | `sin valor declarado` |
| `judgment_status` | `Literal['grounded', 'insufficient']` | `sin valor declarado` |
| `summary` | `str` | `Field(min_length=1)` |
| `favorable` | `tuple[str, ...]` | `sin valor declarado` |
| `contrary` | `tuple[str, ...]` | `sin valor declarado` |
| `uncertainties` | `tuple[str, ...]` | `sin valor declarado` |
| `hypothesis_refs` | `tuple[str, ...]` | `sin valor declarado` |
| `next_step` | `str` | `sin valor declarado` |

Validadores declarados: `computed_numbers_are_rendered_by_code`.

### CaseRequest

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 355. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `continuation_from_job_id` | `str &#124; None` | `None` |
| `symbol` | `str` | `sin valor declarado` |
| `mode` | `Literal['analyze', 'investigate', 'update']` | `'analyze'` |
| `question` | `str` | `Field(default='Examinar los fundamentos materiales y determinar qué conclusión permiten sostener.', min_length=1)` |
| `orientation` | `str &#124; None` | `None` |
| `restrictions` | `tuple[Literal['no_valuation', 'no_external_research'], ...]` | `()` |
| `completion_condition` | `str &#124; None` | `None` |
| `question_id` | `str &#124; None` | `None` |
| `conditions` | `Conditions &#124; None` | `None` |
| `expected_input_revision` | `int` | `Field(ge=0)` |
| `document_urls` | `tuple[str, ...]` | `Field(default=(), max_length=3)` |
| `event_ids` | `tuple[str, ...]` | `()` |
| `request_id` | `str` | `Field(min_length=1, max_length=128)` |
| `price_only` | `bool` | `False` |
| `requires_evaluation` | `bool &#124; None` | `None` |
| `requires_dcf` | `bool` | `False` |

Validadores declarados: `price_update`, `normalize`.

### CaseTaskArgs

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 391. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `command` | `CaseRequest &#124; None` | `None` |
| `job_id` | `str &#124; None` | `None` |

Validadores declarados: `bound_work`.

### StepArgs

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 405. Bases: `CaseTaskArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `step` | `Literal['reserve', 'budget', 'plan_budget', 'settle', 'collect', 'interpret', 'research', 'read_candidate', 'value', 'publish', 'close', 'interrupt', 'fail']` | `sin valor declarado` |
| `failure` | `str &#124; None` | `None` |
| `checkpoint` | `str &#124; None` | `None` |
| `question_id` | `str &#124; None` | `None` |
| `gap_id` | `str &#124; None` | `None` |
| `reasoning_target` | `ReasoningTarget &#124; None` | `None` |
| `target_revision` | `int &#124; None` | `Field(default=None, ge=0)` |
| `query` | `str &#124; None` | `None` |
| `research_question` | `str &#124; None` | `None` |
| `reference_warnings` | `tuple[str, ...]` | `()` |
| `rationale` | `str &#124; None` | `None` |
| `expected_contribution` | `str &#124; None` | `None` |
| `scenarios` | `tuple[Scenario, ...]` | `()` |
| `selected_action` | `dict[str, object] &#124; None` | `None` |
| `stop_reason` | `Literal['objective_resolved', 'no_information', 'irreducible_uncertainty', 'user_input', 'budget', 'no_progress', 'operational_failure', 'planner_stopped'] &#124; None` | `None` |

### ValuationStepArgs

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 423. Bases: `StepArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `step` | `Literal['value']` | `'value'` |

### PlanningStepArgs

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 427. Bases: `ActionArguments`.

Public planner actions omit application-owned reservation payloads.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `job_id` | `str` | `sin valor declarado` |
| `checkpoint` | `str` | `sin valor declarado` |

### PlanningValuationArgs

Fuente: [finmate/casefile/contracts.py](../../../FinMate/finmate/casefile/contracts.py), línea 434. Bases: `PlanningStepArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `step` | `Literal['value']` | `'value'` |

## 4. Operaciones tipadas de interpretación

### AddHypothesis

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 10. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['add_hypothesis']` | `sin valor declarado` |
| `hypothesis` | `Hypothesis` | `sin valor declarado` |

### UpdateHypothesis

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 15. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['update_hypothesis']` | `sin valor declarado` |
| `id` | `str` | `sin valor declarado` |
| `status` | `Literal['supported', 'questioned', 'uncertain']` | `sin valor declarado` |
| `explanation` | `str` | `Field(min_length=1)` |
| `consequences` | `str` | `sin valor declarado` |

### RetireHypothesis

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 23. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['retire_hypothesis']` | `sin valor declarado` |
| `id` | `str` | `sin valor declarado` |

### ReplaceHypothesis

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 28. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['replace_hypothesis']` | `sin valor declarado` |
| `id` | `str` | `sin valor declarado` |
| `hypothesis` | `Hypothesis` | `sin valor declarado` |

### PutArgument

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 34. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['add_argument', 'update_argument']` | `sin valor declarado` |
| `hypothesis_id` | `str` | `sin valor declarado` |
| `argument` | `Argument` | `sin valor declarado` |

### PutQuestion

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 40. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['add_question', 'update_question']` | `sin valor declarado` |
| `hypothesis_id` | `str` | `sin valor declarado` |
| `question` | `Question` | `sin valor declarado` |

### ReplaceScenarios

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 46. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['replace_scenarios']` | `sin valor declarado` |
| `scenarios` | `tuple[Scenario, ...]` | `sin valor declarado` |

### ReplaceReviewConditions

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 51. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['replace_review_conditions']` | `sin valor declarado` |
| `review_conditions` | `tuple[str, ...]` | `sin valor declarado` |

### PutStructuredArgument

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 56. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['add_structured_argument', 'replace_structured_argument']` | `sin valor declarado` |
| `argument` | `StructuredArgument` | `sin valor declarado` |
| `replaces` | `str &#124; None` | `None` |

### PutRelation

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 62. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['add_relation', 'replace_relation']` | `sin valor declarado` |
| `relation` | `DebateRelation` | `sin valor declarado` |
| `replaces` | `str &#124; None` | `None` |

### RetireReasoning

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 68. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['retire_structured_argument', 'retire_relation']` | `sin valor declarado` |
| `id` | `str` | `sin valor declarado` |

### ReorderPremises

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 73. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `op` | `Literal['reorder_premises']` | `sin valor declarado` |
| `id` | `str` | `sin valor declarado` |
| `premise_ids` | `tuple[str, ...]` | `sin valor declarado` |

### AnalysisChanges

Fuente: [finmate/casefile/changes.py](../../../FinMate/finmate/casefile/changes.py), línea 79. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `operations` | `tuple[AddHypothesis &#124; UpdateHypothesis &#124; RetireHypothesis &#124; ReplaceHypothesis &#124; PutArgument &#124; PutQuestion &#124; ReplaceScenarios &#124; ReplaceReviewConditions &#124; PutStructuredArgument &#124; PutRelation &#124; RetireReasoning &#124; ReorderPremises, ...]` | `()` |
| `change` | `str` | `Field(min_length=1)` |
| `observations` | `tuple[Observation, ...]` | `()` |
| `next_question_id` | `str &#124; None` | `None` |
| `stop_reason` | `Literal['sufficient', 'no_information', 'user_input', 'budget', 'investigate']` | `sin valor declarado` |
| `assessment` | `AnalysisAssessment` | `sin valor declarado` |

Validadores declarados: `typed_operations`.

## 5. Cifras privadas y procedencia

### NumericObservation

Fuente: [finmate/casefile/numbers.py](../../../FinMate/finmate/casefile/numbers.py), línea 10. Bases: `Contract`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `kind` | `Literal['financial_observation']` | `'financial_observation'` |
| `version` | `Literal[1]` | `1` |
| `symbol` | `str` | `sin valor declarado` |
| `metric` | `str` | `sin valor declarado` |
| `definition` | `str` | `sin valor declarado` |
| `value` | `float` | `sin valor declarado` |
| `unit` | `Literal['currency', 'currency_per_share', 'percent', 'percentage_points']` | `sin valor declarado` |
| `scale` | `Literal[1]` | `1` |
| `currency` | `str &#124; None` | `sin valor declarado` |
| `period` | `date` | `sin valor declarado` |
| `period_type` | `Literal['annual', 'quarterly', 'instant']` | `sin valor declarado` |
| `scope` | `Literal['consolidated']` | `'consolidated'` |
| `nature` | `Literal['observed', 'calculated']` | `'observed'` |
| `source_ref` | `str` | `sin valor declarado` |
| `provenance` | `dict[str, Any]` | `sin valor declarado` |
| `published_at` | `datetime &#124; None` | `None` |
| `retrieved_at` | `datetime` | `sin valor declarado` |
| `formula_version` | `str &#124; None` | `None` |
| `input_refs` | `tuple[str, ...]` | `()` |

Validadores declarados: `reproducible`.

## 6. Documentos y fragmentos

### Fragment

Fuente: [runtime_contracts/documents.py](../../../FinMate/runtime_contracts/documents.py), línea 10. Bases: `BaseModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `text` | `str` | `Field(min_length=1)` |
| `location` | `str` | `sin valor declarado` |

### DocumentSnapshot

Fuente: [runtime_contracts/documents.py](../../../FinMate/runtime_contracts/documents.py), línea 17. Bases: `BaseModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `Field(default_factory=lambda: str(uuid4()))` |
| `requested_url` | `str` | `sin valor declarado` |
| `final_url` | `str` | `sin valor declarado` |
| `retrieved_at` | `datetime` | `sin valor declarado` |
| `published_at` | `datetime &#124; None` | `None` |
| `content_hash` | `str` | `sin valor declarado` |
| `extractor_version` | `str` | `'html-blocks-v1'` |
| `title` | `str` | `sin valor declarado` |
| `html` | `str` | `sin valor declarado` |
| `raw_content` | `str &#124; None` | `None` |
| `extraction_metadata` | `dict[str, Any] &#124; None` | `None` |
| `fragments` | `tuple[Fragment, ...]` | `sin valor declarado` |

## 7. Perfil y objetivos

### ProfileFactInput

Fuente: [finmate/profile/contracts.py](../../../FinMate/finmate/profile/contracts.py), línea 33. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `key` | `ProfileFactKey` | `sin valor declarado` |
| `value` | `Any` | `sin valor declarado` |

Validadores declarados: `validate_value`.

### ProfileGoalInput

Fuente: [finmate/profile/contracts.py](../../../FinMate/finmate/profile/contracts.py), línea 44. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str &#124; None` | `None` |
| `kind` | `GoalKind` | `sin valor declarado` |
| `title` | `str` | `Field(min_length=1, max_length=160)` |
| `description` | `str &#124; None` | `Field(default=None, max_length=1000)` |
| `status` | `GoalStatus` | `'active'` |
| `priority` | `int &#124; None` | `Field(default=None, ge=1)` |
| `target_date` | `date &#124; None` | `None` |
| `target_amount` | `Decimal &#124; None` | `Field(default=None, gt=0)` |
| `currency` | `str &#124; None` | `None` |

Validadores declarados: `strip_text`, `normalize_currency`, `validate_goal`.

### ProfileUpdateArgs

Fuente: [finmate/profile/contracts.py](../../../FinMate/finmate/profile/contracts.py), línea 86. Bases: `OperatorArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `expected_revision` | `int` | `Field(ge=0)` |
| `request_id` | `str` | `Field(min_length=1, max_length=128)` |
| `request_hash` | `str` | `Field(min_length=64, max_length=64)` |
| `reset` | `bool` | `False` |
| `facts` | `tuple[ProfileFactInput, ...]` | `()` |
| `goals` | `tuple[ProfileGoalInput, ...]` | `()` |

Validadores declarados: `validate_snapshot`.

### FactSpec

Fuente: [finmate/profile/contracts.py](../../../FinMate/finmate/profile/contracts.py), línea 110. Bases: `BaseModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `key` | `ProfileFactKey` | `sin valor declarado` |
| `label` | `str` | `sin valor declarado` |
| `description` | `str` | `sin valor declarado` |
| `input_kind` | `Literal['single_choice', 'multi_choice', 'number']` | `sin valor declarado` |
| `options` | `tuple[tuple[str, str], ...]` | `()` |
| `minimum` | `float &#124; None` | `None` |
| `maximum` | `float &#124; None` | `None` |

## 8. Selección y comparación

### SelectionCriteriaV1

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 51. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `priority_dimensions` | `tuple[DimensionKey, ...]` | `Field(min_length=1, max_length=8)` |
| `notes` | `str &#124; None` | `Field(default=None, max_length=1000)` |

Validadores declarados: `unique_dimensions`.

### SelectionCreateArgs

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 61. Bases: `ClosedArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `title` | `str` | `Field(min_length=1, max_length=120)` |
| `purpose` | `str` | `Field(min_length=1, max_length=1000)` |
| `symbols` | `tuple[str, ...]` | `Field(min_length=2, max_length=5)` |
| `horizon` | `Literal['long']` | `'long'` |
| `criteria` | `SelectionCriteriaV1` | `sin valor declarado` |
| `request_id` | `str` | `Field(min_length=1, max_length=128)` |

Validadores declarados: `strip_text`, `symbols_are_unique`.

### SelectionUpdateArgs

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 81. Bases: `ClosedArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `selection_id` | `str` | `sin valor declarado` |
| `expected_revision` | `int` | `Field(ge=1)` |
| `title` | `str` | `Field(min_length=1, max_length=120)` |
| `purpose` | `str` | `Field(min_length=1, max_length=1000)` |
| `symbols` | `tuple[str, ...]` | `Field(min_length=2, max_length=5)` |
| `horizon` | `Literal['long']` | `'long'` |
| `criteria` | `SelectionCriteriaV1` | `sin valor declarado` |
| `status` | `Literal['active', 'archived']` | `sin valor declarado` |

Validadores declarados: `strip_text`, `symbols_are_unique`.

### SelectionCompareArgs

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 104. Bases: `ClosedArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `selection_id` | `str` | `sin valor declarado` |
| `expected_revision` | `int` | `Field(ge=1)` |
| `expected_sequence` | `int` | `Field(ge=0)` |

### SelectionDecideArgs

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 109. Bases: `ClosedArgs`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `selection_id` | `str` | `sin valor declarado` |
| `candidate_id` | `str` | `sin valor declarado` |
| `expected_decision_revision` | `int` | `Field(ge=0)` |
| `comparison_id` | `str &#124; None` | `None` |
| `decision` | `Literal['undecided', 'investigate', 'wait', 'discard', 'select']` | `sin valor declarado` |
| `reason` | `str` | `Field(min_length=1, max_length=500)` |
| `review_condition` | `str &#124; None` | `Field(default=None, max_length=500)` |
| `request_id` | `str` | `Field(min_length=1, max_length=128)` |
| `origin` | `Literal['ui', 'conversation']` | `sin valor declarado` |
| `interaction_ref` | `str &#124; None` | `Field(default=None, max_length=128)` |

Validadores declarados: `strip_reason`.

### CandidateAssessment

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 127. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `candidate_id` | `str` | `sin valor declarado` |
| `main_attraction` | `str` | `Field(max_length=COMPARISON_SUMMARY_MAX_LENGTH)` |
| `main_risk` | `str` | `Field(max_length=COMPARISON_SUMMARY_MAX_LENGTH)` |
| `fit_with_purpose` | `str` | `Field(max_length=COMPARISON_SUMMARY_MAX_LENGTH)` |
| `unresolved_questions` | `tuple[str, ...]` | `Field(max_length=COMPARISON_MAX_QUESTIONS)` |
| `source_refs` | `tuple[str, ...]` | `Field(max_length=COMPARISON_MAX_CANDIDATE_SOURCE_REFS)` |

Validadores declarados: `concise_summary`, `concise_questions`.

### MaterialDifference

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 145. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `candidate_ids` | `tuple[str, ...]` | `sin valor declarado` |
| `explanation` | `str` | `Field(max_length=COMPARISON_DIFFERENCE_MAX_LENGTH)` |
| `source_refs` | `tuple[str, ...]` | `Field(max_length=COMPARISON_MAX_DIFFERENCE_SOURCE_REFS)` |

Validadores declarados: `concise_explanation`.

### ComparisonConclusion

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 155. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `kind` | `Literal['preliminary_preference', 'insufficient_basis']` | `sin valor declarado` |
| `preferred_candidate_ids` | `tuple[str, ...]` | `sin valor declarado` |
| `explanation` | `str` | `Field(max_length=COMPARISON_CONCLUSION_MAX_LENGTH)` |
| `conditions` | `tuple[str, ...]` | `Field(max_length=COMPARISON_MAX_CONDITIONS)` |
| `source_refs` | `tuple[str, ...]` | `Field(max_length=COMPARISON_MAX_CONCLUSION_SOURCE_REFS)` |

Validadores declarados: `concise_explanation`, `concise_conditions`.

### SelectionComparisonResultV1

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 172. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `candidate_assessments` | `tuple[CandidateAssessment, ...]` | `sin valor declarado` |
| `material_differences` | `tuple[MaterialDifference, ...]` | `Field(max_length=COMPARISON_MAX_DIFFERENCES)` |
| `conclusion` | `ComparisonConclusion` | `sin valor declarado` |

### ReferencedFact

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 178. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `ref` | `str` | `sin valor declarado` |
| `kind` | `Literal['observed', 'calculated', 'referenced_evidence']` | `sin valor declarado` |
| `key` | `str` | `sin valor declarado` |
| `value` | `str &#124; int &#124; float &#124; bool &#124; None` | `sin valor declarado` |
| `unit` | `str &#124; None` | `None` |
| `period` | `str &#124; None` | `None` |
| `currency` | `str &#124; None` | `None` |
| `source` | `str &#124; None` | `None` |
| `source_ref` | `str &#124; None` | `None` |

### CoverageAssessment

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 190. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `status` | `Literal['complete', 'partial']` | `sin valor declarado` |
| `evaluability` | `Literal['usable', 'not_evaluable']` | `sin valor declarado` |
| `dimension_refs` | `dict[DimensionKey, tuple[str, ...]]` | `sin valor declarado` |

### FreshnessAssessment

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 196. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `market` | `Literal['current', 'dated', 'unknown']` | `sin valor declarado` |
| `fundamentals` | `Literal['current', 'dated', 'unknown']` | `sin valor declarado` |

### CandidateInputV1

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 201. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `candidate_id` | `str` | `sin valor declarado` |
| `symbol` | `str` | `sin valor declarado` |
| `ordinal` | `int` | `sin valor declarado` |
| `coverage` | `CoverageAssessment` | `sin valor declarado` |
| `analysis_id` | `str &#124; None` | `sin valor declarado` |
| `catalog_version` | `str &#124; None` | `sin valor declarado` |
| `market_as_of` | `date &#124; None` | `sin valor declarado` |
| `fundamentals_as_of` | `date &#124; None` | `sin valor declarado` |
| `freshness` | `FreshnessAssessment` | `sin valor declarado` |
| `formula_version` | `str &#124; None` | `sin valor declarado` |
| `currency` | `str &#124; None` | `sin valor declarado` |
| `facts` | `tuple[ReferencedFact, ...]` | `sin valor declarado` |

### SelectionInputV1

Fuente: [finmate/selection/contracts.py](../../../FinMate/finmate/selection/contracts.py), línea 216. Bases: `ClosedModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `schema_version` | `str` | `sin valor declarado` |
| `policy_version` | `str` | `sin valor declarado` |
| `prompt_version` | `str` | `sin valor declarado` |
| `catalog_version` | `str` | `sin valor declarado` |
| `selection_id` | `str` | `sin valor declarado` |
| `selection_revision` | `int` | `sin valor declarado` |
| `purpose` | `str` | `sin valor declarado` |
| `criteria` | `SelectionCriteriaV1` | `sin valor declarado` |
| `limitations` | `tuple[str, ...]` | `sin valor declarado` |
| `candidates` | `tuple[CandidateInputV1, ...]` | `sin valor declarado` |

## 9. DTO financieros

### ReadMeta

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 13. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `market_as_of` | `date &#124; None` | `None` |
| `fundamentals_as_of` | `date &#124; None` | `None` |
| `derived_at` | `datetime &#124; None` | `None` |
| `formula_version` | `str` | `sin valor declarado` |
| `batch_id` | `str &#124; None` | `None` |

### ReadResult

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 45. Bases: `ContractModel`, `Generic[T]`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `data` | `T` | `sin valor declarado` |
| `meta` | `ReadMeta` | `sin valor declarado` |

### Page

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 50. Bases: `ContractModel`, `Generic[T]`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `items` | `tuple[T, ...]` | `sin valor declarado` |
| `page` | `int` | `sin valor declarado` |
| `page_size` | `int` | `sin valor declarado` |
| `total` | `int` | `sin valor declarado` |
| `pages` | `int` | `sin valor declarado` |
| `sectors` | `tuple[str, ...]` | `()` |

### Coverage

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 59. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `profile` | `bool` | `False` |
| `prices` | `bool` | `False` |
| `income` | `bool` | `False` |
| `balance` | `bool` | `False` |
| `cashflow` | `bool` | `False` |

### CompanyListItem

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 67. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `name` | `str &#124; None` | `None` |
| `sector` | `str &#124; None` | `None` |
| `industry` | `str &#124; None` | `None` |
| `market_capitalization` | `int &#124; None` | `None` |
| `pe_ratio` | `float &#124; None` | `None` |
| `return_on_equity_ttm` | `float &#124; None` | `None` |
| `latest_close` | `float &#124; None` | `None` |
| `latest_trade_date` | `date &#124; None` | `None` |
| `coverage` | `Coverage` | `sin valor declarado` |

### UniverseSummary

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 80. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `company_count` | `int` | `sin valor declarado` |
| `coverage` | `dict[str, int]` | `sin valor declarado` |
| `sectors` | `tuple[dict[str, int &#124; str], ...]` | `sin valor declarado` |
| `latest_price_date` | `date &#124; None` | `sin valor declarado` |

### CompanySnapshot

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 87. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `name` | `str &#124; None` | `None` |
| `description` | `str &#124; None` | `None` |
| `sector` | `str &#124; None` | `None` |
| `industry` | `str &#124; None` | `None` |
| `country` | `str &#124; None` | `None` |
| `currency` | `str &#124; None` | `None` |
| `market_capitalization` | `int &#124; None` | `None` |
| `shares_outstanding` | `int &#124; None` | `None` |
| `beta` | `float &#124; None` | `None` |
| `pe_ratio` | `float &#124; None` | `None` |
| `forward_pe` | `float &#124; None` | `None` |
| `eps` | `float &#124; None` | `None` |
| `profit_margin` | `float &#124; None` | `None` |
| `return_on_equity_ttm` | `float &#124; None` | `None` |
| `latest_close` | `float &#124; None` | `None` |
| `latest_trade_date` | `date &#124; None` | `None` |
| `revenue_cagr_3y` | `float &#124; None` | `None` |
| `debt_to_equity` | `float &#124; None` | `None` |
| `fcf_margin` | `float &#124; None` | `None` |
| `sharpe` | `float &#124; None` | `None` |
| `max_drawdown` | `float &#124; None` | `None` |
| `return_1m` | `float &#124; None` | `None` |

### FundamentalPeriod

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 113. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `fiscal_period` | `date` | `sin valor declarado` |
| `period_type` | `str` | `sin valor declarado` |
| `currency` | `str &#124; None` | `None` |
| `values` | `dict[str, float &#124; None]` | `sin valor declarado` |

### PricePoint

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 121. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `date` | `date` | `sin valor declarado` |
| `open` | `float &#124; None` | `None` |
| `high` | `float &#124; None` | `None` |
| `low` | `float &#124; None` | `None` |
| `close` | `float &#124; None` | `None` |
| `volume` | `int &#124; None` | `None` |

### MetricDefinitionDTO

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 131. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `key` | `str` | `sin valor declarado` |
| `label` | `str` | `sin valor declarado` |
| `unit` | `str` | `sin valor declarado` |
| `historical` | `bool` | `sin valor declarado` |

### TrendPoint

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 138. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `period` | `date` | `sin valor declarado` |
| `value` | `float` | `sin valor declarado` |

### MetricTrend

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 143. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `metric_key` | `str` | `sin valor declarado` |
| `years` | `int` | `sin valor declarado` |
| `points` | `tuple[TrendPoint, ...]` | `sin valor declarado` |
| `start_value` | `float` | `sin valor declarado` |
| `end_value` | `float` | `sin valor declarado` |
| `absolute_change` | `float` | `sin valor declarado` |
| `relative_change` | `float &#124; None` | `sin valor declarado` |

### SectorComparison

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 154. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `metric_key` | `str` | `sin valor declarado` |
| `sector` | `str` | `sin valor declarado` |
| `value` | `float` | `sin valor declarado` |
| `peer_median` | `float` | `sin valor declarado` |
| `peer_percentile` | `float` | `sin valor declarado` |
| `peer_count` | `int` | `sin valor declarado` |

### ScreenCandidateDTO

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 164. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `name` | `str &#124; None` | `None` |
| `sector` | `str &#124; None` | `None` |
| `latest_close` | `float &#124; None` | `None` |
| `latest_trade_date` | `date &#124; None` | `None` |
| `passed_groups` | `tuple[str, ...]` | `sin valor declarado` |
| `metrics` | `dict[str, Any]` | `sin valor declarado` |

### IndexPoint

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 174. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `date` | `date` | `sin valor declarado` |
| `value` | `float` | `sin valor declarado` |

### MacroPoint

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 179. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `series` | `str` | `sin valor declarado` |
| `date` | `date` | `sin valor declarado` |
| `value` | `float` | `sin valor declarado` |
| `provider` | `str` | `sin valor declarado` |

### DCFInputsDTO

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 186. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `currency` | `str` | `sin valor declarado` |
| `base_date` | `date` | `sin valor declarado` |
| `base_revenue` | `float` | `sin valor declarado` |
| `normalized_fcff_margin` | `float` | `sin valor declarado` |
| `historical_revenue_growth` | `float` | `sin valor declarado` |
| `tax_rate` | `float` | `sin valor declarado` |
| `risk_free_rate` | `float` | `sin valor declarado` |
| `beta` | `float` | `sin valor declarado` |
| `market_cap` | `float` | `sin valor declarado` |
| `debt` | `float` | `sin valor declarado` |
| `cash` | `float` | `sin valor declarado` |
| `shares_outstanding` | `float` | `sin valor declarado` |
| `equity_risk_premium` | `float` | `sin valor declarado` |
| `cost_of_equity` | `float` | `sin valor declarado` |
| `cost_of_debt` | `float` | `sin valor declarado` |
| `wacc` | `float` | `sin valor declarado` |
| `fiscal_dates` | `tuple[date, ...]` | `sin valor declarado` |

### TrackResult

Fuente: [findata/contracts/models.py](../../../FinMate/findata/contracts/models.py), línea 207. Bases: `ContractModel`.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `status` | `Literal['pending', 'active', 'retired', 'no_data']` | `sin valor declarado` |
| `created` | `bool` | `sin valor declarado` |
| `ingestion_job_id` | `str &#124; None` | `None` |

## 10. Proyecciones de conocimiento

### CompanyKnowledgeRequest

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 11. Bases: ninguna.

The user-owned company scopes required by one observation.  ``consumer`` and work identity are provenance.  They never select SQL: the company recipe remains explicit and bounded by user and symbols.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `user_id` | `str` | `sin valor declarado` |
| `symbols` | `tuple[str, ...]` | `sin valor declarado` |
| `observed_at` | `datetime` | `sin valor declarado` |
| `consumer` | `str` | `'opportunity'` |
| `task_id` | `str` | `'conversation'` |
| `task_version` | `str` | `'1'` |
| `intent_revision` | `int` | `1` |

### KnowledgeDependency

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 28. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `kind` | `str` | `sin valor declarado` |
| `identifier` | `str` | `sin valor declarado` |
| `version` | `str` | `sin valor declarado` |
| `as_of` | `datetime &#124; date &#124; None` | `sin valor declarado` |

### CharacterizationFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 36. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `created_at` | `datetime` | `sin valor declarado` |
| `content` | `Mapping[str, object]` | `sin valor declarado` |

### CompanyFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 43. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `symbol` | `str` | `sin valor declarado` |
| `name` | `str &#124; None` | `sin valor declarado` |
| `sector` | `str &#124; None` | `sin valor declarado` |
| `industry` | `str &#124; None` | `sin valor declarado` |
| `currency` | `str &#124; None` | `sin valor declarado` |
| `latest_close` | `float &#124; None` | `sin valor declarado` |
| `latest_trade_date` | `date &#124; None` | `sin valor declarado` |

### ThesisFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 54. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `symbol` | `str` | `sin valor declarado` |
| `judgment` | `Mapping[str, object] &#124; None` | `sin valor declarado` |
| `freshness` | `Mapping[str, object]` | `sin valor declarado` |
| `input_revision` | `int` | `sin valor declarado` |

### EvidenceFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 63. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `source` | `str` | `sin valor declarado` |
| `origin` | `str` | `sin valor declarado` |
| `timestamp` | `datetime` | `sin valor declarado` |
| `dimension_key` | `str &#124; None` | `sin valor declarado` |
| `content` | `str` | `sin valor declarado` |
| `source_ref` | `str &#124; None` | `sin valor declarado` |
| `created_at` | `datetime` | `sin valor declarado` |

### DirectiveFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 75. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `kind` | `str` | `sin valor declarado` |
| `dimension_key` | `str &#124; None` | `sin valor declarado` |
| `created_at` | `datetime` | `sin valor declarado` |

### EventFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 83. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `title` | `str` | `sin valor declarado` |
| `event_date` | `date` | `sin valor declarado` |
| `content` | `str` | `sin valor declarado` |
| `source_url` | `str &#124; None` | `sin valor declarado` |
| `updated_at` | `datetime` | `sin valor declarado` |

### ValuationFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 93. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `method` | `str` | `sin valor declarado` |
| `intrinsic_value_low` | `float` | `sin valor declarado` |
| `intrinsic_value_high` | `float` | `sin valor declarado` |
| `currency` | `str` | `sin valor declarado` |
| `base_date` | `date` | `sin valor declarado` |
| `updated_at` | `datetime` | `sin valor declarado` |

### JobFact

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 104. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `task_type` | `str` | `sin valor declarado` |
| `created_at` | `datetime` | `sin valor declarado` |
| `input_context` | `Mapping[str, object]` | `sin valor declarado` |

### CompanyKnowledgeView

Fuente: [finmate/knowledge/models.py](../../../FinMate/finmate/knowledge/models.py), línea 111. Bases: ninguna.

A user- and symbol-scoped read model valid for one observation only.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `user_id` | `str` | `sin valor declarado` |
| `symbol` | `str` | `sin valor declarado` |
| `observed_at` | `datetime` | `sin valor declarado` |
| `company` | `CompanyFact &#124; None` | `sin valor declarado` |
| `company_exists` | `bool` | `sin valor declarado` |
| `watchlist_id` | `str &#124; None` | `sin valor declarado` |
| `watchlist_status` | `str &#124; None` | `sin valor declarado` |
| `characterization` | `CharacterizationFact &#124; None` | `sin valor declarado` |
| `thesis` | `ThesisFact &#124; None` | `sin valor declarado` |
| `evidence` | `tuple[EvidenceFact, ...]` | `sin valor declarado` |
| `directives` | `tuple[DirectiveFact, ...]` | `sin valor declarado` |
| `unbriefed_events` | `tuple[EventFact, ...]` | `sin valor declarado` |
| `latest_jobs` | `Mapping[str, JobFact]` | `sin valor declarado` |
| `dependencies` | `tuple[KnowledgeDependency, ...]` | `sin valor declarado` |
| `latest_valuation` | `ValuationFact &#124; None` | `None` |

## 11. Contexto y memoria de trabajo

### ContextBudget

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 14. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `max_bytes` | `int` | `24 * 1024` |
| `history_messages` | `int` | `12` |
| `recovery_seconds` | `float` | `2.0` |
| `max_candidates` | `int` | `5` |

### ContextMessage

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 26. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `source_id` | `str` | `sin valor declarado` |
| `role` | `Literal['user', 'assistant']` | `sin valor declarado` |
| `text` | `str` | `sin valor declarado` |

### ContextReference

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 33. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `context_id` | `str` | `sin valor declarado` |
| `resource` | `ResourceRef` | `sin valor declarado` |
| `relation` | `Literal['selected', 'conversation_focus', 'recent_result']` | `sin valor declarado` |
| `source_revision` | `str &#124; None` | `None` |
| `group_id` | `str &#124; None` | `None` |
| `position` | `int &#124; None` | `None` |

### ContextRequest

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 43. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `user_id` | `UserId` | `sin valor declarado` |
| `interaction_id` | `str` | `sin valor declarado` |
| `message` | `ContextMessage` | `sin valor declarado` |
| `history` | `tuple[ContextMessage, ...]` | `()` |
| `references` | `tuple[ContextReference, ...]` | `()` |
| `omissions` | `tuple[str, ...]` | `()` |
| `budget` | `ContextBudget` | `ContextBudget()` |

### ContextQuery

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 54. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `source_id` | `str` | `sin valor declarado` |
| `operation` | `str` | `sin valor declarado` |
| `arguments` | `Mapping[str, JsonValue]` | `field(default_factory=dict)` |

### ContextItem

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 64. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `source_id` | `str` | `sin valor declarado` |
| `content` | `Mapping[str, JsonValue]` | `sin valor declarado` |
| `references` | `tuple[ResourceRef, ...]` | `()` |
| `version` | `str &#124; None` | `None` |
| `observed_at` | `datetime &#124; None` | `None` |
| `provenance` | `str` | `'source_read'` |

### ContextResult

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 78. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `source_id` | `str` | `sin valor declarado` |
| `status` | `Literal['available', 'empty', 'unavailable', 'ambiguous', 'stale']` | `sin valor declarado` |
| `items` | `tuple[ContextItem, ...]` | `()` |
| `omitted` | `int` | `0` |
| `reason` | `str &#124; None` | `None` |
| `next_offset` | `int &#124; None` | `None` |
| `operation` | `str &#124; None` | `None` |

### ContextSnapshot

Fuente: [engine/context/contracts.py](../../../FinMate/engine/context/contracts.py), línea 93. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `revision` | `int` | `sin valor declarado` |
| `payload` | `Mapping[str, JsonValue]` | `sin valor declarado` |
| `serialized_bytes` | `int` | `sin valor declarado` |

### WorkingMemory

Fuente: [engine/context/memory.py](../../../FinMate/engine/context/memory.py), línea 9. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `references` | `tuple[ContextReference, ...]` | `()` |
| `results` | `tuple[ContextResult, ...]` | `()` |
| `confirmed` | `list[dict[str, JsonValue]]` | `field(default_factory=list)` |
| `pending_question` | `str &#124; None` | `None` |

## 12. Trabajo genérico y sesión

### RunLimits

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 31. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `max_decisions` | `int` | `sin valor declarado` |
| `max_resolutions` | `int` | `sin valor declarado` |
| `max_llm_calls` | `int` | `sin valor declarado` |
| `timeout_seconds` | `float` | `sin valor declarado` |
| `max_consistency_actions` | `int` | `1` |
| `max_read_resolutions` | `int` | `4` |

### WorkRequest

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 54. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `task_id` | `TaskId` | `sin valor declarado` |
| `user_id` | `UserId` | `sin valor declarado` |
| `arguments` | `Mapping[str, JsonValue]` | `sin valor declarado` |
| `limits` | `RunLimits` | `sin valor declarado` |
| `origin` | `str` | `'internal'` |
| `idempotency_key` | `str &#124; None` | `None` |
| `context_request` | `ContextRequest &#124; None` | `None` |
| `execution_policy` | `ExecutionPolicy` | `ExecutionPolicy()` |
| `working_memory` | `WorkingMemory &#124; None` | `None` |

### WorkScope

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 74. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `operator_ids` | `frozenset[OperatorId]` | `sin valor declarado` |
| `resources` | `tuple[ResourceRef, ...]` | `()` |
| `proposal_mode` | `ProposalMode` | `'candidates_only'` |

### BoundWork

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 84. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `task_id` | `TaskId` | `sin valor declarado` |
| `task_version` | `str` | `sin valor declarado` |
| `user_id` | `UserId` | `sin valor declarado` |
| `arguments` | `BaseModel` | `sin valor declarado` |
| `scope` | `WorkScope` | `sin valor declarado` |
| `limits` | `RunLimits` | `sin valor declarado` |
| `intent_revision` | `int` | `1` |
| `origin` | `str` | `'internal'` |
| `idempotency_key` | `str &#124; None` | `None` |
| `context_request` | `ContextRequest &#124; None` | `None` |
| `execution_policy` | `ExecutionPolicy` | `ExecutionPolicy()` |
| `working_memory` | `WorkingMemory &#124; None` | `None` |

### WorkRequirement

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 108. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `description` | `str` | `sin valor declarado` |
| `status` | `str` | `sin valor declarado` |
| `references` | `tuple[ResourceRef, ...]` | `()` |

### WorkBlocker

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 116. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `kind` | `str` | `sin valor declarado` |
| `recoverable` | `bool` | `sin valor declarado` |
| `references` | `tuple[ResourceRef, ...]` | `()` |

### WorkAssessment

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 124. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `status` | `AssessmentStatus` | `sin valor declarado` |
| `reason_code` | `str` | `sin valor declarado` |
| `requirements` | `tuple[WorkRequirement, ...]` | `()` |
| `blockers` | `tuple[WorkBlocker, ...]` | `()` |
| `result_refs` | `tuple[ResourceRef, ...]` | `()` |

### ActionPriority

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 137. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `urgency` | `int` | `sin valor declarado` |
| `materiality` | `int` | `0` |
| `tie_breaker` | `str` | `''` |

### ActionCandidate

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 144. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `proposal` | `RawProposal` | `sin valor declarado` |
| `addresses` | `tuple[str, ...]` | `sin valor declarado` |
| `targets` | `tuple[ResourceRef, ...]` | `sin valor declarado` |
| `priority` | `ActionPriority` | `sin valor declarado` |
| `reason` | `str` | `sin valor declarado` |
| `state_signature` | `str` | `sin valor declarado` |

### WorkOpportunity

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 155. Bases: ninguna.

A grounded continuation offered to the user after the current work.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `str` | `sin valor declarado` |
| `proposal` | `RawProposal` | `sin valor declarado` |
| `priority` | `ActionPriority` | `sin valor declarado` |
| `reason_code` | `str` | `sin valor declarado` |
| `context` | `Mapping[str, JsonValue]` | `sin valor declarado` |
| `targets` | `tuple[ResourceRef, ...]` | `sin valor declarado` |
| `state_signature` | `str` | `sin valor declarado` |

### WorkObservation

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 171. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `assessment` | `WorkAssessment` | `sin valor declarado` |
| `candidates` | `tuple[ActionCandidate, ...]` | `()` |
| `required_actions` | `tuple[ActionCandidate, ...]` | `()` |
| `context` | `Mapping[str, JsonValue]` | `field(default_factory=dict)` |
| `progress_token` | `str` | `''` |
| `observed_at` | `datetime &#124; None` | `None` |
| `opportunities` | `tuple[WorkOpportunity, ...]` | `()` |

### TaskSpec

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 194. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `TaskId` | `sin valor declarado` |
| `version` | `str` | `sin valor declarado` |
| `input_model` | `type[BaseModel]` | `sin valor declarado` |
| `operator_ids` | `frozenset[OperatorId]` | `sin valor declarado` |
| `consistency_rule_ids` | `tuple[ConsistencyRuleId, ...]` | `sin valor declarado` |
| `build_scope` | `WorkScopeBuilder` | `sin valor declarado` |
| `observe` | `WorkObserver` | `sin valor declarado` |
| `validate_action` | `WorkActionValidator` | `sin valor declarado` |

### ConsistencyRule

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 212. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `id` | `ConsistencyRuleId` | `sin valor declarado` |
| `evaluate` | `ConsistencyEvaluator` | `sin valor declarado` |

### WorkStep

Fuente: [engine/core/work.py](../../../FinMate/engine/core/work.py), línea 218. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `decision_kind` | `str` | `sin valor declarado` |
| `resolution` | `Resolution &#124; None` | `None` |
| `detail` | `str &#124; None` | `None` |

### SurfaceSelection

Fuente: [finmate/control/conversation/session.py](../../../FinMate/finmate/control/conversation/session.py), línea 18. Bases: ninguna.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `entity_id` | `str` | `sin valor declarado` |
| `card_id` | `str` | `sin valor declarado` |
| `section_id` | `str` | `sin valor declarado` |
| `token` | `int` | `sin valor declarado` |
| `origin_lens` | `str &#124; None` | `None` |
| `kind` | `str` | `'company'` |

### SurfaceTurnResult

Fuente: [finmate/control/conversation/session.py](../../../FinMate/finmate/control/conversation/session.py), línea 28. Bases: ninguna.

Committed results retained for the surface's two-turn window.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `turn` | `int` | `sin valor declarado` |
| `committed` | `tuple[Committed, ...]` | `sin valor declarado` |

### Session

Fuente: [finmate/control/conversation/session.py](../../../FinMate/finmate/control/conversation/session.py), línea 36. Bases: ninguna.

Conversation history plus working memory for the current turn.

| Campo | Tipo declarado | Declaración o valor por defecto |
|---|---|---|
| `user_id` | `str` | `sin valor declarado` |
| `focus_set` | `list[str]` | `field(default_factory=list)` |
| `working_memory` | `WorkingMemory` | `field(default_factory=WorkingMemory)` |
| `execution_policy` | `ExecutionPolicy` | `field(default_factory=ExecutionPolicy)` |
| `turns` | `list[ConversationTurn]` | `field(default_factory=list)` |
| `committed` | `list[Committed]` | `field(default_factory=list)` |
| `reads` | `list[Committed]` | `field(default_factory=list)` |
| `rejected` | `list[Rejected]` | `field(default_factory=list)` |
| `deferred` | `list[Deferred]` | `field(default_factory=list)` |
| `surface_turn` | `int` | `0` |
| `surface_results` | `list[SurfaceTurnResult]` | `field(default_factory=list)` |
| `surface_revisions` | `dict[str, tuple[str, str, tuple[str, ...]]]` | `field(default_factory=dict)` |
| `surface_selection` | `SurfaceSelection &#124; None` | `None` |
| `surface_selection_token` | `int` | `0` |
| `surface_global` | `bool` | `False` |
| `opportunities` | `tuple[WorkOpportunity, ...]` | `()` |

## Cobertura del inventario

Se inventarían 161 clases con 1131 campos declarados y 41 declaraciones de tabla. El recuento de tablas corresponde a modelos privados y Findata v2, no a todas las tablas del repositorio. Se excluyen modelos financieros anteriores a v2, infraestructura de captura/ingesta y artefactos de auditoría.
