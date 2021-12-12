"""
User interface code.

This is the front end.
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

from data_management import DataManager
from config import LONG_NAMES


class UserInterface:
    """Class that holds all the state necessary to display the statistical data
    visually and interactively.

    TODO Sample class setup
    """
    _app: dash.Dash
    _source: DataManager
    _global_trend_cache: dict[str, list[float]]

    def __init__(self, data_source: DataManager, countries: set[str], stocks: set[str]) -> None:
        """Setup the user interface to use data_source to calculate statistics.

        Preconditions:
            - data_source is not None

        TODO doctests?
        """
        self._source = data_source
        self._global_trend_cache = {}

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
                options=[{'label': LONG_NAMES[country], 'value': country}
                         for country in countries],
                value=list(countries)
            ),
            dcc.Checklist(
                id='global-weekly-stocks',
                options=[{'label': LONG_NAMES[stock], 'value': stock}
                         for stock in stocks],
                value=list(stocks)
            ),
            html.H2('Local Correlation'),
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
                options=[{'label': LONG_NAMES[country], 'value': country}
                         for country in countries],
                value=list(countries)
            ),
            dcc.Checklist(
                id='local-weekly-stocks',
                options=[{'label': LONG_NAMES[stock], 'value': stock}
                         for stock in stocks],
                value=list(stocks)
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
        combinations = [(c, s) for c in countries for s in stocks]

        data = {}

        for country, stock in combinations:
            label = f'{LONG_NAMES[country]} v. {LONG_NAMES[stock]}'
            metric_id = f'{days}-{country}-{stock}-{stream}'
            if metric_id not in self._global_trend_cache:
                stats = self._source.get_weekly_global_statistics(stream, days, stock, country)
                self._global_trend_cache[metric_id] = stats

            data[label] = self._global_trend_cache[metric_id]

        return px.line(data)

    def _update_local_weekly_trends(self, stream: str, countries: list[str], stocks: list[str],
                                    threshold: int):
        """Create the plotly for the local trends graph. TODO better description

        TODO cache :) (this is where the fun starts)

        Preconditions:
            - TODO
        """
        combinations = [(c, s) for c in countries for s in stocks]

        data = {'x_vals': [], 'Correlation Coefficient': []}

        for country, stock in combinations:
            data['x_vals'].append(f'{LONG_NAMES[country]} v. {LONG_NAMES[stock]}')
            data['Correlation Coefficient'].append(
                self._source.get_weekly_local_statistics(stream, stock, country, threshold))

        return px.bar(data, x='x_vals', y='Correlation Coefficient')


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['dash', 'dash.dependencies', 'plotly.express',
                          'data_management', 'config'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
