from numpy.lib.shape_base import column_stack
import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup

def get_item_code():
    sosoks = ['0','1'] # 코스피, 코스닥
    item_code_list = []

    for sosok in sosoks :
        url_tmpl = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=%s'
        url = url_tmpl % sosok

        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text,'html.parser')

        item_info = soup.find('td', {'class' : 'pgRR'}) # 가장 마지막 페이지

        href_addr = item_info.a.get('href')
        page_info = re.findall('[\d]+', href_addr) # 정규식표현, 숫자를 계속 찾는다
        page = page_info[1]
        page = int(page) + 1
        for i in range(1, page, 1): # 페이지만큼 반복
            sub_url = '{}&page={}'.format(url, i)

            page_text = requests.get(sub_url).text
            page_soup = BeautifulSoup(page_text, 'html.parser')

            items = page_soup.find_all('a', {'class' : 'tltle'})## title가 아닌 tltle.. 고의인가 실수인가?
            for item in items:
                item_data = re.search('[\d]+', str(item))
                if item_data:
                    item_code = item_data.group()
                    item_name = item.text
                    result = item_code, item_name
                    item_code_list.append(result)

    return item_code_list

def get_html(code):
    URL = "https://finance.naver.com/item/main.nhn?code=" + code[0]
    reponse_data = requests.get(URL).text   

    soup = BeautifulSoup(reponse_data, 'html.parser')
    try:
        finance_frame = soup.select('div.section.cop_analysis div.sub_section')[0]#html에서 재무재표 가져오기

        dt_col = []
        for item in finance_frame.select('thead th'):
            dt_col.append(item.get_text().strip())

        columns = dt_col[3:13] # 재무정보, 연간실적, 분기실적 text빼고 date만 가져오기

        frame_index = []
        for item in finance_frame.select('th.h_th2')[3:]:# 재무정보, 연간실적, 분기실적 text빼고 date만 가져오기
            data = item.get_text().strip()
            frame_index.append(data)

        frame_data = []
        for item in finance_frame.select('td'):
            data = item.get_text().strip()
            if data == '':
                frame_data.append('0')
            else:
                frame_data.append(data)

        convert_data = np.array(frame_data)
        convert_data.resize(len(frame_index),10) # 16x10형태로 변경

        result = pd.DataFrame(data=convert_data[0:,0:], index=frame_index,columns=columns)

        result.to_csv(code[0] + '.csv',encoding='cp949')
    except:
        print(code[0] + '/' + code[1] + '재무재표 정보 미존재')