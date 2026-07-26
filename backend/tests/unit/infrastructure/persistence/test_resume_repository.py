from __future__ import annotations

from app.infrastructure.persistence.resume_repository import SQLAlchemyResumeRepository


def test_save_and_get_by_id_round_trips_resume(db_session, full_resume):
    repo = SQLAlchemyResumeRepository(db_session)

    record = repo.save(full_resume, filename="resume.pdf")
    fetched = repo.get_by_id(record.id)

    assert fetched is not None
    assert fetched.resume == full_resume
    assert fetched.filename == "resume.pdf"
    assert fetched.user_id is None


def test_save_associates_user_id(db_session, full_resume, make_test_user):
    repo = SQLAlchemyResumeRepository(db_session)
    user_id = make_test_user()
    record = repo.save(full_resume, filename="r.pdf", user_id=user_id)
    assert record.user_id == user_id


def test_get_by_id_returns_none_for_missing_record(db_session):
    repo = SQLAlchemyResumeRepository(db_session)
    assert repo.get_by_id("00000000-0000-0000-0000-000000000000") is None


def test_list_by_user_returns_only_that_users_resumes(db_session, full_resume, make_test_user):
    repo = SQLAlchemyResumeRepository(db_session)
    user_a = make_test_user("user-a@example.com")
    user_b = make_test_user("user-b@example.com")

    repo.save(full_resume, filename="a1.pdf", user_id=user_a)
    repo.save(full_resume, filename="a2.pdf", user_id=user_a)
    repo.save(full_resume, filename="b1.pdf", user_id=user_b)

    results = repo.list_by_user(user_a)

    assert len(results) == 2
    assert {r.filename for r in results} == {"a1.pdf", "a2.pdf"}


def test_list_by_user_orders_most_recent_first(db_session, full_resume, make_test_user):
    repo = SQLAlchemyResumeRepository(db_session)
    user = make_test_user()

    first = repo.save(full_resume, filename="first.pdf", user_id=user)
    second = repo.save(full_resume, filename="second.pdf", user_id=user)

    results = repo.list_by_user(user)
    assert results[0].id == second.id
    assert results[1].id == first.id


def test_delete_removes_record(db_session, full_resume):
    repo = SQLAlchemyResumeRepository(db_session)
    record = repo.save(full_resume, filename="r.pdf")

    deleted = repo.delete(record.id)
    assert deleted is True
    assert repo.get_by_id(record.id) is None


def test_delete_returns_false_for_missing_record(db_session):
    repo = SQLAlchemyResumeRepository(db_session)
    assert repo.delete("00000000-0000-0000-0000-000000000000") is False
