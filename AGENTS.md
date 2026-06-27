# AGENTS.md

## Purpose

This file defines rules for AI-assisted development in this repository.
All changes MUST follow these rules.

---

## Core Rules (MANDATORY)

* ALWAYS follow existing code patterns before introducing new ones
* NEVER introduce breaking changes without explicit proposal
* ALWAYS keep changes minimal and focused
* ALWAYS explain non-trivial changes in comments or commit messages

---

## Python Environment

* Python environment is managed using `uv`
* NEVER assume global Python environment
* ALWAYS use project-defined dependencies

### Commands

* Install deps: `uv sync`
* Run scripts: `uv run <command>`

---

## Code Style

* Code MUST comply with `ruff`
* ALWAYS run lint before finishing
* use google style docstring 

### Commands

* Lint: `ruff check .`

* Format (if enabled): `ruff format .`

* 可能な限りruff rulesを守ること。

* Prefer consistency over personal preference

---

## Testing

* pythonファイルに変更を加えたとき、tests/に対応するpytestがある場合はテストを実施する
* テストに失敗した場合はテストコードを修正する前に、実装上の問題を疑い、対応策が複数ある場合はユーザーに確認をすること。
* コードの修正に関与しないタスクについてはテストをスキップしてよい

### Commands

* Run tests: `uv run pytest -q`

---

## Repository Structure Awareness

Before making changes, you MUST read:

* `README.md`
* `docs/` directory (if exists)

If unsure about domain logic:

* DO NOT guess
* ASK or leave a clear TODO

---

## Safe Modification Rules

* NEVER change API signatures without confirmation
* NEVER modify database schema without documentation update
* ALWAYS update related docs when behavior changes

---

## Commit / Change Policy

* Changes MUST be logically grouped
* DO NOT mix unrelated changes
* Large changes MUST be split

---

## What NOT to Do

* DO NOT rewrite large files without reason
* DO NOT introduce new frameworks or libraries casually
* DO NOT remove existing comments unless incorrect
* DO NOT optimize prematurely

---

## When in Doubt

* Prefer smaller, reversible changes
* Add comments explaining intent
* Leave clear notes for human reviewers

---


