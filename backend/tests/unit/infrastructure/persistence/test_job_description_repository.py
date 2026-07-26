from __future__ import annotations

from app.infrastructure.persistence.job_description_repository import (
    SQLAlchemyJobDescriptionRepository,
)


def test_save_and_get_by_id_round_trips_job_description(db_session, full_job_description):
    repo = SQLAlchemyJobDescriptionRepository(db_session)

    record = repo.save(full_job_description)
    fetched = repo.get_by_id(record.id)

    assert fetched is not None
    assert fetched.job_description == full_job_description


def test_get_by_id_returns_none_for_missing_record(db_session):
    repo = SQLAlchemyJobDescriptionRepository(db_session)
    assert repo.get_by_id("00000000-0000-0000-0000-000000000000") is None


def test_list_by_user_filters_correctly(db_session, full_job_description, make_test_user):
    repo = SQLAlchemyJobDescriptionRepository(db_session)
    user = make_test_user("user-a@example.com")
    other = make_test_user("user-b@example.com")

    repo.save(full_job_description, user_id=user)
    repo.save(full_job_description, user_id=other)

    results = repo.list_by_user(user)
    assert len(results) == 1
