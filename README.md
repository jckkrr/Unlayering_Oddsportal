# Unlayering Oddsportal
### The data security of the Oddsportal website keeps out unsophisticated web-scrapers. Other sites could learn from this.

------

Oddsportal is a fantastic archive of sporting bets odds going back well over a decade, and its data was the basis for the BuzzFeed/BBC investigation into match-fixing in tennis. 

There are, however, lots of obstacles in the way of those who would wish to scrape data from the site, and from a data-security perspective, there is much that other websites could learn. 


#### Finding the webpage of individual games

For each individual game in the Oddsportal archive, data is accessed through its individual webpage. 

These are accessed through URLs such as: https://www.oddsportal.com/soccer/england/ryman-league-2009-2010/boreham-wood-kingstonian-GpgTnOLk/.

The construction of these URLs is:

https://www.oddsportal.com + /**sport** + /**country** + /**competition** + -**year(s)** + /**home_team** + -**away_team** +-**match_id_code**

It is the match_id_code that is paramount here. Without it, the page will not be found. If you have it, however, you can make all the other fields 'unknown' (or anything else) and still find the page you are looking for.  

Take this URL for example: https://www.oddsportal.com/unknown/unknown/unknown/unknown-unknown-SpZ0NZO6/

It will return the page https://www.oddsportal.com/soccer/world/club-friendly/union-berlin-st-pauli-SpZ0NZO6/.

#### Finding the data within the individual webpage

In its most basic form, data for webpages will be included within the HTML of the page. This can even be the case for well-planned sites such as the UK Companies House website. 

Many other sites - especially those that dynamically update with live data - may do client-side ingestion of data into the HTML, which can be receieved via XHR/JSON files (which are relatively simple to scrape), or less frequently, through websockets (which require more technical sophistication to scrape). 

So where does Oddsportal get its information from?

On Oddsportal, the information that is of interest to investigators is stored within the div with the ID "odds-data-table".

This can be seen when using the Inspect tool to look at that area of the page. 

![image](https://user-images.githubusercontent.com/69304112/210020339-6bc1d503-1607-42ee-aeeb-779d0982eb68.png)

However, when one looks at HTML code, that div area is blank.

![image](https://user-images.githubusercontent.com/69304112/210020278-731d3cd5-f7a7-476c-8d2d-483b801d80bd.png)

The dynamic change in the code suggests that the HTML has been updated with the data through a JS script. 

Looking through Inspect's Network tab reveals a script file containing JSON data that has contains the raw elements of what is on the page. 

![image](https://user-images.githubusercontent.com/69304112/210021033-482ec19e-8073-4a6c-82dd-25344b2de642.png)

In this example, the file name for that script is: https://fb.oddsportal.com/feed/match/1-1-SpZ0NZO6-1-2-yj97a.dat

The breakdown of this URL is: https://fb.oddsportal.com/feed/match/1-1- + **match_id_code** + -1-2- + **secondary_id_code** +.dat

The inclusion of the secondary_id_code adds another layer of protection against scrapers, as without this, there is no access to the .dat file.

Furthermore, it was observed that this secondary_id_code changes every few minutes, which adds a furhter layer or security to this data.

Where can this be found? It cannot be conjured from nowhere - the original HTML file needs to be directed - and i the case of Oddsportal results pages, it is hidden within a script in that HTML.  

Furthering the security of this, it is hashed. In this case, as "%79%6a%39%64%39". However, this can be unhashed easily enough. 

As a result, any coder with Oddsportals match id codes and the patience to unpeel the layers of data security on their site can, quite easily, get access to the JSON data on the site's pages. 

With some more time, they can also decipher the JSON data, which is not as easy to read as the webpage, but makes sense once you become familiar with the patterns it is using. 


#### Finding the match_id codes for all games in a season

While anybody could easily copy and paste the data from the webpage, or the code from the Inspect tab (click 'Edit as HTML' on the relevant section), that puts a natural limit on how much data can be scraped manuallly. After a few dozen pages, most people would die of boredom.

By being able to programmatically harvest data from a page, much more data can be accessed. 

But being able to scrape masses of data requires knowing where all the match codes are. 

Once again, this can be found in the JS script that houses the main area of content for the page. Within each link, is an 'xeid' code which equals it. 

By going to the overview page of the competition, and getting the codes for each of the season in the archives, thousands of pages of information can easily be scraped.

### Conclusion

What this research has demonstrated is how easily data from an unencrypted open-access web access can be downloaded, even when the owners of the site have put several hurdles in the way of this happening. Anybody publishing data on the web should be aware that if your computer can read the data, it can be scraped. 

While this information may inform some coders who wish to access the data, it should be noted that this data is available from other sources via subscription APIs. 
