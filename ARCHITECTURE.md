# Unified Multi-Project Architecture: A+B+C+Extended

## 🎯 Overview

This document describes the **Meta-Orchestrator Architecture** — a unified system for managing three parallel development vectors:

- **A) Policy-Driven CI/CD** for both Bakhmach-Business-Hub and Hybrid-Portfolio
- **B) Centralized Control Plane** via Meta-Orchestrator + Manus integration
- **C) Energy-Aware Infrastructure** as the foundation for all operations
- **Extended) Intelligent Auto-Scaling** based on consciousness + energy scores

---

## 📐 System Architecture

### Three-Layer Stack

```
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATION LAYER                                         │
│ • Meta-Orchestrator (Python)                               │
│ • Manus Project Sync (API)                                 │
│ • Real-time Consciousness Scoring                          │
└─────────────────────────────────────────────────────────────┘
        ↓              ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Bakhmach    │ │  Portfolio   │ │   Energy     │ │   Workflow   │
│  Business    │ │   (AI/ML)    │ │ Management   │ │     (Manus)  │
│  Hub         │ │              │ │              │ │              │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ - CI/Policy  │ │ - ML Models  │ │ - Battery    │ │ - Tasks      │
│ - Conscious  │ │ - Embeddings │ │ - UPS Status │ │ - Projects   │
│ - Monitoring │ │ - Skill Ext. │ │ - Thermal    │ │ - Commits    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        ↓              ↓              ↓              ↓
┌─────────────────────────────────────────────────────────────┐
│ DATA LAYER                                                  │
│ • Consciousness Reports (.consciousness_report.json)       │
│ • Orchestrator Reports (.orchestrator_report.json)         │
│ • Energy Metrics (/proc/acpi/battery, cloud APIs)          │
│ • Real-time Dashboard (metrics archive)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔋 Energy Model

### EnergyLevel Enum

```python
class EnergyLevel(Enum):
    CRITICAL = 0   # < 5% battery    → Only essential fixes
    LOW = 1        # 5-20% battery   → Reduce experiments
    MEDIUM = 2     # 20-60% battery  → Normal operations
    HIGH = 3       # > 60% battery   → Full speed
    FULL = 4       # Plugged in      → No limits
```

### Deployment Rules by Energy Level

| Level | Bakhmach | Portfolio | Actions |
|-------|----------|-----------|----------|
| **CRITICAL** | Only fixes | Frozen | Automatic throttle, UPS alert |
| **LOW** | Normal | Disabled | No expensive ML ops |
| **MEDIUM** | Normal | Normal mode | Balanced operations |
| **HIGH** | Full speed | Efficient mode | All features available |
| **FULL** | Full speed | Full speed | Unrestricted |

---

## 🧠 Consciousness Model

### Multi-Project Consciousness Scoring

**For Bakhmach:**
- Integration Score (0-100): code + ML + services alignment
- Well-being Score (0-100): personal capacity from PDP
- Stability Score (0-100): incidents, errors, rollbacks
- Mode: FAST/SAFE/HALT

**For Portfolio:**
- Model Health (0-100): ML model performance metrics
- Embedding Quality (0-100): semantic search accuracy
- Computation Load (0-100): CPU/memory usage
- Mode: EFFICIENT (low energy) / NORMAL

**For Infrastructure:**
- Power Available: energy level (0-4)
- Cooling Status: thermal monitoring
- Network Status: connectivity
- Mode: DEGRADED (low power) / NORMAL

### Deployment Policy Logic

```python
def determine_deployment_policy(self):
    # Bakhmach can deploy if:
    # - consciousness_mode ≠ "HALT"
    # - energy_level ≥ MEDIUM
    # - infrastructure power available
    
    # Portfolio can deploy if:
    # - model_health > 70
    # - computation_load < 80
    # - energy_level ≥ MEDIUM
    # - energy ≠ CRITICAL
```

---

## 🔄 Continuous Orchestration Loop

**Executed every 30 seconds:**

1. **Energy Check**
   - Read battery level / cloud energy metrics
   - Classify into EnergyLevel enum

2. **Consciousness Evaluation**
   - Read Bakhmach `.consciousness_report.json`
   - Calculate Portfolio ML/embedding health
   - Check Infrastructure power/thermal

3. **Deployment Policy Determination**
   - For each project, decide if deployments allowed
   - Apply energy + consciousness constraints

4. **Manus Synchronization**
   - Push orchestrator state to Manus API
   - Update task statuses
   - Link commits to tasks

5. **Dashboard & Logging**
   - Print unified dashboard to console
   - Archive metrics for historical analysis
   - Export JSON for web dashboards

6. **Auto-Remediation Triggers**
   - Low energy → throttle experiments
   - High error rate → auto-rollback
   - Consciousness HALT → block deployments

---

## 📊 Data Flow

```
Git Commits (both repos)
        ↓
[CI Policy Gate] → Detect change type
        ↓
[Tests + SLO Checks] → Run domain-specific tests
        ↓
[Consciousness Guard] → Evaluate integration/wellbeing/stability
        ↓
[Meta-Orchestrator] → Check energy + consciousness
        ↓
[Deployment Policy] → Decide: allow/block/throttle
        ↓
[Manus Sync] → Update project status
        ↓
[Dashboard] → Display unified view
```

---

## 🛠️ Components

### Meta-Orchestrator (`ci/meta_orchestrator.py`)
- **register_project()**: Register Bakhmach, Portfolio, Infrastructure
- **check_energy_level()**: Monitor power availability
- **evaluate_consciousness_all_projects()**: Score all projects
- **determine_deployment_policy()**: Decide what can deploy
- **sync_with_manus()**: Push state to Manus API
- **run_continuous_orchestration()**: Main loop (30s intervals)

### Consciousness Guard (`consciousness/consciousness_guard.py`)
- Evaluates Bakhmach-specific consciousness scores
- Returns exit code 0/1 for CI gating
- Blocks deployments in HALT mode

### Real-Time Dashboard (`monitoring/realtime_dashboard.py`)
- Collects metrics from all domains
- Evaluates alerts based on thresholds
- Maintains 60-minute rolling history
- Exports JSON for external dashboards

### Policy Gate (`.github/workflows/policy-gate.yml`)
- Detects change type from commit message
- Runs domain-specific checks
- Calls consciousness_guard.py
- Calls meta_orchestrator.py
- Auto-merges safe changes / requires review otherwise

---

## 🚀 Running the System

### Start Meta-Orchestrator
```bash
python ci/meta_orchestrator.py
```

**Output (every 30s):**
```
================================================================================
META-ORCHESTRATOR DASHBOARD - 2025-12-30T19:30:45.123456
================================================================================
ENERGY: MEDIUM     | Deployment Allowed: {'bakhmach': True, 'portfolio': False}
Consciousness Scores: {
  'bakhmach': {'integration': 70, 'wellbeing': 65, 'stability': 75, 'mode': 'SAFE'},
  'portfolio': {'model_health': 85, 'computation_load': 45, 'mode': 'NORMAL'},
  'infrastructure': {'power_available': 2, 'cooling_status': 'NORMAL'}
}
================================================================================
```

### Start Real-Time Monitoring
```bash
python monitoring/realtime_dashboard.py
```

---

## 📈 Metrics & Observability

### Key Metrics Tracked

**Every Project:**
- Deployment attempts (success/failure)
- SLO violations (latency, error rate)
- Energy consumption (watts, amps)
- Consciousness scores trend

**Bakhmach-specific:**
- Test coverage %
- Performance regression %
- Data drift score
- User satisfaction (from local business feedback)

**Portfolio-specific:**
- Model accuracy trends
- Embedding quality score
- GPU/CPU utilization
- Inference latency

### Storage
- **Recent** (30 min): in-memory archive
- **Historical** (1+ month): JSON files / database
- **Dashboards**: Exportable to Grafana, Datadog, etc.

---

## 🔐 Security & Safety

- **Policy-Driven**: All changes routed through CI policies
- **Consciousness Guards**: No HALT-mode deployments
- **Energy Safeguards**: Battery-critical shutdowns
- **Audit Trail**: All actions logged to Manus + Git
- **Reversibility**: Auto-rollback on SLO violation

---

## 🎯 Success Criteria

✅ **A) CI/CD** — Both projects follow same policies, auto-merge safe changes
✅ **B) Unified Control** — Manus is source of truth, all systems synced
✅ **C) Energy Awareness** — System throttles when battery/power low
✅ **Extended** — Auto-scaling, intelligent resource allocation, no manual intervention

---

## 🛣️ Roadmap

### Phase 1 (Done)
- [x] Meta-Orchestrator class
- [x] Energy enum + check_energy_level()
- [x] Consciousness multi-project scoring
- [x] Deployment policy logic
- [x] Manus sync skeleton

### Phase 2 (Next)
- [ ] Real Manus API integration
- [ ] Real battery/energy monitoring (/proc/acpi/battery)
- [ ] Web dashboard (React/Vue UI)
- [ ] Slack/email alerting
- [ ] Webhook for GitHub commits → Manus tasks

### Phase 3 (Future)
- [ ] Auto-scaler: spin instances at HIGH energy
- [ ] ML model auto-retraining on schedule
- [ ] Distributed consciousness across multiple machines
- [ ] Prediction: energy forecasting for preventive throttling
- [ ] Community: federated consciousness (share scores across teams)

---

## 📚 References

- **Policy-Driven CI/CD**: `docs/CI_POLICY.md`
- **Consciousness Model**: `consciousness/CONSCIOUSNESS_MODEL.md`
- **Monitoring**: `monitoring/README.md`
- **Orchestrator**: `ci/meta_orchestrator.py`

---

**Last Updated:** 2025-12-30
**Status:** MVP (Phase 1 Complete)
**Next Review:** 2026-01-06
