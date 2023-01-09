def getSoup(url, extra_headers):
    
    from requests import get
    from bs4 import BeautifulSoup
    import requests

    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
    
    headers = {'User-Agent': user_agent,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    
    for k,v in extra_headers.items():
        headers[k] = v
        
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    return soup

#############################

def getTables(soup, print_on):
    
    import pandas as pd
    from bs4 import BeautifulSoup

    tables = soup.find_all('table')
    
    if print_on == True:
        for table in tables:
            attrs = list(table.attrs)
            print(f'\n--- {tables.index(table)}/{len(tables)} --- {attrs}')
            for attr in ['summary', 'title']:
                if attr in attrs:
                    print(attr, ' ' * (10 - len(str(attr))), table[attr])
                    
    return tables

#############################

def getTableHead(table):
    
    import pandas as pd
    import bs4
    from bs4 import BeautifulSoup
    
    df = pd.DataFrame()

    thead = table.find('thead')
            
    if thead != None:
        thead_trs = thead.find_all('tr')
                
        if len(thead_trs) > 0:       
            for tr in thead_trs:
                                    
                n = thead_trs.index(tr)
                                                    
                row_vals = [x for x in tr if x != '\n' and type(x) != bs4.element.Comment]
                row_vals = [x.text.strip() if type(x) == bs4.element.Tag else x for x in row_vals]
                #print(row_vals)
                       
                for val in row_vals:                        
                    df.loc[n, row_vals.index(val)] = val
              
    return df

#############################

def getTableBody(table):
    
    import pandas as pd
    from bs4 import BeautifulSoup
    
    columns = None
    df = pd.DataFrame(columns=columns)   
    
    tbody = table.find('tbody')
    if tbody==None:
        tbody = table
    
    rows = tbody.find_all('tr')
                
    for row in rows:
    
        nr = df.shape[0]
                    
        headers = [x.text.strip() for x in row.find_all('th')]
        data = [x.text.strip() for x in row.find_all('td')]
        full_row = headers + data
                
        if df.shape[1] != len(full_row):  
            if len(row.text.strip()) == 0:    ### blank rows
                full_row = ['' for x in range(0,df.shape[1])] 
                            
        row_cols = [x for x in range(0, len(full_row))]
        df.loc[nr, row_cols] = full_row
          
    
    table_title = table['title'] if 'title' in table.attrs else table['summary'] if 'summary' in table.attrs else None
    
    return df.values, table_title

#############################

def getTable(url, extra_headers, tableNumber):
    
    ### A script to get the table data from any table in the HTML  of a website
    ### It also has the capability to show you what tables are in the page and then select the one you want.
    ### To do this, make the second criteria None. Else, put the number of the wanted table there.
    ### It returns a faithful representation of the table that can then be refined.
    
    import pandas as pd
    from bs4 import BeautifulSoup
    
    df = pd.DataFrame()
        
    soup = getSoup(url, extra_headers)
    
    print(str(soup)[0:200])

    displayTables = True if tableNumber == None else False
    tables = getTables(soup, displayTables)
    
    print(len(tables))
    
    if len(tables) == 0:
        cols, values, table_title = None, None, None
        print('!! NO TABLES FOUND IN PAGE !!')
        
    else:
        
        if tableNumber == None:
            
            if len(tables) == 1:
                tableNumber = 0
                print('One table found in page')
            elif len(tables) > 1:
                tableNumber = int(input('Which table? '))

        table = tables[tableNumber]

        headers = getTableHead(table)
        values, table_title = getTableBody(table)

        if len(headers.values) == 0:  ### no header
            cols = None

        elif len(headers.values) == 1:  # normal header
            cols = headers.values[0]

        elif len(headers.values) > 1:   # multiindex header
            if headers.shape[1] == values.shape[1]:  # ... that follows pattern

                cols = []
                for i in range(0,headers.shape[0]):    
                    cols.append(headers.loc[i].values)

            else:   # that does not

                cols = None
                print('\n\t!!! columns headers must be done manually !!!\n')   

    df = pd.DataFrame(columns=cols, data=values)
    if len(tables) != 0:
        df['table_title'] = table_title

    return df

#######

def getGoogleTag(soup):
    
    gtm = re.search('GTM-(\w*)', str(soup))
    gtm = gtm.group(1) if bool(gtm.group(1)) else None
    
    return gtm