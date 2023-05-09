#import palmerpenguins
from shiny import App, render, ui

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

query = """
SELECT *
FROM tournament_results
LIMIT 3
"""
df = pd.read_sql_query(sql=text(query), con=con)


def run_query(query_str: str):
    df = pd.read_sql_query(sql=text(query_str), con=con)
    return df

def get_player_results(player_id: int):

    q_player_results = f"""
    SELECT *
    FROM player_results
    WHERE player_id = {player_id}::text
    """
    df = run_query(q_player_results)
    return df


app_ui = ui.page_fluid(
    ui.input_text("player_id", "IFPA Number:", value=83361),
   # ui.output_text("requested_player_id"),
    ui.output_table("result")
)


def server(input, output, session):
    @output
    # @render.text
    # def requested_player_id():
    #     return input.player_id()
    @render.table
    def result():
        player_results = get_player_results(input.player_id())
        return player_results


            
            



















app = App(app_ui, server, debug=True)
