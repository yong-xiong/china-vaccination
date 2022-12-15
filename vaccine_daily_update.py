import time 
from bs4 import BeautifulSoup
import requests
import pandas as pd
import random
import datetime
import re

df = pd.read_csv('daily_update.csv', index_col=0, parse_dates=True, names = ['date', 'vaccine_num_total', 'vaccine_num_daily', 'link'])
df = df.iloc[1:]
df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'].dt.date
df['vaccine_num_total'] = df['vaccine_num_total'].astype(int)
df['vaccine_num_daily'] = df['vaccine_num_daily'].astype(int)

latest_date_org = df['date'].max()
latest_cavvine_num = df[df['date'] == latest_date_org]['vaccine_num_total'].values[0]

# Get the official link of the latest vaccine data
url = 'http://sousuo.gov.cn/column/40403/0.htm'
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('li')
max_date = datetime.date(2020, 12, 1)
max_date_link = ''
for i in links:
    if '新冠病毒疫苗接种情况' in i.text:
        vaccine_announce_date = i.a['href'][25:35]
        vaccine_announce_date = datetime.datetime.strptime(vaccine_announce_date, '%Y-%m/%d').date()
        vaccine_announce_date = vaccine_announce_date + datetime.timedelta(days=-1)

        if vaccine_announce_date > max_date:
            max_date = vaccine_announce_date
            link = i.a['href']
            max_date_link = link
print(max_date)
print(max_date_link)

# Get the latest vaccine data
if max_date > latest_date_org:
    url = max_date_link
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    soup
    page_text =  soup.find('p').text
    text_extract = page_text[20:]
    text_num = re.findall(r'(\d+\.\d+)', text_extract)
    text_num = text_num[0]
    vaccine_num = int(float(text_num)*10000)
    print(vaccine_num)
    text_date = re.findall(r'(\d{4}年\d{1,2}月\d{1,2}日)', page_text)[0]
    text_date = datetime.datetime.strptime(text_date, '%Y年%m月%d日').date()
    print(text_date)
    vaccine_num_daily = vaccine_num - latest_cavvine_num
    print(vaccine_num_daily)
    print(page_text)
    df = df.append({'date': text_date, 'vaccine_num_total': vaccine_num, 'vaccine_num_daily': vaccine_num_daily, 'link': url}, ignore_index=True)
    df.to_csv('daily_update.csv')
    print('New data added')
else:
    print('No new data')

#make it run every 4 hours
time.sleep(14400)
