import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.io as pio

import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from shinywidgets import output_widget, render_widget
import os
import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

# Import `vapor` theme for plotly
load_figure_template(themes='vapor')

# Import Credientials (returns `True` if successful.)
load_dotenv('./secrets.env')
backboard_user = os.getenv('BACKBOARD_USER')
backboard_pass = os.getenv('BACKBOARD_PASS')
backboard_host = os.getenv('BACKBOARD_HOST')
backboard_port = os.getenv('BACKBOARD_PORT')
backboard_dbname = os.getenv('BACKBOARD_DBNAME')

url_object = URL.create(
    "postgresql",
    username=backboard_user,
    password=backboard_pass,
    host=backboard_host,
    port=backboard_port,
    database=backboard_dbname
)

engine = sqlalchemy.create_engine(url_object)
con=engine.connect()

# Basic SQL query wrapper.
def run_query(query_str: str):
    df = pd.read_sql_query(sql=text(query_str), con=con)
    return df

# Plot Ratings/Rankings
# Cribbed from https://stackoverflow.com/a/62853540/3798609
def performance_plot(df):
    print(type(df['date']))
    # Create subplot with secondary axis
    subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])

    #Put Dataframe in rating_fig and rank_fig
    rating_fig = px.line(df, x='date', y='ratings_value', title='IFPA Rating')
    rank_fig = px.line(df, x='date', y='wppr_rank', title='IFPA Ranking')

    #Change the axis for ranking
    rank_fig.update_traces(yaxis = 'y2')

    #Add the figs to the subplot figure
    subplot_fig.add_traces(rating_fig.data + rank_fig.data)

    #FORMAT subplot figure
    subplot_fig.update_layout(title='IFPA Player Stats', yaxis=dict(title='Rating'), 
                              yaxis2=dict(title='Ranking', autorange='reversed'))
    subplot_fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    
    #subplot_fig.show()
    final_fig = go.FigureWidget(subplot_fig)
    final_fig.update_layout(template = "vapor")
    return final_fig

## New UI
# cribbed from: https://shinylive.io/py/examples/#shinyswatch

app_ui = ui.page_navbar(
    # Available themes: https://bootswatch.com/
    #  cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux,
    #  materia, minty, morph, pulse, quartz, sandstone, simplex, sketchy, slate,
    #  solar, spacelab, superhero, united, vapor, yeti, zephyr
    shinyswatch.theme.vapor(),
    ui.nav(
        "Player Performane",
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.tags.h4("Enter Your IFPA Number:\n"),
                ui.row(
                    ui.column(8, ui.input_text("player_id", "", value=83361)),
                    ui.column(4, ui.input_action_button("action", "GO!")),
                ),
            ui.tags.h1(ui.output_text("player_name")),
            ui.row(
                    ui.column(6, ui.tags.h3("IFPA Rank: ")),
                    ui.column(4, ui.tags.h3(ui.output_text("ifpa_rank")),),
                ),
            

            ),
            ui.panel_main(
                output_widget("perf_plot"),
                ui.output_table("result"),     
            ),
        ),
    ),
    ui.nav("Global Stats"),
    ui.nav("About"),
    title="Backboard",
)

## Shiny Server ##
def server(input, output, session):
    # A reactive dataframe to hold player results
    results_df = reactive.Value(pd.DataFrame())

    @reactive.event(input.action, ignore_none=False)
    def get_player_results():
        player_id = input.player_id()
        q_player_results = f"""
        SELECT *, pred_position - position AS resid_position
        FROM
        (SELECT tournament_id, tournament_name, date, wppr_rank, player_id, position, ratings_value, points, name,
                ROW_NUMBER () OVER (PARTITION BY tournament_id ORDER BY ratings_value DESC) as pred_position
        FROM
        (SELECT player_id, tournament_id, tournament_name, wppr_rank, date, position, points, name, coalesce(ratings_value, '0') as ratings_value
            FROM
                -- Get all results from all those tournaments
                (SELECT player_id, tournament_id, wppr_rank, tournament_name, position, ratings_value, points, date, name
                FROM player_results
                WHERE tournament_id IN
                    -- Get all of the tournament_id's for a player
                    (SELECT tournament_id
                    FROM player_results
                    WHERE player_id = {player_id}::text)) AS y) AS z) AS x
        WHERE player_id = {player_id}::text
        ORDER BY date DESC
        """
        df = run_query(q_player_results)
        return df

    @output
    @render.text
    def player_name():
        name = get_player_results()
        return name['name'][0].strip()
    
    @output
    @render.text
    def ifpa_rank():
        rank = get_player_results()
        return rank['wppr_rank'][0]
    
    @output
    @render_widget
    def perf_plot():
        df = get_player_results()
        df['date'] = df['date'].astype('str')
        return performance_plot(df)
    
    @output
    @render.table
    def result():
        res = get_player_results()
        # Make synthetic column of "position (pred_position)" for compactness.
        res['result'] = res['position'].astype('str') + " (" + res['pred_position'].astype('str') + ")"
        res['ratings_value'] = res['ratings_value'].astype('int')
        res = res.filter(['date', 'tournament_name', 'result', 'ratings_value', 'wppr_rank', 'points'])
        

        res.rename(columns = {'date': 'Date', 
                              'tournament_name': 'Tournament',
                              'result': 'Place',
                              'points': 'Points',
                              'ratings_value': 'Rating',
                              'wppr_rank': 'Rank',}, inplace = True)
        return res


            
            



















app = App(app_ui, server, debug=True)
