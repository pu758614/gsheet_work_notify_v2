import datetime
import json
import pygsheets
import tempfile
from django.conf import settings
from example.conf import field_code_conf

class googleSheet:
    def __init__(self, sheet_title):
        # self.spreadsheet_id = spreadsheet_id
        survey_url = 'https://docs.google.com/spreadsheets/d/1YC0ZVH-xyqAypAp47CnWzmTcFZWsyhRZGI7Gc_GEb5I/edit#gid=507784060'
        temp_data =json.dumps({
            "type": "service_account",
            "project_id": settings.SHEET_PROJECT_ID,
            "private_key_id": settings.SHEET_PRIVATE_KEY_ID,
            "private_key": settings.SHEET_PRIVATE_KEY.replace("\\n",'\n'),
            "client_email": settings.SHEET_CLIENT_EMAIL,
            "client_id": settings.SHEET_CLIENT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": settings.SHEET_CLIENT_X509_CERT_URL,
            "universe_domain": "googleapis.com"
        }).encode('utf-8')

        temp = tempfile.NamedTemporaryFile()
        temp.write(temp_data)
        temp.flush()

        self.gc = pygsheets.authorize(service_account_file=temp.name)
        self.sheet = self.gc.open_by_url(survey_url)
        self.sheet_title = sheet_title

    def create_sheet(self):
        new_sheet = self.sheet.add_worksheet(self.sheet_title)
        return new_sheet

    def read_sheet_cell(self, site):
        worksheet = self.sheet.worksheet_by_title(self.sheet_title)
        data = worksheet.get_value(site)
        return data

    def read_sheet_range(self, start, end):
        worksheet = self.sheet.worksheet_by_title(self.sheet_title)
        data = worksheet.get_values(start, end, returnas='matrix')
        return data

    def read_sheet_all(self):
        worksheet = self.sheet.worksheet_by_title(self.sheet_title)
        # 取得全部，但過濾掉空值空字串空list
        data_list = worksheet.get_all_values(
            returnas='matrix', include_tailing_empty=False)
        new_data = []
        for data in data_list:
            if (len(data) == 0):
                continue
            new_data.append(data)

        # 過濾掉空值空字串
        # data = [x for x in data if x != ['']]
        return new_data

    # pygsheets insert last row
    def insert_sheet(self, data):
        try:
            worksheet = self.sheet.worksheet_by_title(self.sheet_title)
            worksheet.append_table(data,start='A2')
        except Exception as e:
            return False
        return True



    def update_sheet(self, site, data):
        worksheet = self.sheet.worksheet_by_title(self.sheet_title)
        worksheet.update_value(site, data)
        return True

    def check_user(self, user_id):
        data = self.read_sheet_all()
        is_exist = False
        for row in data:
            if (row[0] == user_id):
                is_exist = True
                break
        return is_exist

    def add_user(self, user_id, user_name):

        data = [user_id, user_name,user_name,4]
        self.insert_sheet(data)

    def set_user_notify_day(self, user_id, day):
        data = self.read_sheet_all()
        for index, row in enumerate(data):
            #數字轉英文字
            if (row[0] == user_id):
                self.update_sheet(f"D{index+1}",day)
                break


    def getWorkNames(self,user_id):
        data = self.read_sheet_all()
        name_list = []
        for index, row in enumerate(data):
            if (row[0] == user_id):
                name_list = row[2].split('.')
                break
        return name_list


    # 兩個日期比較大小
    def compare_date(self,date1, date2):
        date1 = datetime.datetime.strptime(date1, '%m/%d')
        date2 = datetime.datetime.strptime(date2, '%m/%d')
        if date1 > date2:
            return 1
        elif date1 < date2:
            return -1
        else:
            return 0

    def is_date(self,date):
        try:
            datetime.datetime.strptime(date, '%m/%d')
            return True
        except ValueError:
            return False


    def getNextWorks(self,name_list):
        data_list=self.read_sheet_all()
        work_date_list = {}
        now_date = datetime.datetime.now().strftime('%m/%d')

        for row in data_list:
            work_date = row[0]
            if(not self.is_date(work_date)):
                continue
            is_over = self.compare_date(work_date,now_date)
            if(is_over==-1):
                continue
            for index, row_data in enumerate(row):
                if(row_data in name_list):
                    field_code = chr(65+index)
                    if(field_code not in field_code_conf):
                        continue
                    if(work_date not in work_date_list):
                        work_date_list[work_date] = []
                    work_name = field_code_conf[field_code]
                    work_date_list[work_date].append(work_name)
        return work_date_list

    def get_user_info(self,user_id):
        data = self.read_sheet_all()
        user_info = {}
        for index, row in enumerate(data):
            if (row[0] == user_id):
                user_info = {
                    'user_id':row[0],
                    'user_name':row[1],
                    'notify_day':int(row[3])
                }
                break
        return user_info

    def write_record(self,user_id,log_type,request,response):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now = f'.{now}'
        log_data = [now,user_id,log_type,request,response]
        self.insert_sheet(log_data)