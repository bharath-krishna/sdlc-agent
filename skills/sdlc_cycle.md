# SDLC Skills: sdlc_cycle

## Skill Name: `sdlc_cycle`

**Description:** A full-lifecycle automation routine that follows the standard SDLC pattern: **Plan → Develop → Test → Deploy**. Applies to any backend project managed by this agent.

---

## The Execution Protocol

Trigger this skill for every new feature or bug fix to ensure a predictable, high-quality release cycle.

### Step 1: PLAN (Strategic Architecting)

**Actor:** `planner_agent`
**Input:** High-level requirement or issue description.
**Action:**

- Analyze the requirement against the existing project architecture.
- Break the work into an ordered technical roadmap.
- Update `PROGRESS.md` in the target project with planned tasks and their status (`[ ]`).
- **Output:** A sequenced task list in `PROGRESS.md`.

### Step 2: DEVELOP (Implementation)

**Actor:** `developer_agent`
**Input:** Plan from Step 1 (`PROGRESS.md`).
**Action:**

- Implement the planned tasks incrementally — one focused change at a time.
- Keep `pyproject.toml` (or equivalent manifest) and `Dockerfile` consistent.
- Follow the modular pattern already established in the project's `src/` directory.
- Mark each completed task in `PROGRESS.md` as `[x]` and commit with a descriptive message.
- **Output:** Functional, modular code committed to the repository.

### Step 3: TEST (Verification)

**Actor:** `developer_agent` or `tester_agent`
**Input:** Implemented code and the project's test suite.
**Action:**

- Run the full test suite (e.g. `uv run pytest tests/ -v`) and capture output.
- Validate API endpoints or core business logic against expected behaviour.
- Confirm dependency resolution is clean (e.g. `uv sync` with no conflicts).
- **Output:** A `PASSED` or `FAILED` status report; update `PROGRESS.md` with test results.

### Step 4: DEPLOY (GitOps & CI/CD)

**Actor:** `developer_agent`
**Input:** Verified, committed code.
**Action:**

- Run `git add`, `git commit`, and `git push` to the target branch.
- Trigger the CI/CD pipeline (build Docker image → push to registry).
- Apply any infrastructure changes (e.g. Kubernetes manifests, Kustomize overlays).
- **Output:** Successful deployment confirmed; update `PROGRESS.md` with deploy status.

---

## Failure Handling

If any phase fails, **stop immediately** and report the phase name and error to the user.

| Phase   | Failure Signal                             | Common Cause                                     |
| ------- | ------------------------------------------ | ------------------------------------------------ |
| Plan    | Planner returns no tasks                   | Ambiguous requirement — ask the user to clarify  |
| Develop | `ImportError` / `ModuleNotFoundError`      | Missing dependency not added to the manifest     |
| Test    | Test assertion failure or non-2xx response | Logic error in implementation or schema mismatch |
| Deploy  | Registry push / auth error                 | CI secret missing or expired                     |

---

## Usage Examples

- `"Run sdlc_cycle for [Feature Name]"`
- `"Check progress of the current sdlc_cycle."`
- `"sdlc_cycle: add user authentication endpoint"`
