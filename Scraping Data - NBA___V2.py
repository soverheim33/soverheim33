"""
Created by Steven Overheim on 5/9/22 to get data for an NBA data science project
Goal of the project is to see what the leading factors are in determining the NBA champion
"""

"""
 Main tables needed thus far:
    The per team statistics table -basic statistics for each team that season and their opponents (allowed rebounds etc)
                                    as well as advanced stats for the team (none for opponent)
    The champions table - the table denoting who won the championship that year
    
    Ommitting shooting statistics even though available due to the fact that there aren't that many years of data available'
"""

# import all needed libraries
from bs4 import BeautifulSoup as Soup
import pandas as pd
import requests 

def get_regular_season_stats(years):
    history = pd.DataFrame()
    for year in years:
        # get the html from entire page
        bball_ref_response = requests.get(f'https://www.basketball-reference.com/leagues/NBA_{year}.html')

        # lets parse all that response
        bball_soup = Soup(bball_ref_response.text)

        # lets find all the tables
        tables = bball_soup.find_all('table')

        # by using caption we find all the table names on the site and can dynamically get the table positions we need
        titles = bball_soup.find_all('caption')

        # turn the list into a list of strings I can search
        titles = [str(x.string) for x in titles]

        # Finds the index position of each of the tables and stores them
        per_game_pos = titles.index('Per Game Stats Table')
        adv_stat_pos = titles.index('Advanced Stats Table')

        # using a comprehension in the team stats to find the table headers
        # these headers are the same for both team and their opponents so no need to duplicate
        basic_stat_cols = [str(x.string) for x in tables[per_game_pos].find_all('th')]
        # only include column headers for the stats we want
        basic_stat_cols = basic_stat_cols[1:25] 

        # lets get the rows in the table isolated and avoid the header row
        rows = tables[per_game_pos].find_all('tr')[1:]

        # now we will perform a comprehension within a comprehension to get a looping effect on our rows
        # what this line will do is make a list of lists of each of the team's data
        # that list of lists is now easily transformed into a dataframe
        team_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]

        # do the same thing for the opponents table of basic stats
        opp_rows = tables[per_game_pos+1].findAll('tr')[1:]
        opp_team_stats = [[td.getText() for td in opp_rows[i].findAll('td')] for i in range(len(opp_rows))]

        # here we transform the list of lists into a dataframe
        stats = pd.DataFrame(team_stats, columns = basic_stat_cols)
        # check for clean outcome
        stats.head(10)

        # we now have a base table we can start adding to
        # first let's create our other two tables
        # we can change the name for the opp stats by adding "opp_" to the begining of every variable
        opp_stat_cols = ["opp_" + x for x in basic_stat_cols]

        # now lets create a dataframe for the opponents info
        opp_stats = pd.DataFrame(opp_team_stats, columns = opp_stat_cols)
        # check to make sure everything is fine
        opp_stats.head(10)

        # first lets get our advanced stat columns
        adv_stat_cols = [str(x.string) for x in tables[adv_stat_pos].findAll('th')]
        adv_stat_cols = adv_stat_cols[6:36]

        # now lets store the rows of data we want
        adv_rows = tables[adv_stat_pos].findAll('tr')[2:]

        # lets perform that double comprehension again to get the data out of the rows into a list of lists
        adv_stats_data = [[td.getText() for td in adv_rows[i].findAll('td')] for i in range(len(adv_rows))]

        # let's now put these into a dataframe 
        adv_stats = pd.DataFrame(adv_stats_data, columns=adv_stat_cols)
        # check to make sure everything is okay
        adv_stats.head(10)

        # need to drop the 3 blank columns from adv_stats
        adv_stats = adv_stats.drop('\xa0', axis =1)

        # quickly rename the opp_stats team column to prep for join
        opp_stats.rename(columns={'opp_Team':'Team'},inplace=True)

        # we now have our 3 tables, we can join them together into one wide table
        # inner join on team, defaults of function will automatically do this
        all_stats = pd.merge(stats, opp_stats)

        # bring in our advanced stats now
        all_stats = pd.merge(all_stats, adv_stats)
        # we now have all our data we want from this year in place

        # time to clean up some of the columns and drop redundant and unnecessary ones
        all_stats = all_stats.drop(['G','opp_G','PW','PL','SRS','Arena','Attend.'], axis = 1)
        
        # get rid of legaue average
        all_stats = all_stats[0:30]
        
        # add a season year to the dataframe
        all_stats['season'] = year
        
        # append dataframe to history
        history = pd.concat([history,all_stats])
    
    # convert the index into the season ranking
    history['season_rank'] = history.index + 1
    
    # reset the index 
    history.reset_index(inplace=True)
    return history

years = range(1980,2023)

df = get_regular_season_stats(years)
df.columns



"""
ON-GOING NOTES: 
- need to clean up the asterisks on team names 
    - can be done after joining all three tables together as they are consistent across all 3 tables
        - may need to check consistency through the years of the asterisks on all 3 tables to make work
"""