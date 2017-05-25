# Ystorical

Ystorical is a python script aimed to download Yahoo historical stock data.
Since changes on Yahoo's site, pandas_datareader is broken and Yahoo data is no more accessible using pandas. Until this issue will be fixed, you can use this script based on this stackoverflow [post](https://stackoverflow.com/questions/44045158/python-pandas-datareader-no-longer-works-for-yahoo-finance-changed-url). 

### Dependecies
pandas  
xvfbwrapper (to run headless on vps)  
dryscrape  
fake_useragent  
lxml  

### Use
Just pass a list of stock symbols with start and end dates  

