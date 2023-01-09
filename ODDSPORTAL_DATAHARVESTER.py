from bs4 import BeautifulSoup, Tag
import glob
import json
import math 
import os
import pandas as pd
import numpy as np
import re
import requests
from requests import get
from urllib.parse import unquote

import scrapingTools_v2

#### Use this script to find out which seasons of a competition are archived

def getSeasonBasic(country,competition):
    
    dfARCHIVELINKS = pd.DataFrame(columns=['country', 'current_competition_name', 'published_competition_name', 'season', 'url', 'season_page_id'])
   
    url = f'https://www.oddsportal.com/soccer/{country}/{competition}/results'
    print(url)
    
    soup = scrapingTools_v2.getSoup(url, {'Referer':'https://www.oddsportal.com/'})
    
    print('Seeing which seasons are available: ', end='\t')
    
    col_content = soup.find('div', {'id': 'col-content'})    
    archive_links = col_content.find_all('ul')[1].find_all('a')
        
    for archive_link in archive_links:
        
        published_competition_name, season, season_page_url, season_page_id = None, None, None, None
    
        season = archive_link.text       
        season_page_url_ending = archive_link['href']
        published_competition_name = season_page_url_ending.split('/')[3]
        season_page_url = 'https://www.oddsportal.com' + season_page_url_ending
        
        season_page_soup = scrapingTools_v2.getSoup(season_page_url, {'Referer':'https://www.oddsportal.com/'})    
        for script in season_page_soup.find_all('script'):
            if 'CDATA' in str(script) and 'PageTournament' in str(script):
                js = re.search('({.*})', str(script)).group(1)
                jl = json.loads(js)
                season_page_id = jl['id']
    
        dfARCHIVELINKS.loc[dfARCHIVELINKS.shape[0]+1] = country,competition, published_competition_name, season, season_page_url, season_page_id
    
    ### Save file as CSV
    ### make directories for country/competition
    if not os.path.exists(f"CSVs/{country}"):
        os.makedirs(f"CSVs/{country}")
        
    if not os.path.exists(f"CSVs/{country}/{competition}"):
        os.makedirs(f"CSVs/{country}/{competition}")
        
    dfARCHIVELINKS.to_csv(f'CSVs/{country}/{competition}/dfSEASONSBASIC.csv', index=False)

    
###### Use this script to find out which games happened in a season

### Note that it has trouble with seasons that are in progress and output will be incomplete

def getOverviewPages(country,competition):
    
    dfARCHIVELINKS = pd.read_csv(f'CSVs/{country}/{competition}/dfSEASONSBASIC.csv')
        
    for index, row in dfARCHIVELINKS.iterrows():
        
        season, season_page_id = row['season'], row['season_page_id']

        print(season, season_page_id, end=' | ')
       
        dfx = pd.DataFrame(columns=['day_epoch', 'kickoff_epoch', 'xeid', 'match_name', 'match_link', 'score'])
        
        i = 1

        while i != None:

            url = f'https://fb.oddsportal.com/ajax-sport-country-tournament-archive/1/{season_page_id}/X0/1/11/{i}'                    
            soup = scrapingTools_v2.getSoup(url, {'Referer':'https://www.oddsportal.com/'})
            table = soup.find('table')

            trs = table.find_all('tr')

            epoch = None

            for tr in trs[1:]:

                if bool(tr.find('th')):

                    th = tr.find('th').find('span') 

                    if th['class'][0] == '\\"datet':

                        th_attrs = [x for x in th.attrs]
                        day_epoch = int(th_attrs[1].split('-')[0].split('t')[1])


                if 'xeid' in tr.attrs:

                    xeid, match_name, match_link, score = None, None, None, None

                    xeid = tr['xeid'].replace('\\"','')
                                
                    match_name = tr.a.text
                    match_link = 'https://www.oddsportal.com' + tr.a['href'].replace('\\"','').replace('\\/','/')

                    for td in tr.find_all('td'):

                        if 'class' in td.attrs and 'datet' in td.attrs and td['class'][0] == '\\"table-time':
                            kickoff_epoch = int([x for x in td.attrs if x not in ['class', 'datet']][0].split('-')[0].split('t')[1])

                        if 'table-score' in td.attrs:
                            score = td.text

                    nr = dfx.shape[0] + 1
                    dfx.loc[nr] = day_epoch, kickoff_epoch, xeid, match_name, match_link, score

            i = None if len(trs) == 1 else i+1
        
        dfx.to_csv(f'CSVs/{country}/{competition}/dfOVERVIEW{str(season).replace("/","_")}.csv', index=False)
    

        
##### Use this to find out all games from a competition that are in the archive (to then go and get all their details)

def preHarvest(country,competition):
    getSeasonBasic(country,competition)
    getOverviewPages(country,competition)
    
    
#### Use the below scripts to get the data from individual games
    
##### This one gets the odds 

def getIndividualMatchOdds(unhash_url):
    
    dfMATCH = pd.DataFrame(columns=['bookie_code', 'home_win', 'draw', 'away_win', 'home_win_opening', 'draw_opening', 'away_win_opening'])

    ####

    extra_headers = {}
    extra_headers['Referer'] = 'https://www.oddsportal.com/'
    
    soup = scrapingTools_v2.getSoup(unhash_url, extra_headers)
    soup_p = soup.find('p').text
    
    js = re.search('({.*})', soup_p).group(1)
    jl = json.loads(js)
                  
    odds, opening_odds = (None, None, None), (None, None, None)
        
    if type(jl['d']['oddsdata']['back']) != list:
        odds = jl['d']['oddsdata']['back']['E-1-2-0-0-0']['odds']
        opening_odds = jl['d']['oddsdata']['back']['E-1-2-0-0-0']['openingOdd']

        bookies_codes = [x for x in odds.keys()] 
        bookies_codes = bookies_codes + [x for x in opening_odds.keys() if x not in bookies_codes]
        
        for bookie_code in bookies_codes:
            
            nr = dfMATCH.shape[0] + 1
            
            odds_bookie_0, odds_bookie_1, odds_bookie_2 = None, None, None
            if type(odds[bookie_code]) == dict and len(odds[bookie_code].keys()) == 3 and sorted(odds[bookie_code].keys()) == ['0','1','2']:
                    odds_bookie_0, odds_bookie_1, odds_bookie_2 = odds[bookie_code]['0'], odds[bookie_code]['1'], odds[bookie_code]['2']
            elif type(odds[bookie_code]) == list:
                if len(odds[bookie_code]) == 3:                
                    odds_bookie_0, odds_bookie_1, odds_bookie_2 = odds[bookie_code][0], odds[bookie_code][1], odds[bookie_code][2]   

                     
            openingodds_bookie_0, openingodds_bookie_1, openingodds_bookie_2 = None, None, None           
            if type(opening_odds[bookie_code]) == dict and len(opening_odds[bookie_code].keys()) == 3 and sorted(opening_odds[bookie_code].keys()) == ['0','1','2']:
                openingodds_bookie_0, openingodds_bookie_1, openingodds_bookie_2 = opening_odds[bookie_code]['0'], opening_odds[bookie_code]['1'], opening_odds[bookie_code]['2']
            elif type(opening_odds[bookie_code]) == list:
                if len(opening_odds[bookie_code]) == 3:
                    openingodds_bookie_0, openingodds_bookie_1, openingodds_bookie_2 = odds[bookie_code][0], odds[bookie_code][1], odds[bookie_code][2]
                                    
            dfMATCH.loc[nr] = bookie_code, odds_bookie_0, odds_bookie_1, odds_bookie_2, openingodds_bookie_0, openingodds_bookie_1, openingodds_bookie_2

    return dfMATCH

######
    
def getMatchData(match_id):
            
    dfx = pd.DataFrame()
    
    url = f'https://www.oddsportal.com/soccer/australia/competition/{match_id}'
    soup = scrapingTools_v2.getSoup(url, {'Referer':'https://www.oddsportal.com/'})
            
    for script in soup.find_all('script'):
        if 'CDATA' in str(script) and 'PageEvent' in str(script):

            g1 = re.search('PageEvent\((.*)\);var', str(script)).group(1)
            g1jl = json.loads(g1)
            
            for k in g1jl.keys():    
            
                if k != 'eventBonus':
                    dfx.loc[0, k] = g1jl[k]

                if k in ['xhash']: #'xhashf' seems to do the exact same   
                    unhashed = unquote(g1jl[k])
                    dfx.loc[0, f'{k}_unhash'] = unhashed
                                                            
                    unhash_url_match = f'https://fb.oddsportal.com/feed/match/1-1-{match_id}-1-2-{unhashed}.dat'                     
                    dfMATCH = getIndividualMatchOdds(unhash_url_match) 
               
    for col in dfx.columns:    
        dfMATCH[col] = dfx[col].values[0]
        
    return dfMATCH


def collectData(country, competition, season):
        
    dfOVERVIEW = pd.read_csv(f'CSVs/{country}/{competition}/dfOVERVIEW{season}.csv') ###!!!
    
    print('.' * dfOVERVIEW.shape[0])
    
    try:  # for when you need to restart due to interuption
        dfODDS = pd.read_csv(f'CSVs/{country}/{competition}/dfODDS{season}.csv')
        print('dataframe exists')
    except:
        dfODDS = pd.DataFrame(columns=['match_id'])
        print('starting new dataframe')
        
        
    ## now to go through each match and get data
    ## currently just gets opening and closing odds
    ## could be expanded to get other odds for match
    
    for xeid in dfOVERVIEW['xeid']:
        
        #print(xeid)
                    
        if xeid in dfODDS['match_id'].to_list(): 
            print('!', end='')

        else:         
            
            result = dfOVERVIEW.loc[dfOVERVIEW['xeid']==xeid, 'score'].values[0]
            
            if pd.notnull(result):  ## eg an upcoming game that has been picked up
                
                result = result.replace('pen.','').replace('ET','')
                                    
                if result not in ['award.', 'canc.', 'abn.', 'postp.']:
                    
                    ### repeating as sometimes this breaks, possbily due to hashcode changing
                    try:
                        dfx = getMatchData(xeid)
                    except:
                        try:
                            dfx = getMatchData(xeid)
                        except:
                            try:
                                dfx = getMatchData(xeid)
                            except:
                                dfx = getMatchData(xeid)
                        
                    
                    H,A = result.split(':')                
                    dfx['result'] = result
                    dfx['H'] = int(H.strip())
                    dfx['A'] = int(A.strip())

                    dfx['day_epoch'] = int(dfOVERVIEW.loc[dfOVERVIEW['xeid']==xeid, 'day_epoch'].values[0])
                    dfx['kickoff_epoch'] = int(dfOVERVIEW.loc[dfOVERVIEW['xeid']==xeid, 'kickoff_epoch'].values[0])

                    dfx['country'] = country
                    dfx['competition'] = competition
                    dfx['season'] = season

                    dfx= dfx[[x for x in dfx.columns if x != 'match_id']]
                    dfx = dfx.rename(columns={'id': 'match_id'})

                    dfODDS = pd.concat([dfODDS, dfx])

                    #print(dfODDS.shape)

                    dfODDS.to_csv(f'CSVs/{country}/{competition}/dfODDS{season}.csv', index=False)

                    print('.', end='') ### creates a rudimentary progress bar
     
    # final calculations
    dfODDS['winner'] = np.where(dfODDS['H'] > dfODDS['A'], 'home', np.where(dfODDS['H'] == dfODDS['A'], 'draw', 'away'))
            
    # final tidy-up
    first_cols = ['country', 'competition', 'season', 'match_id', 'home', 'away', 'tournamentId', 'day_epoch', 'kickoff_epoch', 'result', 'H', 'A', 'winner']
    reordered_cols =  first_cols + [x for x in dfODDS.columns if x not in first_cols]
    dfODDS = dfODDS[reordered_cols].reset_index(drop=True)

    dfODDS.to_csv(f'CSVs/{country}/{competition}/dfODDS{season}.csv', index=False)


### Goes through each season collecting all data
def collectAllMatchesAllSeason(country, competition):
    
    files = [x for x in glob.glob(f'CSVs/{country}/{competition}/dfOVERVIEW*.csv')][::-1]    
    seasons = [re.search('dfOVERVIEW(.*).csv', x).group(1) for x in files]
    
    for season in seasons:
                
        if season not in ['2022_2023']:  ### !!!
        
            print('\n', season)

            try:
                collectData(country, competition, season)
            except:
                collectData(country, competition, season)    
    
    
    
    
    
    
    
    
    
    
    
            
### brings it all together

def fullHarvest(country, competition):
    
    if country == None:
        country = input('Country: ')
    
    if competition == None:
        competition = input('Competition (as displayed in URL on Oddsportal): ')

    country, competition = country.lower(), competition.lower()
    preHarvest(country,competition)
    
    print('Collecting data on for seasons...')
    collectAllMatchesAllSeason(country, competition)
    
    
fullHarvest(None, None)




