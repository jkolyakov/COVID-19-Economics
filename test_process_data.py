"""
Test process_data.py.
"""
# TODO fix this file
import datetime

from hypothesis import given
from hypothesis.strategies import integers, text

from records import CovidRecord, StockRecord
from process_data import differentiate_stock_data


def test_differentiate_stock_data_2_days() -> None:
    """Test differentiate_stock_data on a 2 day sample.

    Note that we are intentioally abusing the type contract so that we can avoid
    floating point erros in this test.
    """
    yesterday = StockRecord('snp500', datetime.date(2021, 1, 1), 1, 1, 1, 1)
    today = StockRecord('snp500', datetime.date(2021, 1, 2), 10, 0, 20, 5)
    expected = [StockRecord('snp500', datetime.date(2021, 1, 2), 9, -1, 19, 4)]
    actual = differentiate_stock_data([yesterday, today])
    assert actual == expected


def test_differentiate_stock_data_3_days() -> None:
    """Test differentiate_stock_data on a 3 day sample.
    """
    yesterday = StockRecord('snp500', datetime.date(2021, 1, 1), 1, 1, 1, 1)
    today = StockRecord('snp500', datetime.date(2021, 1, 2), 10, 0, 2, 7)
    tomorrow = StockRecord('snp500', datetime.date(2021, 1, 3), 0, 0, 0, 0)
    expected = [StockRecord('snp500', datetime.date(2021, 1, 2), 9, -1, 1, 6),
                StockRecord('snp500', datetime.date(2021, 1, 3), -10, 0, -2, -7)]
    actual = differentiate_stock_data([yesterday, today, tomorrow])
    assert actual == expected
