from __future__ import annotations

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.category_scorers.base import ICategoryScorer, aggregate_evidence

REQUIRED_CERT_WEIGHT = 1.5


class CertificationsScorer(ICategoryScorer):
    category = ScoreCategory.CERTIFICATIONS

    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        if not job_description.required_certifications:
            return aggregate_evidence(self.category, [])

        resume_certs = {c.name.strip().lower() for c in resume.certifications}

        evidence = []
        for required_cert in job_description.required_certifications:
            found = required_cert.strip().lower() in resume_certs
            evidence.append(
                Evidence(
                    criterion="required_certification_present",
                    description=f"Required certification '{required_cert}'",
                    found_value=found,
                    expected_value=True,
                    weight=REQUIRED_CERT_WEIGHT,
                    passed=found,
                    confidence=1.0,
                )
            )

        return aggregate_evidence(self.category, evidence)
