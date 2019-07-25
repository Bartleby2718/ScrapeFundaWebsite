import bs4
import requests

list_url: str = 'https://www.funda.kr/v2/invest/list'
list_response: requests.Response = requests.get(list_url)
list_html_soup: bs4.element.ResultSet = bs4.BeautifulSoup(list_response.text, 'html.parser')
products: bs4.element.Tag = list_html_soup.find('div', id='general_merchandise')
product_titles: bs4.element.ResultSet = products.find_all('span', class_='merchandise-idx')
title: bs4.element.Tag
for title in product_titles:
    body: bs4.element.Tag = title.parent.parent.parent.next_sibling.next_sibling
    children: bs4.element.ResultSet = body.find_all('div')
    # 수익률 (리스트 페이지)
    annual_rate: str = children[2].dd.text.replace('%', '').strip()
    print(annual_rate)
    # 기간 (리스트 페이지)
    duration: str = children[3].dd.text
    print(duration)
    if annual_rate != '9' or duration != '3개월':
        continue

    # 호수 (리스트 페이지)
    index: str = title.text.replace('호', '')
    print(index)

    # URL
    detail_url: str = 'https://www.funda.kr/v2/invest/?page=' + index
    detail_response: requests.Response = requests.get(detail_url)
    detail_html_soup: bs4.element.ResultSet = bs4.BeautifulSoup(detail_response.text, 'html.parser')

    # 호수 (디테일 페이지 - 헤더)
    # index: bs4.element.Tag = detail_html_soup.find(id='invest-number')
    # print(index.text)

    headers: bs4.element.ResultSet = detail_html_soup.find_all('li', class_='de-info-fir-li')
    # 대출자 (디테일 페이지 - 헤더)
    lender: bs4.element.Tag = detail_html_soup.find(id='invest-title')
    print(lender.text)

    # 기간 (디테일 페이지 - 상단)
    # duration: bs4.element.Tag = headers[0]
    # print(duration.span.text)

    # 수익률 (디테일 페이지 - 상단)
    # annual_rate: bs4.element.Tag = headers[1]
    # print(annual_rate.span.text)

    # 세이프플랜 (상단)
    safe_plan: bs4.element.Tag = headers[2]
    safe_plan_image_url = safe_plan.img['src']  # 'pc_safe_icon.png'
    print('부분 보호' if '5000' in safe_plan_image_url else '전액 보호')

    # 투자 한도 (디테일 페이지 - 우측)
    limit: bs4.element.Tag = detail_html_soup.find(class_='money-range')
    print(limit.p.span.text)

    # KCB 신용정보 (디테일 페이지 - 하단)
    score: bs4.element.Tag = detail_html_soup.find(class_='c-score_1')
    print(score.span.text + '등급')

    # 기존 신용대출정보(디테일 페이지 - 하단)
    history: bs4.element.Tag = detail_html_soup.find(class_='c-loan-history')
    records = {}
    record: bs4.element.ResultSet
    for record in history.div.table.tbody.find_all('tr'):
        institution: bs4.element.Tag = record.td
        # print(institution.text)
        amount: bs4.element.Tag = institution.next_sibling.next_sibling
        # print(amount.span.text)
        records[institution.text] = amount.span.text
    print(records)

    # 상점 소개 (디테일 페이지 - 하단)
    intro_statements: bs4.element.ResultSet = detail_html_soup.find_all(class_='list_ok introduce')
    intros = []
    for block in intro_statements:
        line: bs4.element.ResultSet
        for line in block.find_all('li'):
            intros.append(line.text)
    print(intros)
