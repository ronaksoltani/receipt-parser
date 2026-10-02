from receipt_parser.parser import parse_receipt


def test_receipt_fields_are_typed_and_currency_normalized():
    result = parse_receipt("Corner Cafe\n03/14/2026\nSubtotal $12.00\nTax $1.20\nTotal $13.20")
    assert result.merchant == "Corner Cafe"
    assert str(result.total) == "13.20"
    assert result.currency == "USD"


def test_ambiguous_fields_remain_empty_and_explain_why():
    result = parse_receipt("Corner Cafe\nItems purchased")
    assert result.total is None
    assert result.currency is None
    assert len(result.warnings) == 2
