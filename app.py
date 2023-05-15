import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.io as pio

from htmltools import HTML, div

import shinyswatch
from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from shinywidgets import output_widget, render_widget
import os
import pandas as pd
from datetime import date, datetime

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
    df.query("ratings_value > 0", inplace=True)
    # Create subplot with secondary axis
    subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])

    #Put Dataframe in rating_fig and rank_fig
    rating_fig = px.line(df, x='date', y='ratings_value', title='IFPA Rating')
    rank_fig = px.line(df, x='date', y='wppr_rank', title='IFPA Ranking')

    #Change the axis for ranking
    rank_fig.update_traces(yaxis = 'y2')

    #Add the figs to the subplot figure
    subplot_fig.add_traces(rating_fig.data + rank_fig.data)

    #Formt subplot figure
    subplot_fig.update_layout(title='IFPA Player Stats', yaxis=dict(title='Rating'), 
                              yaxis2=dict(title='Ranking', autorange='reversed'))
    subplot_fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
    
    #subplot_fig.show()
    final_fig = go.FigureWidget(subplot_fig)
    final_fig.update_layout(template = "vapor")
    return final_fig

# Plot Ranking
def rank_plot(df):
    dfx = df.copy()
    fig = px.line(dfx, x='date', y='wppr_rank')
    fig.update_layout(title=None, yaxis=dict(title='IFPA Ranking', autorange = 'reversed'), xaxis=dict(title='Date'), legend=dict(title='Date'))
    return fig

# Plot Ratings and Performance
def rating_performance_plot(df):
    dfx = df.query("ratings_value > 0").copy()
    fig = px.line(dfx, x='date', y='ratings_value')
    fig.add_traces(px.scatter(dfx, x='date', y='ratings_value', color = 'resid_position').data)
    fig.update_traces(marker=dict(size=15, colorbar=dict(title='My Title')))

    fig.update_coloraxes(dict(cmax = 10, cmin=-10))

    fig.update_layout(title=None, yaxis=dict(title='IFPA Rating'), xaxis=dict(title='Date'), legend=dict(title='Date'))
    fig.update_layout(coloraxis_colorbar_title_text = 'Performance<br>Score')
    #fig.show()
    return fig


# Convert int to oridnal
# from: https://stackoverflow.com/a/20007730/3798609
def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

# Return nice text that converts a timedelta into a string
def pretty_timespan(time_delta):
    days = abs(time_delta.days)
    out_str = ''
    if days >= 365*2:
        out_str = f'{int(days/365)} years'
    elif days >= 60:
        out_str = f'{int(days/30)} months'
    elif days >= 14:
        out_str = f'{int(days/7)} weeks'
    else:
        out_str = f'{int(days)} days'
    return out_str

# About Page Text in HTML
about_html = """
<h1 id="about-backboard">About Backboard</h1>
<p>Backboard is a tool for making pinball player data from IFPA more useful. <a href="https://www.ifpapinball.com/">The International Flipper Pinball Association</a>  (IFPA) tracks results from sanctioned pinball tournaments the world over and uses them to build rankings for regional, national, and international championship tournaments. The final standings in each tournament are factored into algorithms to determine a player&#39;s <a href="https://www.ifpapinball.com/menu/ranking-info-2/#rating">rating</a>. Competing in tournaments also awards <a href="https://www.ifpapinball.com/menu/ranking-info-2/#base">points</a> by which championship rankings are determined.</p>
<p>The collected results for each player are made available on the IFPA website (<a href="https://www.ifpapinball.com/player.php?p=83361">example</a>), but the presentation and clarity leaves something to be desired. While all the relevant information <em>is</em> present- it&#39;s not easy to interpret trends in your metrics and the summary statistics provided are minimal.</p>
<p>Backboard makes this data more useful by showing graphs of a players rating and ranking history over time, providing additional summary statistics, and evaluating tournament-level performance with a new <em>Performance Score</em>.</p>
<h3 id="performance-scores">Performance Scores</h3>
<p>A player&#39;s performance in a tournament is, ultimately, just the player&#39;s place/position at the end of play. This is used for point allocation and rating adjustments. However the skill levels of the players in a tournament can vary widely and it&#39;s difficult to gauge one&#39;s own performance relative to the other players&#39; skill level.</p>
<p>The <strong>Performance Score</strong> presented here indicates how much better (or worse) a player&#39;s position in the tournament was compared to predicted performance. IFPA ratings are based on a modified version of the <a href="https://en.wikipedia.org/wiki/Glicko_rating_system">Glicko</a> rating system and intended to indicate the predicted outcome in a match. Thus, in theory, the outcome of a tournament <em>should</em> be identical to a list of player rankings from highest to lowest. The <strong>Performance Score</strong> is the difference between this predicted standing and the actual one. </p>
<p>For example, if a player has the 10th highest rating in a tournament, but ends up in 4th Place, their <strong>Performance Score</strong> would be 6. If a player had the 4th highest rating but ended up in 10th place, their performance score would be -6.</p>
<h3 id="how-it-s-done-">How it&#39;s done.</h3>
<p>Tournament results and player data are retrieved from the IFPA&#39;s <a href="https://www.ifpapinball.com/api/documentation/">API</a> and collected into a PostgreSQL database hosted on <a href="https://www.digitalocean.com/">DigitalOcean</a>. Queries of this database are used to draw graphs with <a href="https://plotly.com/python/">Plotly</a>. This site was created with the <a href="https://shiny.rstudio.com/py/">Shiny</a> framework and is hosted on <a href="https://www.shinyapps.io/">shinyapps.io</a>.</p>
"""

## New UI
# cribbed from: https://shinylive.io/py/examples/#shinyswatch

app_ui = ui.page_navbar(
    # Available themes: https://bootswatch.com/
    #  cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux,
    #  materia, minty, morph, pulse, quartz, sandstone, simplex, sketchy, slate,
    #  solar, spacelab, superhero, united, vapor, yeti, zephyr
    shinyswatch.theme.vapor(),
    ui.nav(
        "Player Performance",
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
                    ui.column(4, ui.tags.h3(ui.output_text("ifpa_rank"))),
                ),
            ui.row(
                    ui.column(6, ui.tags.h3("IFPA Rating: ")),
                    ui.column(4, ui.tags.h3(ui.output_text("ifpa_rating"))),
                ),
            ui.row(
                    ui.column(6, ui.tags.h5("Tournaments Played: ")),
                    ui.column(4, ui.tags.h5(ui.output_text("tournaments_played"))),
                ),
            ui.row(
                    ui.column(6, ui.tags.h5(ui.output_text("tournament_best_str"))),
                    ui.column(4, ui.tags.h5(ui.output_text("tournament_best_num"))),
                ),
            ui.row(
                    ui.column(6, ui.tags.h5("Active for: ")),
                    ui.column(4, ui.tags.h5(ui.output_text("time_active")),),
                ),
            ui.row(
                    ui.column(6, ui.tags.h5("Last Tournament: ")),
                    ui.column(4, ui.tags.h5(ui.output_text("since_last")),),
                ),                 
            output_widget("ranking_plot")
            ),
            ui.panel_main(
                ui.tags.h4("Player Performance"),
                output_widget("rating_perf_plot"),
                ui.output_table("result"),     
            ),
        ),
    ),
    ui.nav(
        "About",
        ui.layout_sidebar(
            ui.panel_sidebar(),
            ui.panel_main(
                ui.HTML(about_html)
            ),
        )),
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
        df = get_player_results()
        return df['name'][0].strip()
    
    @output
    @render.text
    def ifpa_rank():
        df = get_player_results()
        return ordinal(df['wppr_rank'][0])

    @output
    @render.text
    def ifpa_rating():
        df = get_player_results()
        return int(df['ratings_value'][0])

    @output
    @render.text
    def time_active():
        df = get_player_results()
        time_active = df['date'].max() - df['date'].min()
        return pretty_timespan(time_active)
    
    @output
    @render.text
    def since_last():
        df = get_player_results()
        time_since = date.today() - df['date'].max()
        out_str = pretty_timespan(time_since)
        return out_str + " ago"
    
    @output
    @render.text
    def tournaments_played():
        df = get_player_results()
        out_str = df['tournament_id'].unique().shape[0]
        return out_str

    @output
    @render.text
    def tournament_best_str():
        df = get_player_results()
        num_won = (df['position'] == 1).sum()
        if num_won > 0:
            out_str = f'Tournaments Won: '
        else:
            out_str = f'Best Position: '
        return out_str

    @output
    @render.text
    def tournament_best_num():
        df = get_player_results()
        num_won = (df['position'] == 1).sum()
        best = df['position'].min()
        if num_won > 0:
            out_num = str(num_won)
        else:
            out_num = str(ordinal(best))
        return out_num
    
    # Plots
    @output
    @render_widget
    def perf_plot():
        df = get_player_results()
        df['date'] = df['date'].astype('str')
        return performance_plot(df)

    @output
    @render_widget
    def rating_perf_plot():
        df = get_player_results()
        df['date'] = df['date'].astype('str')
        return rating_performance_plot(df)

    @output
    @render_widget
    def ranking_plot():
        df = get_player_results()
        df['date'] = df['date'].astype('str')
        return rank_plot(df)
    
    # Table
    @output
    @render.table
    def result():
        res = get_player_results()
        # Make synthetic column of "position (pred_position)" for compactness.
        #res['result'] = res['position'].astype('str') + " (" + res['resid_position'].astype('str') + ")"
        res['place'] = res['position'].apply(ordinal)
        res['ratings_value'] = res['ratings_value'].astype('int')
        res = res.filter(['date', 'tournament_name', 'place', 'points', 'resid_position'])
        #res['wppr_rank'] = res['wppr_rank'].apply(ordinal)

        res.rename(columns = {'date': 'Date', 
                              'tournament_name': 'Tournament',
                              'place': 'Place',
                              'resid_position': 'Perf. Score',
                              'points': 'Points'}, inplace = True)
        return res


            
            



















app = App(app_ui, server, debug=True)
