from __future__ import annotations

from datetime import date

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import ContactInfo, DateRange, ExperienceEntry, Resume
from app.domain.services.category_scorers.experience_scorer import ExperienceScorer
from app.domain.services.matching_policy import MatchingPolicy


def test_meets_years_requirement(sample_resume, sample_job_description):
    scorer = ExperienceScorer()
    result = scorer.score(sample_resume, sample_job_description)

    years_evidence = next(e for e in result.evidence if e.criterion == "years_required_vs_found")
    assert years_evidence.passed is True
    assert years_evidence.found_value >= sample_job_description.min_years_experience


def test_fails_years_requirement_when_insufficient():
    resume = Resume(
        raw_text="",
        contact_info=ContactInfo(),
        experience=[
            ExperienceEntry(
                title="Intern",
                company="X",
                date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 4, 1)),
            )
        ],
    )
    jd = JobDescription(raw_text="", title="Senior Eng", min_years_experience=5.0)

    scorer = ExperienceScorer()
    result = scorer.score(resume, jd)

    years_evidence = next(e for e in result.evidence if e.criterion == "years_required_vs_found")
    assert years_evidence.passed is False
    assert years_evidence.found_value < 5.0


def test_detects_employment_gap_over_threshold():
    resume = Resume(
        raw_text="",
        contact_info=ContactInfo(),
        experience=[
            ExperienceEntry(
                title="Eng A",
                company="X",
                date_range=DateRange(start=date(2019, 1, 1), end=date(2019, 6, 1)),
            ),
            # 10-month gap
            ExperienceEntry(
                title="Eng B",
                company="Y",
                date_range=DateRange(start=date(2020, 4, 1), end=date(2021, 1, 1)),
            ),
        ],
    )
    jd = JobDescription(raw_text="", title="Eng")

    scorer = ExperienceScorer()
    result = scorer.score(resume, jd)

    gap_evidence = [e for e in result.evidence if e.criterion == "employment_gap"]
    assert len(gap_evidence) == 1
    assert gap_evidence[0].passed is False
    assert gap_evidence[0].found_value == 10


def test_no_gap_evidence_for_contiguous_experience():
    resume = Resume(
        raw_text="",
        contact_info=ContactInfo(),
        experience=[
            ExperienceEntry(
                title="Eng A",
                company="X",
                date_range=DateRange(start=date(2019, 1, 1), end=date(2020, 1, 1)),
            ),
            ExperienceEntry(
                title="Eng B",
                company="Y",
                date_range=DateRange(start=date(2020, 1, 15), end=None),
            ),
        ],
    )
    jd = JobDescription(raw_text="", title="Eng")

    scorer = ExperienceScorer()
    result = scorer.score(resume, jd)

    gap_evidence = [e for e in result.evidence if e.criterion == "employment_gap"]
    assert len(gap_evidence) == 0


def test_semantic_matching_included_when_policy_provided(
    sample_resume, sample_job_description, fake_embedder
):
    matching_policy = MatchingPolicy(embedder=fake_embedder, similarity_threshold=0.3)
    scorer = ExperienceScorer(matching_policy=matching_policy)

    result = scorer.score(sample_resume, sample_job_description)

    semantic_evidence = [
        e for e in result.evidence if e.criterion.startswith("semantic_match")
    ]
    assert len(semantic_evidence) == 1
    # The JD requirement mentions "REST APIs" which overlaps with a resume bullet
    assert semantic_evidence[0].passed is True
    assert semantic_evidence[0].source_span is not None


def test_no_semantic_matching_when_policy_not_provided(
    sample_resume, sample_job_description
):
    scorer = ExperienceScorer(matching_policy=None)
    result = scorer.score(sample_resume, sample_job_description)
    semantic_evidence = [
        e for e in result.evidence if e.criterion.startswith("semantic_match")
    ]
    assert len(semantic_evidence) == 0
