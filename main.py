"""
Program entry point.
"""
import datetime

from process_data import DataManager
from user_interface import UserInterface

if __name__ == '__main__':
    manager = DataManager(
        sources={
            'data/covid-usa.csv',
            'data/stock-snp500.csv'
        },
        start=datetime.date(2020, 1, 1),
        end=datetime.date(2021, 1, 1)
    )
    gui = UserInterface(
        data_source=manager
    )
    gui.run()
