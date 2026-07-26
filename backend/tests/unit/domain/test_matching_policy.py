from __future__ import annotations

from app.domain.entities.job_description import JobRequirement
from app.domain.entities.resume import ContactInfo, Resume
from app.domain.services.matching_policy import MatchingPolicy


def test_finds_best_matching_bullet(sample_resume, fake_embedder):
    policy = MatchingPolicy(embedder=fake_embedder, similarity_threshold=0.3)
    requirement = JobRequirement(
        text="Experience with scalable REST APIs", requirement_type="experience"
    )

    evidence = policy.match_requirement_to_resume(requirement, sample_resume)

    assert evidence.passed is True
    assert "REST API" in evidence.source_span
    assert evidence.criterion == "semantic_match:experience"


def test_below_threshold_fails(sample_resume, fake_embedder):
    policy = MatchingPolicy(embedder=fake_embedder, similarity_threshold=0.99)
    # Only partially overlaps the best candidate bullet ("database" matches,
    # "scaling" does not -- the resume says "scalable", a distinct token in
    # the fake embedder's vocabulary), so similarity lands well below 0.99.
    requirement = JobRequirement(
        text="Database scaling improvements needed", requirement_type="experience"
    )

    evidence = policy.match_requirement_to_resume(requirement, sample_resume)
    assert evidence.passed is False
    assert evidence.found_value < 0.99


def test_no_candidate_text_returns_failed_zero_confidence_evidence(fake_embedder):
    empty_resume = Resume(raw_text="", contact_info=ContactInfo())
    policy = MatchingPolicy(embedder=fake_embedder)
    requirement = JobRequirement(text="anything", requirement_type="experience")

    evidence = policy.match_requirement_to_resume(requirement, empty_resume)

    assert evidence.passed is False
    assert evidence.confidence == 0.0
    assert evidence.found_value is None
