from typing import Dict, List, Tuple
import bs4
import datetime
import requests
import xlsxwriter

XLSX_FILE_NAME: str = 'Funda.xlsx'


def write_row_in_xlsx(workbook, worksheet, row_num: int, index: int, borrower: str, annual_rate: float, duration: int,
                      safe_plan: str, limit: int, credit_rating: int, info: str, funda_rating: str,
                      months_in_operation: int, bank_or_insurance: int, card_or_savings_bank: int):
    multi_line_format_dict: dict = {'align': 'left', 'text_wrap': True, 'valign': 'top'}
    multi_line_format: xlsxwriter.workbook.Format = workbook.add_format(multi_line_format_dict)
    single_line_format_dict: dict = {'align': 'center', 'valign': 'vcenter'}
    single_line_format: xlsxwriter.workbook.Format = workbook.add_format(single_line_format_dict)

    worksheet.write_number(row_num, 0, index, single_line_format)
    worksheet.write(row_num, 1, borrower, single_line_format)
    worksheet.write(row_num, 2, funda_rating, single_line_format)
    worksheet.write(row_num, 3, annual_rate, single_line_format)
    worksheet.write_number(row_num, 4, duration, single_line_format)
    worksheet.write_number(row_num, 5, limit, single_line_format)
    worksheet.write(row_num, 6, safe_plan, single_line_format)
    worksheet.write_number(row_num, 7, months_in_operation, single_line_format)
    worksheet.write_number(row_num, 8, credit_rating, single_line_format)
    worksheet.write_number(row_num, 9, bank_or_insurance, single_line_format)
    worksheet.write_number(row_num, 10, card_or_savings_bank, single_line_format)
    worksheet.write(row_num, 11, info, multi_line_format)


def create_custom_workbook() -> Tuple[xlsxwriter.workbook.Workbook, xlsxwriter.workbook.Worksheet]:
    # Create Excel workbook
    workbook: xlsxwriter.workbook.Workbook = xlsxwriter.Workbook(XLSX_FILE_NAME)
    now: str = datetime.datetime.today().strftime('%Y%m%d %H%M%S')
    worksheet: xlsxwriter.workbook.Worksheet = workbook.add_worksheet(now)

    # Write headers in xlsx
    header_format_dict: dict = {'align': 'center', 'bold': True, 'valign': 'vcenter'}
    header_format: xlsxwriter.workbook.Format = workbook.add_format(header_format_dict)
    worksheet.write(0, 0, '호수', header_format)
    worksheet.set_column(0, 0, 5)
    worksheet.write(0, 1, '대출자', header_format)
    worksheet.set_column(1, 1, 25)
    worksheet.write(0, 2, '펀다 등급', header_format)
    worksheet.set_column(2, 2, 10)
    worksheet.write(0, 3, '연 수익률(세전, %)', header_format)
    worksheet.set_column(3, 3, 20)
    worksheet.write(0, 4, '투자 기간(개월)', header_format)
    worksheet.set_column(4, 4, 15)
    worksheet.write(0, 5, '투자 한도', header_format)
    worksheet.set_column(5, 5, 10)
    worksheet.write(0, 6, '세이프플랜', header_format)
    worksheet.set_column(6, 6, 10)
    worksheet.write(0, 7, '운영 기간', header_format)
    worksheet.set_column(7, 7, 10)
    worksheet.write(0, 8, 'KCB신용등급', header_format)
    worksheet.set_column(8, 8, 15)
    worksheet.write(0, 9, '은행, 보험', header_format)
    worksheet.set_column(9, 9, 15)
    worksheet.write(0, 10, '카드, 저축은행', header_format)
    worksheet.set_column(10, 10, 15)
    worksheet.write(0, 11, '상점 소개', header_format)
    worksheet.set_column(11, 11, 65)
    return workbook, worksheet


def unsecured_bonds(detail_url: str, workbook, worksheet, row_num: int, index: str, annual_rate: str, duration: int,
                    funda_rating: str, safe_plan: str):
    detail_response: requests.Response = requests.get(detail_url)
    detail_html_soup: bs4.BeautifulSoup = bs4.BeautifulSoup(detail_response.text, 'html.parser')

    # 호수 (디테일 페이지 - 헤더)
    # index_tag: bs4.element.Tag = detail_html_soup.find(id='invest-number')
    # index: str = index_tag.text.replace('호', '')

    headers: bs4.element.ResultSet = detail_html_soup.find_all('li', class_='de-info-fir-li')
    # 대출자 (디테일 페이지 - 헤더)
    borrower_tag: bs4.element.Tag = detail_html_soup.find(id='invest-title')
    borrower = borrower_tag.text

    # 기간 (디테일 페이지 - 상단)
    # duration_tag: bs4.element.Tag = headers[0]
    # duration: int = int(duration_tag.span.text.replace('개월', ''))

    # 수익률 (디테일 페이지 - 상단)
    # annual_rate_tag: bs4.element.Tag = headers[1]
    # annual_rate: str = annual_rate_tag.span.text.replace('%!', '')

    # 세이프플랜 (상단)
    # safe_plan_tag: bs4.element.Tag = headers[2]
    # safe_plan_image_url = safe_plan_tag.img['src']  # 'pc_safe_icon.png'
    # partially_covered: bool = '5000' in safe_plan_image_url

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
    bank_or_insurance: int = 0
    card_or_savings_bank: int = 0
    for record in history.div.table.tbody.find_all('tr'):  # record: bs4.element.ResultSet
        institution: bs4.element.Tag = record.td
        amount_tag: bs4.element.Tag = institution.next_sibling.next_sibling
        amount = int(amount_tag.span.text)
        if institution.text.strip() == '은행, 보험':
            bank_or_insurance = amount
        elif institution.text.strip() == '카드, 저축은행':
            card_or_savings_bank = amount

    # 상점 소개 (디테일 페이지 - 하단)
    intro_statements: bs4.element.ResultSet = detail_html_soup.find_all(class_='list_ok introduce')
    months_in_operation: int = 0

    intros = []
    for block in intro_statements:  # block: bs4.element.ResultSet
        for line in block.find_all('li'):  # line: bs4.element.ResultSet
            if line.text.startswith('운영기간: '):
                years_and_months: str = line.text[6:]
                years = int(years_and_months[:years_and_months.find('년')])
                months = int(years_and_months[years_and_months.find('년') + 1:years_and_months.find('개월')])
                months_in_operation: int = 12 * years + months
            else:
                intros.append(line.text)
    write_row_in_xlsx(workbook, worksheet, row_num, int(index), borrower, float(annual_rate), duration,
                      safe_plan, limit, credit_rating, '\n'.join(intros),
                      funda_rating, months_in_operation, bank_or_insurance, card_or_savings_bank)


def main():
    list_url: str = 'https://www.funda.kr/v2/invest/list'
    list_response: requests.Response = requests.get(list_url)
    list_html_soup: bs4.BeautifulSoup = bs4.BeautifulSoup(list_response.text, 'html.parser')
    products: bs4.element.Tag = list_html_soup.find('div', id='general_merchandise')
    product_titles: bs4.element.ResultSet = products.find_all('span', class_='merchandise-idx')

    workbook, worksheet = create_custom_workbook()
    row_num: int = 0
    page_info_list: List[tuple] = []
    for title in product_titles:  # title: bs4.element.Tag
        body: bs4.element.Tag = title.parent.parent.parent.next_sibling.next_sibling
        children: bs4.element.ResultSet = body.find_all('div')

        # 펀다등급(리스트 페이지)
        funda_rating_tag: bs4.element.Tag = children[0].dd
        funda_rating: str = funda_rating_tag.text.strip()

        # 상품특징 (리스트 페이지)
        safe_plan_tag: bs4.element.Tag = children[1].dd
        if safe_plan_tag.text == '이벤트':
            continue
        if safe_plan_tag.text == '매출우수':
            safe_plan: str = '보호 불가'
        elif safe_plan_tag['title'] == "세이프플랜 적립금 내에서 투자원금 전액이 보호됩니다.":
            safe_plan: str = '전액 보호'
        else:
            safe_plan: str = '부분 보호'

        # 수익률 (리스트 페이지)
        annual_rate: str = children[2].dd.text.replace('%', '').strip()
        # 기간 (리스트 페이지)
        duration: int = int(children[3].dd.text.replace('개월', ''))
        # I want only the bonds with the annual rate of 9% and the duration of 3 months
        if annual_rate != '9':
            continue
        row_num += 1

        # 호수 (리스트 페이지)
        index: str = title.text.replace('호', '')

        # URL
        detail_url: str = 'https://www.funda.kr/v2/invest/?page=' + index
        page_info: tuple = (
            detail_url, workbook, worksheet, row_num, index, annual_rate, duration, funda_rating, safe_plan,
        )
        page_info_list.append(page_info)
        unsecured_bonds(*page_info)
    worksheet.set_default_row(35)  # partially show the third row of store info
    worksheet.set_row(0, 14.4)  # reset header row height
    workbook.close()


if __name__ == '__main__':
    main()
