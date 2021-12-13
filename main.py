"""COVID-19 Economics - Project Entry Point

This module consists of the entry point of this program.  Running

    python3 main.py

in your shell will start the project's user interface which can be visited by
pointing your browser to localhost:8050.

This file is Copyright (C) 2021, Theodore Preduta and Jacob Kolyakov.
"""
from data_management import DataManager
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
