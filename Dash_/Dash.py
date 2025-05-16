from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
available_countries = df['country'].unique()
available_continents = df['continent'].unique()
measures = ['pop', 'lifeExp', 'gdpPercap']
y_axes_options = measures

app = Dash(__name__)

app.layout = html.Div([

    html.H1("Title of Dash App", style={'textAlign':'center'}),

    html.Div([
        html.Label("Выберите страны для сравнения:"),
        dcc.Dropdown(
            options=[{'label': c, 'value': c} for c in available_countries],
            value=['Canada'],
            multi=True,
            id='countries-selector'
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Выберите диапазон лет:"),
        dcc.RangeSlider(
            min=int(df['year'].min()),
            max=int(df['year'].max()),
            step=1,
            value=[int(df['year'].min()), int(df['year'].max())],
            marks={str(year): str(year) for year in range(int(df['year'].min()), int(df['year'].max())+1, 5)},
            id='year-range-slider'
        )
    ], style={'width': '48%', 'display': 'inline-block', 'paddingLeft': '20px'}),

    html.Hr(),

    html.Div([
        html.H3("Линейный график: Популяция по годам"),
        dcc.Graph(id='line-graph')
    ]),

    html.Div([
        html.Label("Выберите меру для y-оси (линейный график):"),
        dcc.Dropdown(
            options=[{'label': m, 'value': m} for m in measures],
            value='pop',
            id='y-measure-dropdown'
        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        html.H3("Пузырьковая диаграмма"),
        html.Div([
            html.Label("Выберите x:"), dcc.Dropdown(
                options=[{'label': m, 'value': m} for m in measures],
                value='gdpPercap',
                id='bubble-x'
            ),
            html.Label("Выберите y:"), dcc.Dropdown(
                options=[{'label': m, 'value': m} for m in measures],
                value='lifeExp',
                id='bubble-y'
            ),
            html.Label("Выберите радиус:"), dcc.Dropdown(
                options=[{'label': m, 'value': m} for m in measures],
                value='pop',
                id='bubble-size'
            ),
        ], style={'columnCount': 3}),
        dcc.Graph(id='bubble-graph')
    ], style={'marginTop': '30px'}),
    html.Div([
        html.H3("Топ-15 стран по популяции"),
        dcc.Graph(id='top15-graph')
    ], style={'marginTop': '30px'}),

    
    html.Div([
        html.H3("Круговая диаграмма по популяциям на континентах"),
        dcc.Graph(id='pie-continents')
    ], style={'marginTop': '30px'})

])


@callback(
    Output('line-graph', 'figure'),
    [Input('countries-selector', 'value'),
     Input('year-range-slider', 'value'),
     Input('y-measure-dropdown', 'value')]
)
def update_line_chart(countries, year_range, y_measure):
    if not countries:
        return px.line(title='Нет выбранных стран')
    start_year, end_year = year_range
    dff = df[(df['country'].isin(countries)) & (df['year'] >= start_year) & (df['year'] <= end_year)]
    if dff.empty:
        return px.line(title='Нет данных для выбранных условий')
    fig = px.line(dff, x='year', y=y_measure, color='country', markers=True,
                  title='Популяция по годам')
    return fig

@callback(
    Output('bubble-graph', 'figure'),
    [Input('bubble-x', 'value'),
     Input('bubble-y', 'value'),
     Input('bubble-size', 'value'),
     Input('year-range-slider', 'value')]
)
def update_bubble_chart(x_axis, y_axis, size_axis, year_range):
    start_year, end_year = year_range
    dff = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    if dff.empty:
        return px.scatter(title='Нет данных')
    dff_avg = dff.groupby('country').agg({
        x_axis: 'mean',
        y_axis: 'mean',
        size_axis: 'mean',
        'continent': 'first'
    }).reset_index()

    fig = px.scatter(
        dff_avg,
        x=x_axis,
        y=y_axis,
        size=size_axis,
        color='continent',
        hover_name='country',
        size_max=60,
        log_x=False,
        log_y=False,
        title='Пузырьковая диаграмма'
    )
    return fig

@callback(
    Output('top15-graph', 'figure'),
    [Input('year-range-slider', 'value')]
)
def update_top15(year_range):
    start_year, end_year = year_range
    dff = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    
    top15 = dff.groupby('country')['pop'].mean().nlargest(15).reset_index()
    fig = px.bar(top15, y='country', x='pop', orientation='h', title='Топ-15 стран по населению')
    return fig

@callback(
    Output('pie-continents', 'figure'),
    [Input('year-range-slider', 'value')]
)
def update_pie_continents(year_range):
    start_year, end_year = year_range
    dff = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
 
    continent_totals = dff.groupby('continent')['pop'].mean().reset_index()
    fig = px.pie(continent_totals, values='pop', names='continent', title='Популяция по континентам')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
