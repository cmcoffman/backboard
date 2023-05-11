#import palmerpenguins
from shiny import App, reactive, render, ui

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


# Import census API key - returns true if successful
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



def run_query(query_str: str):
    df = pd.read_sql_query(sql=text(query_str), con=con)
    return df

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
    return go.FigureWidget(subplot_fig)

app_ui = ui.page_fluid(
    ui.input_text("player_id", "IFPA Number:", value=83361),
    #ui.output_plot("plot"),
    output_widget("perf_plot"),
    ui.output_table("result")
)


def server(input, output, session):
    

    @reactive.Calc
    def get_player_results():
        player_id = input.player_id()
        q_player_results = f"""
        SELECT *
        FROM player_results
        WHERE player_id = {player_id}::text
        ORDER BY date
        """
        df = run_query(q_player_results)
        return df
    

    @output
    @render_widget
    def perf_plot():
        df = get_player_results()
        df['date'] = df['date'].astype('str')
        return performance_plot(df)
        

    # @render.plot
    # def plot():
    #     player_results = get_player_results()
    #     performance_plot(player_results)
        
    
    @output
    @render.table
    def result():
        player_results = get_player_results()
        return player_results


            
            



















app = App(app_ui, server, debug=True)
