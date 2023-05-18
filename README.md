About Backboard
===============

Backboard is a tool for making pinball player data from IFPA more useful. [The International Flipper Pinball Association](https://www.ifpapinball.com/) (IFPA) tracks results from sanctioned pinball tournaments the world over and uses them to build rankings for regional, national, and international championship tournaments. The final standings in each tournament are factored into algorithms to determine a player's [rating](https://www.ifpapinball.com/menu/ranking-info-2/#rating). Competing in tournaments also awards [points](https://www.ifpapinball.com/menu/ranking-info-2/#base) by which championship rankings are determined.

The collected results for each player are made available on the IFPA website ([example](https://www.ifpapinball.com/player.php?p=83361)), but the presentation and clarity leaves something to be desired. While all the relevant information _is_ present- it's not easy to interpret trends in your metrics and the summary statistics provided are minimal.

Backboard makes this data more useful by showing graphs of a players rating and ranking history over time, providing additional summary statistics, and evaluating tournament-level performance with a new _Performance Score_.

### Performance Scores

A player's performance in a tournament is, ultimately, just the player's place/position at the end of play. This is used for point allocation and rating adjustments. However the skill levels of the players in a tournament can vary widely and it's difficult to gauge one's own performance relative to the other players' skill level.

The **Performance Score** presented here indicates how much better (or worse) a player's position in the tournament was compared to predicted performance. IFPA ratings are based on a modified version of the [Glicko](https://en.wikipedia.org/wiki/Glicko_rating_system) rating system and intended to indicate the predicted outcome in a match. Thus, in theory, the outcome of a tournament _should_ be identical to a list of player rankings from highest to lowest. The **Performance Score** is the difference between this predicted standing and the actual one.

For example, if a player has the 10th highest rating in a tournament, but ends up in 4th Place, their **Performance Score** would be 6. If a player had the 4th highest rating but ended up in 10th place, their performance score would be -6.

### How it's done.

Tournament results and player data are retrieved from the IFPA's [API](https://www.ifpapinball.com/api/documentation/) and collected into a PostgreSQL database hosted on [DigitalOcean](https://www.digitalocean.com/). Queries of this database are used to draw graphs with [Plotly](https://plotly.com/python/). This site was created with the [Shiny](https://shiny.rstudio.com/py/) framework and is hosted on [shinyapps.io](https://www.shinyapps.io/).

"""
