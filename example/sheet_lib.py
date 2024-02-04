import pygsheets


class googleSheet:
    def __init__(self, sheet_title):
        # self.spreadsheet_id = spreadsheet_id
        survey_url = 'https://docs.google.com/spreadsheets/d/1YC0ZVH-xyqAypAp47CnWzmTcFZWsyhRZGI7Gc_GEb5I/edit#gid=507784060'
        self.gc = pygsheets.authorize(service_account_file='/code/credentials.json')
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

    def update_sheet(self, site, data):
        try:
            worksheet = self.sheet.worksheet_by_title(self.sheet_title)
            worksheet.update_value(site, data)
        except Exception as e:
           return False
        return True



# Usage example
# spreadsheet_id = '17fti37_SPCGL2lSESR1AFEIwy-7DfBw3GKIlp2fZH7Y'
sheet = googleSheet('user')
# # new_sheet = sheet.create_sheet('New Sheet')
# # data = [['Name', 'Age'], ['John', '25'], ['Jane', '30']]
# # sheet.update_sheet('New Sheet', data)
# sheet_data = sheet.read_sheet_all()
# print(sheet_data)
sheet_data = sheet.update_sheet('A1', 'test')


print(sheet_data)
# # sheet.delete_sheet('New Sheet')

# credentials = {
#     "type": "service_account",
#     "client_id": "111676479322924520930",
#     "client_email": "sheet-216@mimetic-perigee-236704.iam.gserviceaccount.com",
#     "private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCcap91kE0Fa/+k\nEWYX9EliVe3cSqsD+5lChJ1CSK8WVh/yCMXCCM1+hImfshfnEYVin+9I3dVa/fRx\nR1LU4u5dFQKQhTC0ZWLolMPvKGO7L6m4FJNFfuL5USC3du+7ZLxPjVX+407XTfZv\nBL1b3LOjnXFBB/0sXIfqac1nrepdHSBeNv79fdsTsCGbLbz8S8caXIfXYqsK2y1W\nuIXR+WY4R5KLce7GP7W0n97FArLA5GNDl9Xlo84zM7cfRw4ZoGzhmBTdwy6G1QpL\nV2S3m4jVioYX3XLMT3BwGI1uBKuP8w7VBJQZTs3RE1L67Z3JO+g4IF+Q1wSxQbMY\nsc2iLLz5AgMBAAECggEABODx/ZCdSGOilv9YbfuXfN7VgxMco6yJrpiUj5xVArc3\nupzBr1BHOZCgesfLJVDHdmiq5dzOcm68nLpm5982pFZbDL8swlmttLesJ1XdC3n8\nexKAN/ER2wkn4jUOW+vT0E7mHWPBYieLPdH55oc7Hqmy3j6Fq+gscJgxeRAEgPgy\nvHf8WvXfHTU2DNDmAjY4mJ5rGGvjj+T1MJL6HI5fif5s7q4MV/ssAwD8NQqoWMpF\nknOta7lyxmxShtMYlL1crG5AvJyx4c46aXgImujRXs0ZRMF6LWZ9nItnXxVTJ9Q9\nhx87BywWlAIlQVqCXcHJXOpeMqVjy/feZf9ZZ4floQKBgQDO3s2jG3T0zdFFAZur\nvJvOUIQ5be0tBSA1Yjz3FJluBcv+VMtcHnBKjJ16cLexMrcWHvbNJ7SycaGTONQg\nG5mC1A2BmFg6Tv897LDe+1XLiRCf2HfQPYwY4fGDrajG3LAvRV5D41EkWiqKs/fi\nTNEbsaZF6D4WTHDRLatkUBWaGQKBgQDBkFp2TI07/NkVjElHmnyaDRRoq03jXcD4\nK5DnIyG/Awm7bkYjMOFQDUGIKMpCw29NhagMNsHR1eDbor41eei+NvD7hDuRc/tn\nn4uyX7dfYy3jMpOO8S2iqWe/yPHFp0xowoKuJpp9anua9QmWEcZA/GvXH+vsbGdD\nBle31/ZV4QKBgAWVfAWAEzscZx6uuW38TFRYVglaz0Ec1065lR2yP6X5oBUAYvDc\nnXlVrFaGvl6ZGNoPAehtvvHmIU9hBFDNjeo7IRYzb4Y7ZaZdQjTyodE5pOo7pJhJ\nYQO27Zb5VAnyIQtVmwLIGwOZL3bI/tLr8eUGeY9/glWFwLHUwsCVbM/ZAoGAJhah\ntmWZ5RP8I6FXSh+8JRQtz+rliLgKIMtx2AmxukR+xcMNSh90NqxlGMXuBvUuEbMb\nPkwIF6JefNmpVByJD+T/xn5eumB4OAvNEWyESODbRrnND3Ol5zwuji6cZKhnALZF\nwL8X51XsvLE7Eayttlv1XH+LjRpHt4in+iUk9AECgYEAwx1VxTStp+W3xIvg9yb6\nP54FIO33GLWB9s3GB2Yvs33RwoLIoiqSpqFXdf1L2IYzptJ4LqjG4sArFkgPEln1\nnE6qLl/G5XIiJmaKew2e7RAITGf5FkXTIHOWr27MPOws5tMjOoEDCvXX6weneTZq\nL18FDrpF8tw1BWm9m0lw1lo=\n-----END PRIVATE KEY-----\n"
# }
# gc = pygsheets.authorize(service_account_file='/code/credentials.json')

# survey_url = 'https://docs.google.com/spreadsheets/d/1YC0ZVH-xyqAypAp47CnWzmTcFZWsyhRZGI7Gc_GEb5I/edit#gid=507784060'
# sh = gc.open_by_url(survey_url)
# ws = sh.worksheet_by_title('2024')
# val = ws.get_value('B4')
# print(val)
