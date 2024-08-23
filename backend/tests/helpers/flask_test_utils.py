import argon2
from predicTCR_server.model import User, Sample, db
import datetime
import pathlib
import shutil
import tempfile


def add_test_users(app):
    ph = argon2.PasswordHasher()
    with app.app_context():
        # add users for tests
        for name, is_admin in [("admin", True), ("user", False)]:
            email = f"{name}@embl.de"
            db.session.add(
                User(
                    email=email,
                    password_hash=ph.hash(name),
                    activated=True,
                    is_admin=is_admin,
                )
            )
            db.session.commit()


def add_test_samples(app, data_path: pathlib.Path):
    with app.app_context():
        # add samples for tests
        week = 46
        for n, name in zip(
            [1, 2, 3, 4],
            [
                "ref_seq",
                "ZIP_TEST_pMC_Final_Kan",
                "ZIP_TEST_pCW571",
                "ZIP_TEST_pDONR_amilCP",
            ],
        ):
            key = f"22_{week}_A{n}"
            ref_dir = data_path / "2022" / f"{week}" / "inputs" / "references"
            ref_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory() as tmp_dir:
                with open(f"{tmp_dir}/test.txt", "w") as f:
                    f.write(key)
                shutil.make_archive(f"{ref_dir}/{key}_{name}", "zip", tmp_dir)
            new_sample = Sample(
                email="user@embl.de",
                name=name,
                primary_key=key,
                tube_primary_key=key,
                running_option="running_option",
                concentration=100 + 13 * n,
                date=datetime.date.fromisocalendar(2022, week, n),
                has_reference_seq_zip=True,
                has_results_zip=False,
            )
            db.session.add(new_sample)
            db.session.commit()
