"""
User interface code.
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.express as px

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
            html.H2('Global Trends'),  # currently just a plot of x^<slider>
            dcc.Graph(id='global-trends-graph'),
            dcc.Slider(
                id='global-trends-slider',
                min=-5,
                max=5,
                step=0.25,
                marks={
                    -5: '-5',
                    -1: '-1',
                    0: '0',
                    1: '1',
                    5: '5'
                },
                value=0
            )
        ])

        # add update methods
        self._app.callback(
            Output(component_id='global-trends-graph', component_property='figure'),
            [Input(component_id='global-trends-slider', component_property='value')]
        )(self._update_global_trends)

    def run(self) -> None:
        """Start the user interface.
        """
        self._app.run_server(debug=True)



    def _update_global_trends(self, threshold: float):
        """TODO this function currently just outputs an equation

        It mostly acts as a slider test at this point
        """
        return px.line(
            {f'x^{threshold}': [(x / 10) ** threshold for x in range(1, 100)]},
        )

    def _update_local_trends(self):
        """TODO
        """
        pass
