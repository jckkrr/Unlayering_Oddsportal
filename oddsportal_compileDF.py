import glob
import numpy as np
import os
import pandas as pd
import re

colors = {'home': {'r': 0,'g': 100, 'b': 0}, 'draw': {'r': 249,'g': 180, 'b': 45}, 'away': {'r': 255,'g': 0, 'b': 0},}
def getColor(wintype, alpha):    
    return f'rgba({colors[wintype]["r"]}, {colors[wintype]["g"]}, {colors[wintype]["b"]}, {alpha})'

dBOOKIES = dict((row['bookie_code'], row['bookie_name']) for index, row in pd.read_csv('CSVs/dfBOOKIES.csv').iterrows())
dBOOKIES[0] = 'unknown'

def compileDF(country, competition):

    df_files = [x for x in glob.glob(f'CSVs/{country}/{competition}/dfODDS*')]
    
    for df_file in df_files:
        
        dff = pd.read_csv(df_file)  
        dff = dff.sort_values(by=['kickoff_epoch'])
        dff['startTime_normalised'] = dff['kickoff_epoch'] - dff['kickoff_epoch'].min()
        dff['file'] = df_file

        if df_files.index(df_file) == 0:
            df = dff.copy()
        else:
            df = pd.concat([df,dff])

        df['winning_odds'] = np.where(df['winner']=='home',df['home_win'],np.where(df['winner']=='draw',df['draw'],df['away_win']))
        df['winning_odds'] = df['winning_odds'].astype(float)

        df['color'] = np.where(df['winner']=='home', getColor('home', 0.33), np.where(df['winner']=='draw', getColor('draw', 0.33), getColor('away', 0.33)))

        df['bookie_name'] = df['bookie_code'].astype(int)
        df['bookie_name'] = np.where(df['bookie_name'].isin(dBOOKIES.keys()), df['bookie_code'], 0)    
        df['bookie_name'] = np.where(df['bookie_name'].isin(dBOOKIES.keys()), df['bookie_name'].apply(lambda x: dBOOKIES[x]), 'UNKNOWN')

        df['hover_text'] = df['home'] + ' ' + df['H'].apply(lambda x: str(x).replace('.0','')) + ' : ' + df['A'].apply(lambda x: str(x).replace('.0','')) + ' ' + df['away'] 
        df['hover_text'] = df['hover_text'].apply(lambda x: f'<b>{x}</b>') 
        df['hover_text'] = df['hover_text'] + '<br>' + df['winner'] + ' $' + df['winning_odds'].apply(lambda x: str(x))
        df['hover_text'] = df['hover_text'] + '<br>' + 'Match ID: ' + df['match_id'] + '<br>' + 'Bookmaker: ' + df['bookie_name']  

    print(df.shape, end='\t')
    
    return df

###
   
def getDFCONCAT(country, competitions_list):
    
    dfCONCAT = pd.DataFrame()
    
    if competitions_list == None:
        competitions_list = [x.split('\\')[1] for x in glob.glob(f'CSVs/{country}/*')]
    
    for comp in competitions_list:
        
        print(comp[0:20], end=' ' * (22-len(comp[0:20])))
        
        dfCONCAT = pd.concat([dfCONCAT, compileDF(country, comp)])
        
        print(dfCONCAT.shape, end='\n')
        
    a = dfCONCAT.shape[0]
    
    dfCONCAT = dfCONCAT.loc[dfCONCAT.winner.notnull()] #### !!!! googd for sorting out tables that arent yet complete
    dfCONCAT = dfCONCAT.reset_index(drop=True)

    b = dfCONCAT.shape[0]
            
    return dfCONCAT

#######

def makeAV(dfCONCAT):
    
    dfAV = dfCONCAT.copy()

    dfAV = dfAV.groupby(['country', 'competition', 'season', 'match_id', 'home', 'away','H', 'A', 'winner', 'color', 'file', 'startTime_normalised'])[['home_win', 'draw', 'away_win', 'winning_odds']].mean().reset_index()

    dfAV['hover_text'] = dfAV['home'] + ' ' + dfAV['H'].apply(lambda x: str(x).replace('.0','')) + ' : ' 
    dfAV['hover_text'] = dfAV['hover_text'] + dfAV['A'].apply(lambda x: str(x).replace('.0',''))  + ' ' + dfAV['away'] 
    dfAV['hover_text'] = dfAV['hover_text'] + '<br>Match id: ' + dfAV['match_id'] + '<br>Average winning odds: ' + dfAV['winning_odds'].apply(lambda x: str(x))

    return dfAV