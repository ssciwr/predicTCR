import argon2
from predicTCR_server.model import User, Sample, db, Status
import pathlib


def add_test_users(app):
    ph = argon2.PasswordHasher()
    with app.app_context():
        for name, is_admin, is_runner in [
            ("admin", True, False),
            ("user", False, False),
            ("runner", False, True),
        ]:
            email = f"{name}@abc.xy"
            db.session.add(
                User(
                    email=email,
                    password_hash=ph.hash(name),
                    activated=True,
                    enabled=True,
                    quota=1,
                    last_submission_timestamp=0,
                    is_admin=is_admin,
                    is_runner=is_runner,
                )
            )
            db.session.commit()


def add_test_samples(app, data_path: pathlib.Path):
    with app.app_context():
        for sample_id, name in zip(
            [1, 2, 3, 4],
            [
                "s1",
                "s2",
                "s3",
                "s4",
            ],
        ):
            ref_dir = data_path / f"{sample_id}"
            ref_dir.mkdir(parents=True, exist_ok=True)
            for input_file_type in ["h5", "csv"]:
                with open(f"{ref_dir}/input.{input_file_type}", "w") as f:
                    f.write(input_file_type)
            new_sample = Sample(
                email="user@abc.xy",
                name=name,
                tumor_type=f"tumor_type{sample_id}",
                source=f"source{sample_id}",
                timestamp=sample_id,
                status=Status.QUEUED,
                has_results_zip=False,
            )
            db.session.add(new_sample)
            db.session.commit()
