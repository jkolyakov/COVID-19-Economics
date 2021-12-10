"""
User interface code.
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from process_data import DataManager


class UserInterface:
    """Class that holds all the state necessary to display the statistical data
    visually and interactively.

    TODO Sample class setup
    """
    _app: dash.Dash
    _source: DataManager

    def __init__(self, data_source: DataManager) -> None:
        """Setup the user interface to use data_source to calculate statistics.

        Preconditions:
            - data_source is not None

        TODO doctests?
        """
        self._source = data_source

        self._app = dash.Dash(
            __name__,
            external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
            # TODO we should really be writing our own css instead of just using this
        )

        # setup the app layout
        self._app.layout = html.Div([
            html.H6("Change the value in the text box to see callbacks in action!"),
            html.Div([
                "Input: ",
                dcc.Input(id='my-input', value='initial value', type='text')
            ]),
            html.Br(),
            html.Div(id='my-output'),
        ])  # TODO delete this

        # add update methods
        self._app.callback(
            Output(component_id='my-output', component_property='children'),
            Input(component_id='my-input', component_property='value')
        )(self._update_output_div)  # TODO delete this

    def run(self) -> None:
        """Start the user interface.
        """
        self._app.run_server(debug=True)

    def _update_output_div(self, input_value: str) -> str:
        """TODO delete this
        """
        return 'Output: {}'.format(input_value)

