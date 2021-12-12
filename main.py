"""
Program entry point.
"""
import datetime

from process_data import DataManager
from user_interface import UserInterface

from config import DATA_FILES, START_DATE, END_DATE, ALL_COUNTRIES, ALL_STOCKS

if __name__ == '__main__':
    manager = DataManager(
        sources=DATA_FILES,
        start=START_DATE,
        end=END_DATE
    )
    gui = UserInterface(
        data_source=manager,
        countries=ALL_COUNTRIES,
        stocks=ALL_STOCKS
    )
    gui.run()
