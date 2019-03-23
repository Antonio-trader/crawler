import re
import smtplib
import traceback

import requests
import PyPDF2
from bs4 import BeautifulSoup


def get_html(url):
    r = requests.get(url)

    # Возвращает HTML- код страницы (url)
    return r.text


def get_link(html):
    soup = BeautifulSoup(html, 'lxml')
    td = soup.find('table', id='attachments').find('tr', class_='odd')

    # находим ссылку на pdf.file
    pdf_link = td.find('a').get('href')

    # и возвращаем ее
    return pdf_link


def save_pdf_file(url):
    """Открываем pdf файл и записываем в него содержимое по ссылке"""

    response = requests.get(url, stream=True)

    pdf = 'pdf_file.pdf'
    with open(pdf, 'bw') as f:
        # скачиваем по частям, не целым файлом
        for chunk in response.iter_content(8192):
            f.write(chunk)

    # возвращаем pdf.file
    return pdf


def parse_pdf_file(pdf):
    """Открываем pdf.file и постранично парсим"""

    pdfFileObj = open(pdf, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    file_list = []
    # Получаем количество страниц в pdf-файле
    num_page = pdfReader.numPages

    for i in range(num_page):
        pageObj = pdfReader.getPage(i)

        # Находим на странице все коды ОКПО
        result = re.findall(r'\d{8}', pageObj.extractText())

        # результат записываем в список
        file_list += result
    pdfFileObj.close()

    # возвращаем список с результатом
    return file_list


def save_csv_file(pdf_list):
    """Из списка с результатом сохраняем в csv file"""

    csv = 'csv_file.csv'
    with open(csv, 'w', encoding='utf8') as fg:
        fg.write('ЄДРПОУ' + '\n')
        count = 0
        for i in pdf_list:
            fg.write(i + '|\n')
            count += 1

        # Возвращает количество строк в csv-файле
        return "{} has {} lines".format(csv, count)


def send_email(user, password, recipient, message):
    """Отправка сообщения на почту"""

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, recipient, message)
        server.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")


def main():
    url = 'http://www.minagro.gov.ua/node/25851'

    user = 'test75644@gmail.com'
    password = 'pythoncool'
    recipient = 'test75644@i.ua'

    try:
        minagro = get_html(url)
        pdf_link = get_link(minagro)
        pdf = save_pdf_file(pdf_link)
        pdf_list = parse_pdf_file(pdf)
        msg_save = save_csv_file(pdf_list)
        send_email(user, password, recipient, msg_save)

    except:
        var = 'Error!!!\n' + traceback.format_exc()
        send_email(user, password, recipient, var)


if __name__ == '__main__':
    main()

