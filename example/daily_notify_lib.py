import datetime
import time
from example.line_lib import lineLib
from example.sheet_lib import googleSheet

from example.conf import field_code_conf


def emoji(code):
    bin_str = bytes.fromhex((8 - len(code)) * '0' + code).decode('utf-32-be')
    return bin_str


def get_column_index_from_field_conf(field_name):
    for field_code, conf_name in field_code_conf.items():
        if str(conf_name).strip() == field_name:
            return ord(field_code.upper()) - ord('A')
    return None


def getToDayNotifyUser():
    google_sheet_lib = googleSheet('user')
    # lineLib().sendMessage('Ubdea301f314d01c74045b234820eacde','123456')
    user_list = google_sheet_lib.read_sheet_all()
    now_week_day = str(datetime.datetime.today().weekday()+1)
    notify_user_list = {}
    # for user_list取得index跟value
    for index, user_data in enumerate(user_list):
        if (index == 0):
            continue
        if (now_week_day == user_data[3]):
            work_name_list = user_data[2].split('.')
            for work_name in work_name_list:
                notify_user_list[work_name] = {
                    'uuid': user_data[0],
                    'name': user_data[1],
                    'work_name': work_name_list
                }
    return notify_user_list


def daily_notify():
    now_year = datetime.datetime.now().strftime('%Y')
    next_saturday = (datetime.datetime.now() + datetime.timedelta(days=(5 -
                     datetime.datetime.now().weekday()) % 7)).strftime('%m/%d')
    user_list = getToDayNotifyUser()
    # 如果開頭是0，去掉0
    if next_saturday[0] == '0':
        next_saturday = next_saturday[1:]
    # 把日的數字0去掉 ex:3/02 -> 3/2
    next_saturday = next_saturday.replace('/0', '/')
    google_sheet_lib = googleSheet(now_year)
    data_list = google_sheet_lib.read_sheet_all()
    note_col_idx = get_column_index_from_field_conf('備註')
    collect_offering_role_col_idx_set = set(
        idx for idx in [
            get_column_index_from_field_conf('小組主責'),
            get_column_index_from_field_conf('小組敬拜'),
        ] if idx is not None
    )
    notify_data_list = {}
    for row in data_list:

        date = row[0]
        if (date != next_saturday):
            continue

        # 若備註欄包含關鍵字，提醒小組主責與小組敬拜記得收奉獻
        note_text = row[note_col_idx] if (
            note_col_idx is not None and len(row) > note_col_idx) else ''
        has_offering_note = '收奉獻' in note_text

        for index, row_data in enumerate(row):
            # 處理多人服事，支援「.」、「,」和換行符號分隔
            names = [row_data]  # 預設單人
            # 先將換行符號轉換為統一分隔符
            row_data = row_data.replace('\n', '|').replace('\r', '')
            # 支援多種分隔符
            if '.' in row_data:
                names = row_data.split('.')
            elif ',' in row_data:
                names = row_data.split(',')
            elif '|' in row_data:
                names = row_data.split('|')

            for name in names:
                name = name.strip()  # 去除可能的空白
                if not name:  # 跳過空字串
                    continue
                if (name in user_list):
                    user_data = user_list[name]
                    field_code = chr(65+index)
                    if field_code not in field_code_conf:
                        continue
                    if (user_data['name'] not in notify_data_list):
                        notify_data_list[user_data['name']] = {
                            'user_id': user_data['uuid'],
                            'work_item': [],
                            'need_collect_offering': False
                        }
                    notify_data_list[user_data['name']]['work_item'].append(
                        field_code_conf[field_code])
                    if has_offering_note and index in collect_offering_role_col_idx_set:
                        notify_data_list[user_data['name']][
                            'need_collect_offering'] = True

    for user_name in notify_data_list:
        notify_data = notify_data_list[user_name]
        # list 轉字串
        items_str = '、'.join(notify_data['work_item'])
        msg = f"{user_name} 平安！\n您這週六({next_saturday})有{items_str}的服事，請預備心服事，願神祝福您。{emoji('10008D')}"
        if notify_data.get('need_collect_offering'):
            msg += "\n提醒：本次小組要收奉獻，請記得收奉獻。"
        # print(msg)
        lineLib().sendMessage(notify_data['user_id'], msg)
        googleSheet('record').write_record(user_name, 'notify', '', msg)
        # time.sleep(3)
    return True


def daily_notify_test():
    now_year = datetime.datetime.now().strftime('%Y')
    next_saturday = (datetime.datetime.now() + datetime.timedelta(days=(5 -
                     datetime.datetime.now().weekday()) % 7)).strftime('%m/%d')
    user_list = getToDayNotifyUser()
    # 如果開頭是0，去掉0
    if next_saturday[0] == '0':
        next_saturday = next_saturday[1:]
    # 把日的數字0去掉 ex:3/02 -> 3/2
    next_saturday = next_saturday.replace('/0', '/')
    google_sheet_lib = googleSheet(now_year)
    data_list = google_sheet_lib.read_sheet_all()
    note_col_idx = get_column_index_from_field_conf('備註')
    collect_offering_role_col_idx_set = set(
        idx for idx in [
            get_column_index_from_field_conf('小組主責'),
            get_column_index_from_field_conf('小組敬拜'),
        ] if idx is not None
    )
    notify_data_list = {}
    for row in data_list:

        date = row[0]
        if (date != next_saturday):
            continue

        # 若備註欄包含關鍵字，提醒小組主責與小組敬拜記得收奉獻
        note_text = row[note_col_idx] if (
            note_col_idx is not None and len(row) > note_col_idx) else ''
        has_offering_note = '收奉獻' in note_text

        for index, row_data in enumerate(row):
            # 處理多人服事，支援「.」、「,」和換行符號分隔
            names = [row_data]  # 預設單人
            # 先將換行符號轉換為統一分隔符
            row_data = row_data.replace('\n', '|').replace('\r', '')
            # 支援多種分隔符
            if '.' in row_data:
                names = row_data.split('.')
            elif ',' in row_data:
                names = row_data.split(',')
            elif '|' in row_data:
                names = row_data.split('|')

            for name in names:
                name = name.strip()  # 去除可能的空白
                if not name:  # 跳過空字串
                    continue
                if (name in user_list):
                    user_data = user_list[name]
                    field_code = chr(65+index)
                    if field_code not in field_code_conf:
                        continue
                    if (user_data['name'] not in notify_data_list):
                        notify_data_list[user_data['name']] = {
                            'user_id': user_data['uuid'],
                            'work_item': [],
                            'need_collect_offering': False
                        }
                    notify_data_list[user_data['name']]['work_item'].append(
                        field_code_conf[field_code])
                    if has_offering_note and index in collect_offering_role_col_idx_set:
                        notify_data_list[user_data['name']][
                            'need_collect_offering'] = True
    all_msg = ''
    for user_name in notify_data_list:
        notify_data = notify_data_list[user_name]
        # list 轉字串
        items_str = '、'.join(notify_data['work_item'])
        msg = f"{user_name} 平安！\n您這週六({next_saturday})有{items_str}的服事，請預備心服事，願神祝福您。{emoji('10008D')}"
        if notify_data.get('need_collect_offering'):
            msg += "\n提醒：本次小組要收奉獻，請記得收奉獻。"
        all_msg = f"{all_msg}<br>{notify_data['user_id']}--{msg}"
        # lineLib().sendMessage(notify_data['user_id'],msg)
        # googleSheet('record').write_record(user_name,'notify','',msg)
        time.sleep(3)
    return all_msg


# main
# if __name__ == '__main__':
#     daily_notify()
