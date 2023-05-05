## Overview
# backboard
1. What is your problem statement? What will you actually be doing?
    - Make player performance data from Matchplay and IFPA more interpretable.
    - Assessing if player performance in a tournament is "expected" or "unexpected" by modeling/predicting the outcome of a tournament given a set of players.
    - Identifying key tournament venues and player groups with a network analysis of which players tend to play each other in tournaments.
    - The final product looks like:
        1. A webapp showing:
            - Chart of rating/ranking history
            - Breakdown of tournament performance vs expected tournament performance
            - Map of tournament venues
            - Diagram of local pinball "social network"
        2. Backed by an SQL database which caches data from the API and adds new results when the player requests their latest results.
        3. Tournament performance estimates based on modeling expected player performance, using orginal regession.

2. Who is your audience? Why will they care?
    Pinball players:
    1. There are no good tools to evalualate your performance other than point-value ranks and ratings.
    2. It is difficult to know how well you did in a tournament because of the wide range in skill levels of the players. It is not easy to tell how "hard" the competition is with existing tools.
    3. Locating places where tournaments happen:
        - Tournament postings on the IFPA website are *very* poorly implemented and it is not easy to find the places which host regular tournaments. 
        - Different venues are frequented by different groups of players with different skill levels. Some locations thus have "harder" tournaments which may or may not be appropriate for a player's skill level.

3. What is your success metric? How will you know if you are actually solving the problem in a useful way?
    - Evaluating other player's response and use of the tool.
    - Evaluating the model to see how well it predicts tournament results.

4. What is your data source? What format is your data in? How much cleaning and munging will be required?
    - There are APIs from Matchplay and IFPA for all this data. There's little/no cleaning but it's definitely more than one table of data.

5. What are potential challenges or obstacles and how will you mitigate them?
    - Figuring out the UX part of the webapp as well as the most efficient visualizations. I really want people to use this thing.

6. Is this a reasonable project given the time constraints that you have?
    - I think so. The project is also useful even without comprehensive implementation because there really are so few tools to look at performance.
