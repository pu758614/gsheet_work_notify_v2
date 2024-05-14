import datetime,time
from example.line_lib import lineLib
from example.sheet_lib import googleSheet

from example.conf import field_code_conf


def emoji(code):
    bin_str = bytes.fromhex((8 - len(code)) * '0' + code).decode('utf-32-be')
    return bin_str

def getToDayNotifyUser():
    google_sheet_lib = googleSheet('user')
    # lineLib().sendMessage('Ubdea301f314d01c74045b234820eacde','123456')
    user_list = google_sheet_lib.read_sheet_all()
    now_week_day= str(datetime.datetime.today().weekday()+1)
    notify_user_list = {}
    # for user_list取得index跟value
    for index, user_data in enumerate(user_list):
        if(index==0):
            continue
        if(now_week_day==user_data[3]):
            work_name_list = user_data[2].split('.')
            for work_name in work_name_list:
                notify_user_list[work_name] = {
                    'uuid':user_data[0],
                    'name':user_data[1],
                    'work_name':work_name_list
                }
    return notify_user_list



def daily_notify():
    now_year = datetime.datetime.now().strftime('%Y')
    next_saturday = (datetime.datetime.now() + datetime.timedelta(days=(5 - datetime.datetime.now().weekday()) % 7)).strftime('%m/%d')
    user_list = getToDayNotifyUser()
    # 如果開頭是0，去掉0
    if next_saturday[0] == '0':
        next_saturday = next_saturday[1:]
    # 把日的數字0去掉 ex:3/02 -> 3/2
    next_saturday = next_saturday.replace('/0', '/')
    google_sheet_lib = googleSheet(now_year)
    data_list = google_sheet_lib.read_sheet_all()
    notify_data_list = {}
    for row in data_list:

        date = row[0]
        if(date!=next_saturday):
            continue
        for index, row_data in enumerate(row):
            if(row_data in user_list):
                user_data = user_list[row_data]
                field_code = chr(65+index)
                if(user_data['name'] not in notify_data_list):
                    notify_data_list[user_data['name']] = {
                        'user_id':user_data['uuid'],
                        'work_item':[]
                    }
                notify_data_list[user_data['name']]['work_item'].append(field_code_conf[field_code])
    for user_name in notify_data_list:
        notify_data = notify_data_list[user_name]
        #list 轉字串
        items_str = '、'.join(notify_data['work_item'])
        msg = f"{user_name} 平安！\n您這週六({next_saturday})有{items_str}的服事，請預備心服事，願神祝福您。{emoji('10008D')}"
        lineLib().sendMessage(notify_data['user_id'],msg)
        googleSheet('record').write_record(user_name,'notify','',msg)
        time.sleep(3)
    return True

def daily_notify_test():
    now_year = datetime.datetime.now().strftime('%Y')
    next_saturday = (datetime.datetime.now() + datetime.timedelta(days=(5 - datetime.datetime.now().weekday()) % 7)).strftime('%m/%d')
    user_list = getToDayNotifyUser()
    # 如果開頭是0，去掉0
    if next_saturday[0] == '0':
        next_saturday = next_saturday[1:]
    # 把日的數字0去掉 ex:3/02 -> 3/2
    next_saturday = next_saturday.replace('/0', '/')
    google_sheet_lib = googleSheet(now_year)
    data_list = google_sheet_lib.read_sheet_all()
    notify_data_list = {}
    for row in data_list:

        date = row[0]
        if(date!=next_saturday):
            continue
        for index, row_data in enumerate(row):
            if(row_data in user_list):
                user_data = user_list[row_data]
                field_code = chr(65+index)
                if(user_data['name'] not in notify_data_list):
                    notify_data_list[user_data['name']] = {
                        'user_id':user_data['uuid'],
                        'work_item':[]
                    }
                notify_data_list[user_data['name']]['work_item'].append(field_code_conf[field_code])
    all_msg = ''
    for user_name in notify_data_list:
        notify_data = notify_data_list[user_name]
        #list 轉字串
        items_str = '、'.join(notify_data['work_item'])
        msg = f"{user_name} 平安！\n您這週六({next_saturday})有{items_str}的服事，請預備心服事，願神祝福您。{emoji('10008D')}"
        all_msg = f"{all_msg}<br>{notify_data['user_id']}--{msg}"
        # lineLib().sendMessage(notify_data['user_id'],msg)
        # googleSheet('record').write_record(user_name,'notify','',msg)

    return all_msg


# main
# if __name__ == '__main__':
#     daily_notify()
