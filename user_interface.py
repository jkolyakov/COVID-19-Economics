"""
User interface code.

This is the front end.
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from plotly.graph_objs import Figure

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
    _local_trend_cache: dict[str, float]

    def __init__(self, data_source: DataManager, countries: set[str], stocks: set[str]) -> None:
        """Setup the user interface to use data_source to calculate statistics.

        Preconditions:
            - data_source is not None

        TODO doctests?
        """
        self._source = data_source
        self._global_trend_cache = {}
        self._local_trend_cache = {}

        self._app = dash.Dash(__name__)

        # setup the app layout
        self._app.layout = html.Div(className='content', children=[
            html.H1('Global Trends'),
            dcc.Graph(id='global-graph'),
            html.Div(className='controls', children=[
                html.Div(className='control', children=[
                    html.H4('Stock Stream'),
                    dcc.Dropdown(
                        id='global-stream',
                        options=[{'label': 'Open', 'value': 'open'},
                                 {'label': 'High', 'value': 'high'},
                                 {'label': 'Low', 'value': 'low'},
                                 {'label': 'Close', 'value': 'close'}],
                        value='open',
                        clearable=False
                    )
                ]),
                html.Div(className='control', children=[
                    html.H4('Countries'),
                    dcc.Checklist(
                        id='global-countries',
                        options=[{'label': LONG_NAMES[country], 'value': country}
                                 for country in countries],
                        value=list(countries),
                    ),
                ]),
                html.Div(className='control', children=[
                    html.H4('Stocks'),
                    dcc.Checklist(
                        id='global-stocks',
                        options=[{'label': LONG_NAMES[stock], 'value': stock}
                                 for stock in stocks],
                        value=list(stocks)
                    )
                ]),
            ]),
            html.Hr(),
            html.H1('Local Trends'),
            dcc.Graph(id='local-graph'),
            html.Div(className='controls', children=[
                html.Div(className='large-control', children=[
                    html.H4('Maximum Market Reaction Time (days)'),
                    dcc.Slider(
                        id='local-max-days',
                        min=0,
                        max=30,
                        step=1,
                        marks={
                            0: '0',
                            10: '10',
                            20: '20',
                            30: '30'
                        }
                    )
                ]),
                html.Div(className='control', children=[
                    html.H4('Stock Stream'),
                    dcc.Dropdown(
                        id='local-stream',
                        options=[{'label': 'Open', 'value': 'open'},
                                 {'label': 'High', 'value': 'high'},
                                 {'label': 'Low', 'value': 'low'},
                                 {'label': 'Close', 'value': 'close'}],
                        value='open',
                        clearable=False
                    )
                ]),
                html.Div(className='control', children=[
                    html.H4('Countries'),
                    dcc.Checklist(
                        id='local-countries',
                        options=[{'label': LONG_NAMES[country], 'value': country}
                                 for country in countries],
                        value=list(countries),
                    ),
                ]),
                html.Div(className='control', children=[
                    html.H4('Stocks'),
                    dcc.Checklist(
                        id='local-stocks',
                        options=[{'label': LONG_NAMES[stock], 'value': stock}
                                 for stock in stocks],
                        value=list(stocks)
                    )
                ])
            ]),
            html.Hr(),
            html.P(
                'Copyright \u00A9 2021, Theodore Preduta and Jacob Kolyakov.',
                className='copyright-text'
            )
        ])

        # add update methods
        self._app.callback(
            Output(component_id='global-graph', component_property='figure'),
            [Input(component_id='global-stream', component_property='value'),
             Input(component_id='global-countries', component_property='value'),
             Input(component_id='global-stocks', component_property='value')]
        )(self._update_global_weekly_trends)

        self._app.callback(
            Output(component_id='local-graph', component_property='figure'),
            [Input(component_id='local-stream', component_property='value'),
             Input(component_id='local-countries', component_property='value'),
             Input(component_id='local-stocks', component_property='value'),
             Input(component_id='local-max-days', component_property='value')]
        )(self._update_local_weekly_trends)

    def run(self) -> None:
        """Start the user interface.
        """
        self._app.run_server(debug=True)

    def _update_global_weekly_trends(self, stream: str,
                                     countries: list[str], stocks: list[str]) -> Figure:
        """Create the plotly graph for the global trends graph. TODO better description

        Preconditions:
            - TODO
        """
        combinations = [(c, s) for c in countries for s in stocks]

        data = {}

        for country, stock in combinations:
            label = f'{LONG_NAMES[country]} v. {LONG_NAMES[stock]}'

            metric_id = f'{country}-{stock}-{stream}'
            if metric_id not in self._global_trend_cache:
                stats = self._source.get_global_statistics(stream, 100, stock, country)
                self._global_trend_cache[metric_id] = stats

            data[label] = self._global_trend_cache[metric_id]

        return px.line(data)  # TODO name the axis

    def _update_local_weekly_trends(self, stream: str, countries: list[str], stocks: list[str],
                                    max_days: int) -> Figure:
        """Create the plotly for the local trends graph. TODO better description

        Preconditions:
            - TODO
        """
        combinations = [(c, s) for c in countries for s in stocks]

        data = {'Country/Stock Combination': [], 'Correlation Coefficient': []}

        for country, stock in combinations:
            metric_id = f'{country}-{stock}-{stream}-{max_days}'
            if metric_id not in self._local_trend_cache:
                stat = self._source.get_local_statistics(stream, stock, country, max_days)
                self._local_trend_cache[metric_id] = stat

            data['Country/Stock Combination']\
                .append(f'{LONG_NAMES[country]} v. {LONG_NAMES[stock]}')
            data['Correlation Coefficient'].append(self._local_trend_cache[metric_id])

        return px.bar(data, x='Country/Stock Combination', y='Correlation Coefficient')


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['dash', 'dash.dependencies', 'plotly.express', 'plotly.graph_objs',
                          'data_management', 'config'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
