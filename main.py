"""COVID-19 Economics - Project Entry Point

This module consists of the entry point of this program.  Running

    python3 main.py

in your shell will start the project's user interface which can be visited by
pointing your browser to localhost:8050.

This file is Copyright (C) 2021, Theodore Preduta and Jacob Kolyakov.
"""
from data_management import DataManager
from user_interface import UserInterface
from config import DATA_FILES, START_DATE, END_DATE

if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()  # TODO delete before submisision

    manager = DataManager(
        sources=DATA_FILES,
        start=START_DATE,
        end=END_DATE
    )
    gui = UserInterface(manager)
    gui.run(debug=True)  # TODO turn debug off before submission
