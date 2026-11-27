from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from check_dependencies import QUESTIONS, from_git, main, packages, problems, sections

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE = "a" * 40
HEAD = "b" * 40
BEFORE = """
[project]
name = "example-project"
dependencies = ["httpx>=0.28.1", "pydantic>=2.13"]

[dependency-groups]
dev = ["pytest>=9.1", "ruff>=0.16.5"]
"""


def answered(name: str, skip: frozenset[int] = frozenset()) -> str:
    answers = [
        f"{position}. **{question}.** An answer."
        for position, question in enumerate(QUESTIONS, 1)
        if position not in skip
    ]
    return "\n".join([f"## Dependency: {name}", "", *answers])


def run(after: str, body: str | None, before: str = BEFORE) -> int:
    manifests = {BASE: before, HEAD: after}
    payload = {"number": 610, "body": body, "baseRefOid": BASE, "headRefOid": HEAD}
    return main(
        ["check_dependencies.py", "610", "."],
        lambda _repo, _number: payload,
        lambda _repo, revision: manifests[revision],
    )


def test_a_new_package_without_its_section_fails(capsys: pytest.CaptureFixture[str]) -> None:
    after = BEFORE.replace('"pydantic>=2.13"', '"pydantic>=2.13", "Rich>=14"')
    assert run(after, "Closes #609\n\n## Summary\n\nAdds rich.") == 1
    captured = capsys.readouterr()
    assert captured.out == "PR #610 adds rich and removes none\n"
    assert "'## Dependency: rich'" in captured.err
    assert "Where it runs" in captured.err


def test_a_new_package_with_its_section_passes() -> None:
    after = BEFORE.replace('"pydantic>=2.13"', '"pydantic>=2.13", "rich>=14"')
    assert run(after, f"## Summary\n\nAdds rich.\n\n{answered('rich')}\n") == 0


def test_a_first_manifest_makes_every_package_new(capsys: pytest.CaptureFixture[str]) -> None:
    body = "\n\n".join(answered(name) for name in ("httpx", "pydantic", "pytest"))
    assert run(BEFORE, body, before="") == 1
    captured = capsys.readouterr()
    assert captured.out == "PR #610 adds httpx, pydantic, pytest, ruff and removes none\n"
    assert "'## Dependency: ruff'" in captured.err


def test_a_manifest_absent_at_a_revision_reads_as_empty(tmp_path: Path) -> None:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=tmp_path, capture_output=True, text=True, check=True
        ).stdout.strip()

    git("init", "-q")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    git("add", "README.md")
    git("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "x")
    (tmp_path / "pyproject.toml").write_text(BEFORE, encoding="utf-8")
    assert from_git(tmp_path, git("rev-parse", "HEAD")) == ""


def test_a_new_dev_package_without_its_section_fails() -> None:
    after = BEFORE.replace('"ruff>=0.16.5"', '"ruff>=0.16.5", "hypothesis>=6"')
    assert run(after, "") == 1


def test_a_version_bump_passes() -> None:
    after = BEFORE.replace("pydantic>=2.13", "pydantic>=2.14").replace("ruff>=0.16.5", "ruff>=1")
    assert run(after, None) == 0


def test_a_removal_passes(capsys: pytest.CaptureFixture[str]) -> None:
    assert run(BEFORE.replace(', "pydantic>=2.13"', ""), "") == 0
    assert capsys.readouterr().out == "PR #610 adds no package and removes pydantic\n"


def test_a_package_moved_between_groups_is_not_new() -> None:
    after = BEFORE.replace(', "pydantic>=2.13"', "").replace(
        '"ruff>=0.16.5"', '"ruff>=0.16.5", "pydantic>=2.13"'
    )
    assert run(after, "") == 0


def test_a_section_missing_an_answer_fails(capsys: pytest.CaptureFixture[str]) -> None:
    after = BEFORE.replace('"pydantic>=2.13"', '"pydantic>=2.13", "rich>=14"')
    assert run(after, answered("rich", frozenset({5}))) == 1
    assert "5. What it pulls in" in capsys.readouterr().err


def test_a_section_for_another_package_does_not_count() -> None:
    after = BEFORE.replace('"pydantic>=2.13"', '"pydantic>=2.13", "rich>=14"')
    assert run(after, answered("textual")) == 1


def test_answers_under_a_later_heading_do_not_count() -> None:
    after = BEFORE.replace('"pydantic>=2.13"', '"pydantic>=2.13", "rich>=14"')
    body = "## Dependency: rich\n\n## Test plan\n\n" + answered("x").split("\n", 2)[2]
    assert run(after, body) == 1


def test_a_subheading_inside_a_section_keeps_it_open() -> None:
    body = answered("rich").replace("4.", "### Licence\n\n4.")
    assert sections(body) == {"rich": frozenset(range(1, 7))}


@pytest.mark.parametrize(
    ("added", "heading"),
    [
        pytest.param("python_dotenv", "## Dependency: python-dotenv", id="underscore"),
        pytest.param("Python.Dotenv", "## Dependency: `python-dotenv`", id="dot and backticks"),
    ],
)
def test_names_are_compared_normalised(added: str, heading: str) -> None:
    after = BEFORE.replace('"pydantic>=2.13"', f'"pydantic>=2.13", "{added}[cli]>=1.2"')
    body = answered("x").replace("## Dependency: x", heading)
    assert run(after, body) == 0


def test_an_optional_dependency_counts() -> None:
    after = BEFORE.replace(
        "[dependency-groups]",
        '[project.optional-dependencies]\npi = ["gpiozero>=2"]\n\n[dependency-groups]',
    )
    added = packages(after, "head") - packages(BEFORE, "base")
    assert added == {"gpiozero"}
    assert problems(added, "")


def test_an_included_group_is_not_a_package() -> None:
    after = BEFORE + 'lint = [{include-group = "dev"}, "ruff>=0.16.5"]\n'
    assert run(after, "") == 0


@pytest.mark.parametrize(
    "manifest",
    [
        "[project\n",
        '[project]\ndependencies = "httpx"\n',
        "[project]\ndependencies = [3]\n",
        '[project]\ndependencies = [">=1"]\n',
        '[dependency-groups]\ndev = "pytest"\n',
    ],
)
def test_a_malformed_manifest_exits_two(manifest: str) -> None:
    assert run(manifest, "") == 2


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"number": "610", "body": "", "baseRefOid": BASE, "headRefOid": HEAD},
        {"number": 610, "body": 3, "baseRefOid": BASE, "headRefOid": HEAD},
        {"number": 610, "body": "", "headRefOid": HEAD},
    ],
)
def test_a_malformed_payload_exits_two(payload: object) -> None:
    assert main(["check_dependencies.py", "610"], lambda _r, _n: payload, lambda _r, _v: "") == 2


@pytest.mark.parametrize("argv", [["check_dependencies.py"], ["check_dependencies.py", "main"]])
def test_a_missing_or_unreadable_number_exits_two(argv: list[str]) -> None:
    assert main(argv, lambda _r, _n: {}, lambda _r, _v: "") == 2


def test_the_real_manifest_parses() -> None:
    found = packages((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"), "pyproject")
    assert {"mypy", "pytest", "ruff"} <= found
