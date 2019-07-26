import bs4
import datetime
import requests
import xlsxwriter


def write_row_in_xlsx(workbook, worksheet, row_num: int, index: int, borrower: str, annual_rate: float, duration: int,
                      partially_covered: bool, limit: int, credit_rating: int, info: str):
    intro_format = workbook.add_format({'align': 'left', 'text_wrap': True, 'valign': 'top'})
    non_intro_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

    worksheet.write_number(row_num, 0, index, non_intro_format)
    worksheet.write(row_num, 1, borrower, non_intro_format)
    worksheet.write(row_num, 2, annual_rate, non_intro_format)
    worksheet.write_number(row_num, 3, duration, non_intro_format)
    worksheet.write(row_num, 4, '부분 보호' if partially_covered else '전액 보호', non_intro_format)
    worksheet.write_number(row_num, 5, limit, non_intro_format)
    worksheet.write_number(row_num, 6, credit_rating, non_intro_format)
    worksheet.write(row_num, 7, info, intro_format)


XLSX_FILE_NAME: str = 'Funda.xlsx'
list_url: str = 'https://www.funda.kr/v2/invest/list'
list_response: requests.Response = requests.get(list_url)
list_html_soup: bs4.element.ResultSet = bs4.BeautifulSoup(list_response.text, 'html.parser')
products: bs4.element.Tag = list_html_soup.find('div', id='general_merchandise')
product_titles: bs4.element.ResultSet = products.find_all('span', class_='merchandise-idx')

# Create Excel workbook
workbook = xlsxwriter.Workbook(XLSX_FILE_NAME)
now: str = datetime.datetime.today().strftime('%Y%m%d %H%M%S')
worksheet = workbook.add_worksheet(now)

# Write headers in xlsx
header_format = workbook.add_format({'align': 'center', 'bold': True, 'valign': 'vcenter'})
worksheet.write(0, 0, 'Index', header_format)
worksheet.write(0, 1, 'Borrower', header_format)
worksheet.write(0, 2, 'Annual Rate (%)', header_format)
worksheet.write(0, 3, 'Duration (month)', header_format)
worksheet.write(0, 4, 'Safe Plan', header_format)
worksheet.write(0, 5, 'Limit', header_format)
worksheet.write(0, 6, 'Credit Rating', header_format)
worksheet.set_column('A:G', 25)
worksheet.write(0, 7, 'Info', header_format)
worksheet.set_column('H:H', 65)

title: bs4.element.Tag
row_num: int = 0
for title in product_titles:
    body: bs4.element.Tag = title.parent.parent.parent.next_sibling.next_sibling
    children: bs4.element.ResultSet = body.find_all('div')
    # 수익률 (리스트 페이지)
    annual_rate: str = children[2].dd.text.replace('%', '').strip()
    # 기간 (리스트 페이지)
    duration: int = int(children[3].dd.text.replace('개월', ''))
    # I want only the bonds with the annual rate of 9% and the duration of 3 months
    if annual_rate != '9' or duration != 3:
        continue

    row_num += 1
    # 호수 (리스트 페이지)
    index: str = title.text.replace('호', '')

    # URL
    detail_url: str = 'https://www.funda.kr/v2/invest/?page=' + index
    detail_response: requests.Response = requests.get(detail_url)
    detail_html_soup: bs4.element.ResultSet = bs4.BeautifulSoup(detail_response.text, 'html.parser')

    # 호수 (디테일 페이지 - 헤더)
    # index_tag: bs4.element.Tag = detail_html_soup.find(id='invest-number')
    # index: int = int(index_tag.text.replace('호', ''))

    headers: bs4.element.ResultSet = detail_html_soup.find_all('li', class_='de-info-fir-li')
    # 대출자 (디테일 페이지 - 헤더)
    borrower_tag: bs4.element.Tag = detail_html_soup.find(id='invest-title')
    borrower = borrower_tag.text

    # 기간 (디테일 페이지 - 상단)
    # duration_tag: bs4.element.Tag = headers[0]
    # duration: str = duration_tag.span.text

    # 수익률 (디테일 페이지 - 상단)
    # annual_rate_tag: bs4.element.Tag = headers[1]
    # annual_rate: str = annual_rate_tag.span.text

    # 세이프플랜 (상단)
    safe_plan_tag: bs4.element.Tag = headers[2]
    safe_plan_image_url = safe_plan_tag.img['src']  # 'pc_safe_icon.png'
    partially_covered: bool = '5000' in safe_plan_image_url

    # 투자 한도 (디테일 페이지 - 우측)
    limit_tag: bs4.element.Tag = detail_html_soup.find(class_='money-range')
    limit: int = int(limit_tag.p.span.text.replace('만원', ''))
    # 모집 금액 (디테일 페이지 - 헤더)
    status_tag: bs4.element.Tag = detail_html_soup.find(class_='funding-status')
    status: str = status_tag.text.replace('만원', '')
    current: int = int(status.split('/')[0])
    total: int = int(status.split('/')[1])
    limit = min(limit, total - current)

    # KCB 신용정보 (디테일 페이지 - 하단)
    credit_rating_tag: bs4.element.Tag = detail_html_soup.find(class_='c-score_1')
    credit_rating: int = int(credit_rating_tag.span.text)

    # 기존 신용대출정보(디테일 페이지 - 하단)
    history: bs4.element.Tag = detail_html_soup.find(class_='c-loan-history')
    records = {}
    record: bs4.element.ResultSet
    for record in history.div.table.tbody.find_all('tr'):
        institution: bs4.element.Tag = record.td
        amount_tag: bs4.element.Tag = institution.next_sibling.next_sibling
        amount: str = amount_tag.span.text
        records[institution.text] = amount

    # 상점 소개 (디테일 페이지 - 하단)
    intro_statements: bs4.element.ResultSet = detail_html_soup.find_all(class_='list_ok introduce')
    intros = []
    for block in intro_statements:
        line: bs4.element.ResultSet
        for line in block.find_all('li'):
            intros.append(line.text)
    write_row_in_xlsx(workbook, worksheet, row_num, int(index), borrower, float(annual_rate), duration,
                      partially_covered, limit, credit_rating, '\n'.join(intros))
worksheet.set_default_row(20)  # partially show the second row of store info
worksheet.set_row(0, 14.4)  # reset header row heightn
workbook.close()
