"""COVID-19 Economics - User Interface

This module consists of all the user interface code for the project.  By itself
this file does not do any data processing, it only handles taking user input and
calling the appropriate backend interface (or retrieving the values from a
cache).

This file is Copyright (C) 2021, Theodore Preduta and Jacob Kolyakov.
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from plotly.graph_objs import Figure  # for type contracts

from data_management import DataManager
from config import LONG_NAMES, ALL_STOCKS, ALL_COUNTRIES


class UserInterface:
    """Class that holds all the state necessary to display the statistical data
    visually and interactively.

    Representation Invariants:
        - self._source is not None
        - self._app is not None
        - self._global_trend_cache is not None
        - self._local_trend_cache is not None

    >>> import datetime
    >>> dm = DataManager({'data/stock-snp500.csv', 'data/covid-usa.csv'}, \
                         datetime.date(2021, 1, 1), datetime.date(2021, 1, 10))
    >>> ui = UserInterface(dm)
    """
    # Private Instance Attributes:
    #     - _app: The dash web application that will display the data and handle coordinating
    #             update requests.
    #     - _source: The backend source of data to be displayed.  The _source provides an interface
    #                for the graph data.
    #     - _global_trend_cache: A mapping from a unique id of a set of graphed data to the data
    #                            itself.  This allows us to skip noticeably slower calculations.
    #     - _local_trend_cache: A mapping from a unique id of a graphed datapoint to the data
    #                           itself.  This allows us to skip noticeably slower calculations.
    _app: dash.Dash
    _source: DataManager
    _global_trend_cache: dict[str, list[float]]
    _local_trend_cache: dict[str, float]

    def __init__(self, data_source: DataManager) -> None:
        """Setup the user interface to use data_source to calculate statistics.

        Preconditions:
            - data_source is not None
        """
        self._source = data_source
        self._global_trend_cache = {}
        self._local_trend_cache = {}

        self._app = dash.Dash(__name__)

        # setup the app layout
        self._app.layout = html.Div(className='content', children=[
            html.H1('Global Trends'),
            dcc.Graph(id='global-graph'),
            make_control_widget('global', []),
            html.Hr(),
            html.H1('Local Trends'),
            dcc.Graph(id='local-graph'),
            make_control_widget('local', extra_controls=[
                html.Div(className='large-control', children=[
                    html.H4('Maximum Market Reaction Time (days)'),
                    dcc.Slider(
                        id='local-max-days',
                        min=0,
                        max=90,
                        step=1,
                        marks={x * 10: str(x * 10) for x in range(10)},
                        value=0
                    )
                ])
            ]),
            html.Hr(),
            html.P(
                'Copyright \u00A9 2021, Theodore Preduta and Jacob Kolyakov.',
                className='copyright-text'
            ),
            html.Br(),
            html.Br()
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

    def run(self, debug: bool = False) -> None:
        """Start the user interface.
        """
        self._app.run_server(debug=debug, port=8050)

    def _update_global_weekly_trends(self, stream: str,
                                     countries: list[str], stocks: list[str]) -> Figure:
        """Return an updated graph to display given the user wants to view the data from the
        combinations of countries with stocks with stream stock stream.

        Preconditions:
            - stream in {'open', 'close', 'high', 'low'}
            - all(c in ALL_COUNTRIES for c in countries)
            - all(s in ALL_STOCKS for c in stocks)
        """
        combinations = [(c, s) for c in countries for s in stocks]

        data = {}

        for country, stock in combinations:
            label = f'{LONG_NAMES[country]} v. {LONG_NAMES[stock]}'

            metric_id = f'{country}-{stock}-{stream}'
            if metric_id not in self._global_trend_cache:
                stats = self._source.get_global_statistics(stream, 90, stock, country)
                self._global_trend_cache[metric_id] = stats

            data[label] = self._global_trend_cache[metric_id]

        figure = px.line(data)
        figure.update_xaxes(title_text='Shift (days)')
        figure.update_yaxes(title_text='Correlation Coefficient')
        return figure

    def _update_local_weekly_trends(self, stream: str, countries: list[str], stocks: list[str],
                                    max_days: int) -> Figure:
        """Return an updated graph to display given the user wants to view the data from the
        combinations of countries with stock stream stock stream given a maximum reaction time
        of max_days.

        Preconditions:
            - stream in {'open', 'close', 'high', 'low'}
            - all(c in ALL_COUNTRIES for c in countries)
            - all(s in ALL_STOCKS for c in stocks)
            - max_days >= 0
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


def make_control_widget(id_prefix: str, extra_controls: list[html.Div]) -> html.Div:
    """Make an instance of a control widget containing the list of possible countries and
    stocks along with a stock stream selector, all with id id_prefix-<widget>.  If extra_controls
    is not empty, the the contents of extra_controls will be added before the stock stream widget.

    Preconditions:
        - id_prefix != ''
    """
    return html.Div(className='controls', children=[
        *extra_controls,
        html.Div(className='control', children=[
            html.H4('Stock Stream'),
            dcc.Dropdown(
                id=f'{id_prefix}-stream',
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
                id=f'{id_prefix}-countries',
                options=[{'label': LONG_NAMES[country], 'value': country}
                         for country in ALL_COUNTRIES],
                value=list(ALL_COUNTRIES),
            ),
        ]),
        html.Div(className='control', children=[
            html.H4('Stocks'),
            dcc.Checklist(
                id=f'{id_prefix}-stocks',
                options=[{'label': LONG_NAMES[stock], 'value': stock}
                         for stock in ALL_STOCKS],
                value=list(ALL_STOCKS)
            )
        ]),
    ])


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
