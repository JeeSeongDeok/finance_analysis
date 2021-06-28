import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from selenium import webdriver

if __name__ == '__main__':
    success_url = []
    for n in range(1,7):
        # 네이버 증권 테마에서 시작 페이지는 1 ~ 6까지 있음
        url = 'https://finance.naver.com/sise/theme.nhn?&page=' + str(n)
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        theme_address = []
        company_address = []
        # 홈페이지 테이블에서 td.col_type1을 들고오면 테마 주소를 들고올 수 있음
        table = soup.select('div#contentarea_left')
        for tr in table:
            th = tr.select('td.col_type1')
            for td in th:
                theme_address.append('https://finance.naver.com' + td.find("a")["href"])
        # 테마 주소 구하기 끝
        # 테마주소 구한 뒤 거기 해당하는 종목명을 들고오자
        for address in theme_address:
            url = address
            html = requests.get(url)
            soup = BeautifulSoup(html.content, 'html.parser')

            table = soup.select('div.name_area')
            for td in table:
                company_address.append('https://finance.naver.com' + td.find("a")["href"])
         # 회사 들고오기 완료
         # 회사 들고온 후 회사의 정보를 들고오자

        for company in company_address:
            url = company
            html = requests.get(url)
            soup = BeautifulSoup(html.content, 'html.parser')
            for i in soup.select('div.section.cop_analysis'):
                name = i.select('tr')
                for j in name:
                    sentence = j.find('th').text.replace('\n', '').strip()
                    scores = j.select('td')
                    if sentence == 'ROE(지배주주)':
                        if scores[2].text.replace('\n', '').strip().replace(',', '').replace('-', '') == '':
                            continue
                        if float(scores[2].text.replace('\n', '').strip().replace(',', '')) < 10.0:
                            url = ''
                            break
                    elif sentence == 'PER(배)':
                        if scores[2].text.replace('\n', '').strip().replace(',', '').replace('-', '') == '':
                            continue
                        if float(scores[2].text.replace('\n', '').strip().replace(',', '')) > 20.0:
                            url = ''
                            break
                    elif sentence == 'PBR(배)':
                        if scores[2].text.replace('\n', '').strip().replace(',', '').replace('-', '') == '':
                            continue
                        if float(scores[2].text.replace('\n', '').strip().replace(',', '')) > 3.0:
                            url = ''
                            break
                    elif sentence == '부채비율':
                        if scores[2].text.replace('\n', '').strip().replace(',', '').replace('-', '') == '':
                            continue
                        if float(scores[2].text.replace('\n', '').strip().replace(',', '')) > 100.0:
                            url = ''
                            break
                    elif sentence == '매출액' or sentence == '영업이익' or sentence == '당기순이익':
                        # 연간 실적 확인
                        try:
                            old_year_benefit = scores[2].text.replace('\n', '').strip().replace(',', '')
                        except:
                            url = ''
                            break
                        if old_year_benefit == '-' or old_year_benefit == '':
                            continue
                        if scores[3].text.replace('\n', '').strip() == '':
                            new_year_benefit = scores[2].text.replace('\n', '').strip().replace(',', '')
                            old_year_benefit = scores[1].text.replace('\n', '').strip().replace(',', '')
                        else:
                            new_year_benefit = scores[3].text.replace('\n', '').strip().replace(',', '')
                        if new_year_benefit == '' and old_year_benefit == '':
                            url = ''
                            break
                        elif new_year_benefit == '-' or old_year_benefit == '-':
                            url = ''
                            break
                        try:
                            if float(new_year_benefit) <= 5000 and sentence == '매출액':
                                url = ''
                                break
                            elif float(new_year_benefit) <= 1000:
                                url = ''
                                break
                            if float(old_year_benefit) > float(new_year_benefit):
                                url = ''
                                break
                        except:
                            url = ''
                            break

            if url != '':
                success_url.append(url)
        print(n, '번째 페이지 끝')
    print('최종 처리 단계')
    my_set = set(success_url)
    new_success = list(my_set)
    for i in new_success:
        print('success: ' + i)