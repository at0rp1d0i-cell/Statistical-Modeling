# Final Editing And Package Guide Implementation Plan

<execution_handoff>
  <executor>codex</executor>
  <primary_mode>solo-execute</primary_mode>
  <alternate_mode>subagent-driven-development</alternate_mode>
  <rule>Execute task-by-task with verification after each task.</rule>
</execution_handoff>

**Goal:** Add a final human Word-editing guide and make the generated submission package carry that guide alongside the manuscript, tables, figures, code, and data notice.

**Architecture:** Keep research-design decisions unchanged. Add a paper-facing Markdown guide under `docs/paper/`, include it in packaging through `src/32_prepare_submission_package.py`, and update the existing checklist/inventory/README to point editors to the guide.

**Tech Stack:** Markdown documentation, Python packaging script, pytest, py_compile, zip validation.

---

### Task 1: Add the final Word editing guide

**Files:**
- Create: `docs/paper/final-editing-guide.md`

**Steps:**
1. Write the guide with table/figure placement, editing order, and explicit do-not-overclaim boundaries.
2. Keep it operational for the human Word/WPS stage rather than changing empirical claims.
3. Verify the file renders as plain Markdown and references only existing tables/figures.

### Task 2: Wire the guide into submission packaging

**Files:**
- Modify: `src/32_prepare_submission_package.py`
- Modify: `tests/test_prepare_submission_package.py`

**Steps:**
1. Add `final-editing-guide.md` to `PAPER_DOC_FILES`.
2. Mention the guide in `MANIFEST.md` structure and next-step instructions.
3. Extend the package smoke test to create and assert the guide copy.

### Task 3: Update paper-facing navigation docs

**Files:**
- Modify: `docs/paper/submission-checklist.md`
- Modify: `docs/paper/table-figure-inventory.md`
- Modify: `README.md`

**Steps:**
1. Point final editors to `docs/paper/final-editing-guide.md` before moving tables/figures.
2. Clarify that PDF/PNG/JPG figures are available, with PNG preferred if Word does not preserve PDF vectors.
3. Record which tables/figures belong in正文 versus technical appendix.

### Task 4: Regenerate package artifacts and verify

**Files:**
- Regenerate ignored local artifacts under `dist/`.

**Steps:**
1. Run `python3 src/33_export_submission_docx.py`.
2. Run `python3 src/32_prepare_submission_package.py`.
3. Run `unzip -t dist/submission_package_current.zip`.
4. Run `python3 -m pytest -q`.
5. Run `python3 -m py_compile $(find src tests -name '*.py' | sort)`.
6. Run `git diff --check`.

### Task 5: Commit and push

**Files:**
- Versioned docs/code/test changes only.

**Steps:**
1. Review `git diff` and `git status`.
2. Commit with Lore protocol and `Co-authored-by: OpenAI Codex <noreply@openai.com>`.
3. Push `main` to `origin/main`.
