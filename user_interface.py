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

    def __init__(self, data_source: DataManager, countries: dict[str, str],
                 stocks: dict[str, str]) -> None:
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
            html.H2('Global Weekly Trends'),
            dcc.Graph(id='global-weekly-graph'),
            dcc.Slider(
                id='global-weekly-days',
                min=0,
                max=31,
                step=1,
                value=0,
                marks={x: f'{x}' for x in range(32)}
            ),
            dcc.Dropdown(
                id='global-weekly-stream',
                options=[{'label': 'Open', 'value': 'open'},
                         {'label': 'High', 'value': 'high'},
                         {'label': 'Low', 'value': 'low'},
                         {'label': 'Close', 'value': 'close'}],
                value='open'
            ),
            dcc.Checklist(
                id='global-weekly-countries',
                options=[{'label': countries[country], 'value': country}
                         for country in countries],
                value=[country for country in countries]
            ),
            dcc.Checklist(
                id='global-weekly-stocks',
                options=[{'label': stocks[stock], 'value': stock}
                         for stock in stocks],
                value=[stock for stock in stocks]
            ),
            html.H2('Local Weekly Trends'),
            dcc.Graph(id='local-weekly-graph'),
            dcc.Slider(
                id='local-weekly-threshold',
                min=0,
                max=10000,
                step=100,
                value=0,
                marks={x: f'{x}' for x in range(0, 10000, 1000)}
            ),
            dcc.Dropdown(
                id='local-weekly-stream',
                options=[{'label': 'Open', 'value': 'open'},
                         {'label': 'High', 'value': 'high'},
                         {'label': 'Low', 'value': 'low'},
                         {'label': 'Close', 'value': 'close'}],
                value='open'
            ),
            dcc.Checklist(
                id='local-weekly-countries',
                options=[{'label': countries[country], 'value': country}
                         for country in countries],
                value=[country for country in countries]
            ),
            dcc.Checklist(
                id='local-weekly-stocks',
                options=[{'label': stocks[stock], 'value': stock}
                         for stock in stocks],
                value=[stock for stock in stocks]
            )
        ])

        # add update methods
        self._app.callback(
            Output(component_id='global-weekly-graph', component_property='figure'),
            [Input(component_id='global-weekly-days', component_property='value'),
             Input(component_id='global-weekly-stream', component_property='value'),
             Input(component_id='global-weekly-countries', component_property='value'),
             Input(component_id='global-weekly-stocks', component_property='value')]
        )(self._update_global_weekly_trends)

        self._app.callback(
            Output(component_id='local-weekly-graph', component_property='figure'),
            [Input(component_id='local-weekly-stream', component_property='value'),
             Input(component_id='local-weekly-countries', component_property='value'),
             Input(component_id='local-weekly-stocks', component_property='value'),
             Input(component_id='local-weekly-threshold', component_property='value')]
        )(self._update_local_weekly_trends)

    def run(self) -> None:
        """Start the user interface.
        """
        self._app.run_server(debug=True)

    def _update_global_weekly_trends(self, days: int, stream: str,
                                     countries: list[str], stocks: list[str]):
        """Create the plotly graph for the global trends graph. TODO better description

        TODO cache :) (this is where the fun starts)

        Preconditions:
            - TODO
        """
        combinations = [(country, stock) for country in countries for stock in stocks]

        data = {}

        for country, stock in combinations:
            label = f'{country}-{stock}'
            data[label] = self._source.get_weekly_global_statistics(stream, days, stock, country)

        return px.line(data)

    def _update_local_weekly_trends(self, stream: str, countries: list[str], stocks: list[str],
                                    threshold: int):
        """Create the plotly for the local trends graph. TODO better description

        TODO cache :) (this is where the fun starts)

        Preconditions:
            - TODO
        """
        combinations = [(country, stock) for country in countries for stock in stocks]

        data = {}

        for country, stock in combinations:
            label = f'{country}-{stock}'
            data[label] = self._source.get_weekly_local_statistics(stream, stock,
                                                                   country, threshold)

        return px.line(data)
