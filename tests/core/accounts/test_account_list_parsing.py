from geth.accounts import (
    parse_geth_accounts,
)

raw_accounts = b"""Account #0: {8c28b76a845f525a7f91149864574d3a4986e693}
keystore:///private/tmp/pytest-of-pygeth/pytest-1/test_with_no_overrides0/base-dir
/testing/keystore/UTC--2024-06-19T20-40-51.284430000Z
--8c28b76a845f525a7f91149864574d3a4986e693\n
Account #1: {6f137a71a6f197df2cbbf010dcbd3c444ef5c925} keystore:///private/tmp
/pytest-of-pygeth/pytest-1/test_with_no_overrides0/base-dir
/testing/keystore/UTC--2024-06-19T20-40-51.284430000Z
--6f137a71a6f197df2cbbf010dcbd3c444ef5c925\n"""
accounts = (
    "0x8c28b76a845f525a7f91149864574d3a4986e693",
    "0x6f137a71a6f197df2cbbf010dcbd3c444ef5c925",
)


def test_parsing_accounts_output():
    assert sorted(list(parse_geth_accounts(raw_accounts))) == sorted(list(accounts))
