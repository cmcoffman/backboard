# Coffman Progress Report 2023-05-7

1. Do you have data fully in hand and if not, what blockers are you facing?
  - Yes I have all the data I need for the project. I made a postgres database and loaded it with data from the IFPA API, about 1.2 million rows in total. I also have transferred the data to a hosted database on DigitalOcean. The webapp will get it's data from there.

2. Have you done a full EDA on all of your data?
 - I have and I feel I am fully familar with it's structure and properties.

3. Have you begun the modeling process? How accurate are your predictions so far?
  - No. I have struggled a little bit figuring out the most sensible approach. See next section. 

4. What blockers are you facing, including processing power, data acquisition, modeling difficulties, data cleaning, etc.? How can we help you overcome those challenges?
- The goal is to predict the outcome of a tournament with a given set of players. I want to use this to provide an evaluation of "how good" a player did in a tournament by comparing the actual results to the predicted results. If they do better or worse than predicted you can identify players who overperformed or underperformed. Relevant features for the model would include the players ratings, rankings, years of experiance, recent tournament results, etc. The problem is my observations are at the tournament level - I am trying to predict not the ranking of a player, but the ranking of all of them. I've been researching but I am struggling to find a modeling framework which fits my situation exactly. Of course the simplest solution is just to use player ratings to predict the outcome. The ratings system is designed to be predictive like this and ratings are updated based on every tournament. The distance between how well the player did vs their rank in the ratings would be the measure of how much they over/under-performed. _I would really value a discussion about the best approach._


5. Have you changed topics since your lightning talk? Since you submitted your Problem Statement and EDA? If so, do you have the necessary data in hand (and the requisite EDA completed) to continue moving forward?

- My topic has not changed.

6. What is your timeline for the next week and a half? What do you have to get done versus what would you like to get done?

- Monday: The webapp be will be communicating with the database and be able to retrieve data.

- Tuesday: The webapp will accept someone's player id as input and output charts of rating and ranking history and summary statistics like tournaments played so far this year, best results, etc. **This is the minimum level of functionality for the webapp to be useful.**

- Wednesday: Start implementing some kind of model, even if it's basic so I have something to build upon. The model should at minimum output if the player did better or worse than expected for each tournament in their history and display this as a graph.

- Thursday / Friday: Catchup and UI tweaks and improvements, making code pretty.

- Saturday / Sunday: Presentation prep.

