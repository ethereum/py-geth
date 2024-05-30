import os

from geth.accounts import (
    create_new_account,
    get_accounts,
)


def test_create_new_account_with_text_password(tmpdir):
    data_dir = str(tmpdir.mkdir("data-dir"))

    assert not get_accounts(data_dir=data_dir)

    account_0 = create_new_account(data_dir=data_dir, password=b"some-text-password")
    account_1 = create_new_account(data_dir=data_dir, password=b"some-text-password")

    accounts = get_accounts(data_dir=data_dir)
    assert sorted((account_0, account_1)) == sorted(tuple(set(accounts)))


def test_create_new_account_with_file_based_password(tmpdir):
    pw_file_path = str(tmpdir.mkdir("data-dir").join("geth_password_file"))

    with open(pw_file_path, "w") as pw_file:
        pw_file.write("some-text-password-in-a-file")

    data_dir = os.path.dirname(pw_file_path)

    assert not get_accounts(data_dir=data_dir)

    account_0 = create_new_account(data_dir=data_dir, password=pw_file_path)
    account_1 = create_new_account(data_dir=data_dir, password=pw_file_path)

    accounts = get_accounts(data_dir=data_dir)
    assert sorted((account_0, account_1)) == sorted(tuple(set(accounts)))
