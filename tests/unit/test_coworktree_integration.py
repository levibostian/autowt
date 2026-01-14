"""Tests for coworktree command selection.

These tests validate that autowt prefers `coworktree` for worktree operations
when the binary is available, while falling back to `git worktree`.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from autowt.config import Config, set_config
from autowt.services.git import GitService


def test_create_worktree_uses_coworktree_when_available() -> None:
    repo_path = Path("/repo")
    worktree_path = Path("/repo-wt")

    config = Config.from_dict({"worktree": {"prefer_coworktree": True}})
    set_config(config)

    with patch("shutil.which", return_value="/usr/local/bin/coworktree"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            service = GitService()
            assert service.create_worktree(repo_path, "my-branch", worktree_path)

            cmd = mock_run.call_args[0][0]
            assert cmd[0] == "coworktree"


def test_create_worktree_uses_git_when_coworktree_unavailable() -> None:
    repo_path = Path("/repo")
    worktree_path = Path("/repo-wt")

    config = Config.from_dict({"worktree": {"prefer_coworktree": True}})
    set_config(config)

    with patch("shutil.which", return_value=None):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            service = GitService()
            assert service.create_worktree(repo_path, "my-branch", worktree_path)

            cmd = mock_run.call_args[0][0]
            assert cmd[:2] == ["git", "worktree"]


def test_create_worktree_uses_git_when_preference_disabled() -> None:
    repo_path = Path("/repo")
    worktree_path = Path("/repo-wt")

    config = Config.from_dict({"worktree": {"prefer_coworktree": False}})
    set_config(config)

    with patch("shutil.which", return_value="/usr/local/bin/coworktree"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            service = GitService()
            assert service.create_worktree(repo_path, "my-branch", worktree_path)

            cmd = mock_run.call_args[0][0]
            assert cmd[:2] == ["git", "worktree"]
