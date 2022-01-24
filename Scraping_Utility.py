from os import error
import requests
import pandas as pd
import numpy as np
import csv
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import lxml






## This utilities purpose is to scrap injury data from prosportstransactions.com, and roster info +
#  games missed per injury from pro-football-reference.
# prosportstranctions data is not stored in a way to make it easily available however ProFootballReference
# has csv and excel data that can be imported

# teams url codes and years for rosters
teams = ['crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle', 'dal', 'den', 'det', 'gnb', 'htx', 'clt', 'jax', 'kan' ,'rai', 'sdg', 'ram', 'mia', 'min', 'nwe', 'nor', 'nyg', 'nyj', 'phi', 'pit', 'sfo', 'sea', 'tam', 'oti', 'was']
teams2 = [ 'clt', 'jax', 'kan' ,'rai', 'sdg', 'ram', 'mia', 'min', 'nwe', 'nor', 'nyg', 'nyj', 'phi', 'pit', 'sfo', 'sea', 'tam', 'oti', 'was']
years = ['2010','2011','2012','2013','2014','2015','2016', '2017', '2018', '2019', '2020']

#builds a url given a teamcode and year
def urlBuild(team, year, selector):
  if selector == 'r':
    url = f'https://www.pro-football-reference.com/teams/{team}/{year}_roster.htm'
  if selector == 'i':
    url = f'https://www.pro-football-reference.com/teams/{team}/{year}_injuries.htm'
  return url

# scroll shim adjusts the position of the website allowing the correct link to be clicked
def scroll_shim(passed_in_driver, object):
      x = object.location['x']
      y = object.location['y']
      x = x - 140
      y = y - 140
      scroll_by_coord = 'window.scrollTo(%s,%s);' % (
          x,
          y
      )
      scroll_nav_out_of_way = 'window.scrollBy(0, -60);'
      passed_in_driver.execute_script(scroll_by_coord)
      passed_in_driver.execute_script(scroll_nav_out_of_way)




def scraperRoster(teams, years): 
  """Scrapes the roster of each team and year specified, capturing csv data and appending it to the specified file.
  employs selenium and chromedriver to navigate the website and beautiful soup to capture the data
  writes data to a csv file


  Args:
      teams ([list]): [list of all teams in the nfl by a three letter identifier]
      years ([list]): [list of years to capture, initally captured 2000-2020, data before 2009 is not useful due to rule changes]
  """
  driver = webdriver.Chrome("chromedriver.exe")
  options = webdriver.ChromeOptions()
  options.add_argument('--ignore-certificate-errors')
  options.add_argument('--ignore-ssl-errors')
  options.add_argument('--ignore-certificate-errors-spki-list')
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  driver = webdriver.Chrome(options=options)
  
  with open('rosterData2021.csv' , 'a', encoding='utf8', errors='ignore', newline='') as f:
    for team in teams:
      for year in years:
        url = urlBuild(team, year, selector='r')
        driver.get(url)
        sleep(2)
        li1 = driver.find_element(By.XPATH, '//*[@id="roster_sh"]/div/ul/li[2]/span')
        actions = ActionChains(driver)
        scroll_shim(driver, li1)
        actions.move_to_element(li1)
      
        actions.perform()
        sleep(2)
        driver.maximize_window()
        button1 = driver.find_element(By.XPATH, '//*[@id="roster_sh"]/div/ul/li[2]/div/ul/li[4]/button')
        actions.click(on_element=button1)
        actions.perform()
        sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        csvH = soup.find('pre', id='csv_roster')
        csvS = str(csvH.text)
        
        sleep(5)
        # print(csvS)
        data = []
        for line in csvS.splitlines():
          if '$' in line:
          #if there is a salary column, find the remove it and replace with empty string
            line = re.sub(r",\$.+", '', line)
          line = line + ',' + str(team).upper() + ',' + str(year)
          data.append([line])
        LOD = len(data) - 1
        data2 = data[5:LOD]
        writer = csv.writer(f)
        for d in data2:
          writer.writerow(d)
  driver.close()
  f.close()
  


# This would capture additional data for each game missed but did not get used in this project
def scraperGamesMissed(): 
  driver = webdriver.Chrome("chromedriver.exe")
  options = webdriver.ChromeOptions()
  options.add_argument('--ignore-certificate-errors')
  options.add_argument('--ignore-ssl-errors')
  options.add_argument('--ignore-certificate-errors-spki-list')
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  driver = webdriver.Chrome(options=options)

  with open('gamesMissedFinal.csv' , 'a', encoding='utf8', errors='ignore', newline='') as f:
    for team in teams:
      for year in years:
        url = urlBuild(team, year, selector='i')
        driver.get(url)

        driver.maximize_window()
        sleep(2)
        li1 = driver.find_element(By.XPATH, '//*[@id="team_injuries_sh"]/div/ul/li[2]/span')
        actions = ActionChains(driver)
        scroll_shim(driver, li1)
        actions.move_to_element(li1)
     
        actions.perform()
        sleep(4)
        button1 = driver.find_element(By.XPATH, '//*[@id="team_injuries_sh"]/div/ul/li[2]/div/ul/li[4]/button')
        actions.click(on_element=button1)
        actions.perform()
        sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        csvH = soup.find('pre', id='csv_team_injuries')
        csvS = str(csvH.text)
     
        sleep(5)
        data = []
        for line in csvS.splitlines():
          # line = transformGamesMissed(line, year, team)
          
          data.append([line])
          
      
        data2 = data[5:]
        writer = csv.writer(f)
        for d in data2:
          print(d)
          writer.writerow(d)
  driver.close()
  f.close()

# builds the url for capturing injury data from prosportstransactions, returns correct url
def NavUrl(year, pos):
  base = 'https://www.prosportstransactions.com/football/Search/SearchResults.php?Player=&Team=&BeginDate='
  pos = str(pos * 25)
  endYear = (int(year) + 1)
  urlParsed = f'{base}{year}-03-03&EndDate={endYear}-03-03&ILChkBx=yes&submit=Search&start={pos}'
  return str(urlParsed)


def scrapeInjuryData(years):
  """Scrapes injury data from prosportstransaction.  This website uses REST architecture and can be navigated via url manipulation.  
 Selenium was not necessary. Beautiful soup was able to extract table information and transform to dataframe.

  Args:
      years ([list]): [years to scrape]

  Returns:
      [dataframe]: returns a pandas.dataframe of injury information.
  """

  for year in years:
    flag = True
    pos = 0
    while flag:
      url = NavUrl(year, pos)
      result = requests.get(url)
      # print(url)
      print(result.status_code)

      src = result.content

      soup = BeautifulSoup(src, features="lxml")
      table = soup.find('table', attrs={'class':'datatable center'})

     

      temp = pd.read_html(str(table), header=0)[0]
      if(temp.empty):
        flag = False
      else:
        temp["Year"] = f'{year}'
        pos = pos + 1
        if(pos == 1 and year == years[0]):
          df = temp
        else:
        
          df = df.append(temp, ignore_index=True)
    
  return df
      
#helper utility to remove formatting errors
def removeAdditionalCols(data, s):
  reg = r'[0-9]{4}(,,)'
  prog = re.compile(reg)
  results = prog.search(data)
  result = re.search(s, reg)
  print(results)

# same as scraperRoster with slight formating changes because data for 2021 was stored slightly different.
# returns its own file seperate from the rest of the data because its to be used differently.
def scraperRoster2021(teams, year): 
  driver = webdriver.Chrome("chromedriver.exe")
  options = webdriver.ChromeOptions()
  options.add_argument('--ignore-certificate-errors')
  options.add_argument('--ignore-ssl-errors')
  options.add_argument('--ignore-certificate-errors-spki-list')
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  driver = webdriver.Chrome(options=options)
  
  with open('rosterData2021.csv' , 'a', encoding='utf8', errors='ignore', newline='') as f:
    for team in teams:
        url = urlBuild(team, year, selector='r')
        driver.get(url)
        sleep(2)
        driver.maximize_window()
        sleep(3)
        li1 = driver.find_element(By.XPATH, '//*[@id="roster_sh"]/div/ul/li[2]/span')
        actions = ActionChains(driver)
        scroll_shim(driver, li1)
        actions.move_to_element(li1)
      # //*[@id="roster_sh"]/div/ul/li[2]
      # /html/body/div[2]/div[5]/div[2]/div[1]/div/ul/li[2]/span
      # //*[@id="roster_sh"]/div/ul/li[2]/span
        actions.perform()
        sleep(2)
       
        button1 = driver.find_element(By.XPATH, '//*[@id="roster_sh"]/div/ul/li[2]/div/ul/li[4]/button')
        actions.click(on_element=button1)
        actions.perform()
        sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        csvH = soup.find('pre', id='csv_roster')
        csvS = str(csvH.text)
        # //*[@id="share_on_roster"]
        # /html/body/div[2]/div[5]/div[2]/div[1]/div/ul/li[2]/div/ul/li[1]/button
        sleep(5)
        # print(csvS)
        data = []
        for line in csvS.splitlines():
          if '$' in line:
          #if there is a salary column, find the remove it and replace with empty string
            line = re.sub(r",\$.+", '', line)
          line = line + ',' + str(team).upper() + ',' + str(year)
          data.append([line])
        LOD = len(data) - 1
        data2 = data[5:LOD]
        writer = csv.writer(f)
        for d in data2:
          writer.writerow(d)
  driver.close()
  f.close()
