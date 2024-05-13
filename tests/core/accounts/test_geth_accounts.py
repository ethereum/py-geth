from geth.accounts import (
    get_accounts,
)


def test_single_account(one_account_data_dir):
    data_dir = one_account_data_dir
    accounts = get_accounts(data_dir=data_dir)
    assert tuple(set(accounts)) == ("0xae71658b3ab452f7e4f03bda6f777b860b2e2ff2",)


def test_multiple_accounts(three_account_data_dir):
    data_dir = three_account_data_dir
    accounts = get_accounts(data_dir=data_dir)
    assert sorted(tuple(set(accounts))) == sorted(
        (
            "0xae71658b3ab452f7e4f03bda6f777b860b2e2ff2",
            "0xe8e085862a8d951dd78ec5ea784b3e22ee1ca9c6",
            "0x0da70f43a568e88168436be52ed129f4a9bbdaf5",
        )
    )


def test_no_accounts(no_account_data_dir):
    data_dir = no_account_data_dir
    accounts = get_accounts(data_dir=data_dir)
    assert accounts == tuple()
