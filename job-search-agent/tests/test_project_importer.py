"""
tests/test_project_importer.py
----------------------------------
Tests for the GitHub Project Importer.

No real GitHub or Anthropic API calls here: `build_repo_source_text` is
pure Python, and the agent test uses a fake LLM provider plus a plain
dict standing in for a GitHub API repo response.
"""

from agents.fact_checking import verify_claims_against_text
from agents.project_importer import (
    LLMProjectDraft,
    ProjectImportAgent,
    build_repo_source_text,
)
from integrations.llm.base import LLMProvider

FAKE_REPO = {
    "name": "movie-rec-app",
    "description": "A movie recommendation web app using collaborative filtering.",
    "language": "Python",
    "topics": ["machine-learning", "streamlit"],
    "stargazers_count": 12,
    "html_url": "https://github.com/testuser/movie-rec-app",
}
FAKE_README = """
# Movie Recommendation App

Built with Python, Pandas, and Scikit-learn. Deployed with Streamlit.
Trained on the MovieLens 100K dataset (100,000 ratings, 943 users).
"""


def test_build_repo_source_text_includes_repo_and_readme_facts():
    source_text = build_repo_source_text(FAKE_REPO, FAKE_README)
    assert "movie-rec-app" in source_text
    assert "collaborative filtering" in source_text
    assert "streamlit" in source_text
    assert "MovieLens 100K" in source_text


def test_build_repo_source_text_handles_missing_readme():
    source_text = build_repo_source_text(FAKE_REPO, None)
    assert "movie-rec-app" in source_text


def test_claims_grounded_in_readme_verify():
    source_text = build_repo_source_text(FAKE_REPO, FAKE_README)
    verified, unverified = verify_claims_against_text(
        ["Python", "Scikit-learn", "Streamlit", "100000 ratings"], source_text
    )
    assert verified == ["Python", "Scikit-learn", "Streamlit", "100000 ratings"]
    assert unverified == []


def test_claim_not_in_repo_or_readme_is_flagged():
    source_text = build_repo_source_text(FAKE_REPO, FAKE_README)
    verified, unverified = verify_claims_against_text(["Kubernetes deployment"], source_text)
    assert unverified == ["Kubernetes deployment"]


# ---------------------------------------------------------------------------
# End-to-end agent test with a fake LLM provider (no real API calls)
# ---------------------------------------------------------------------------


class FakeLLMProvider(LLMProvider):
    def __init__(self, canned_response):
        self._canned_response = canned_response

    def complete_structured(self, system_prompt, user_prompt, output_model):
        assert output_model is LLMProjectDraft
        return self._canned_response


def test_agent_import_repo_end_to_end_with_fake_llm():
    draft = LLMProjectDraft(
        name="Movie Recommendation App",
        description="A web app that recommends movies using collaborative filtering.",
        bullets=[
            "Built a collaborative filtering recommender trained on the MovieLens 100K dataset.",
            "Deployed the app publicly using Streamlit.",
        ],
        technologies=["Python", "Pandas", "Scikit-learn", "Streamlit"],
        claims_referenced=["Python", "Scikit-learn", "Streamlit", "MovieLens 100K", "Kubernetes"],
    )
    agent = ProjectImportAgent(llm_provider=FakeLLMProvider(draft))

    result = agent.import_repo(FAKE_REPO, FAKE_README)

    assert result.project.name == "Movie Recommendation App"
    assert result.project.url == "https://github.com/testuser/movie-rec-app"
    assert "Python" in result.verified_claims
    assert "Kubernetes" in result.unverified_claims
