from concurrent.futures import ThreadPoolExecutor
from openAPI import SchoolInfo
from DBmanager import School_Info_DB, BASED_INFO
import threading
import datetime

school_data_list = list()
ATPT_OFCDC_SC_CODE_LIST = list()
ATPT_OFCDC_SC_NAME_LIST = list()
LAST_UPDATE_DATE = ''

TODAY = str(datetime.date.today()).replace('-', '')
TOMORROW = str(datetime.date.today() + datetime.timedelta(days=1)).replace('-', '')
NEXT_WEEK = str(datetime.date.today() + datetime.timedelta(days=7)).replace('-', '')


def init_data():
    '''
    작성 : 서율
    기능 : 전역변수 초기화
    '''
    global ATPT_OFCDC_SC_CODE_LIST
    global ATPT_OFCDC_SC_NAME_LIST
    global LAST_UPDATE_DATE

    sql_query_0 = {'last_date': {'$exists': 0}}  # mongoDB find sql 의 query
    sql_query_1 = {'_id': 0}
    db_cursor = BASED_INFO.get_based_info_from_collection(sql_query_0, sql_query_1)
    db_dict = dict(list(db_cursor)[0])

    ATPT_OFCDC_SC_CODE_LIST = db_dict['ATPT_OFCDC_SC_CODE']
    ATPT_OFCDC_SC_NAME_LIST = db_dict['ATPT_OFCDC_SC_NAME']

    sql_query_0 = {'last_date': {'$exists': 1}}  # mongoDB find sql 의 query
    sql_query_1 = {'_id': 0}
    db_cursor = BASED_INFO.get_based_info_from_collection(sql_query_0, sql_query_1)
    LAST_UPDATE_DATE = dict(list(db_cursor)[0])['last_date']


def fetch_school_data(atpt_ofcdc_sc_code):
    '''
    작성 : 윤서율
    기능 : 교육청 코드로 각 지역별 학교데이터 딕셔너리를 만들어 리스트에 넣는다.
    '''
    school = SchoolInfo(atpt_ofcdc_sc_code)
    print('Thread Name :', threading.current_thread().getName(), 'Start', atpt_ofcdc_sc_code)
    check = school.call_data()
    print('Thread Name :', threading.current_thread().getName(), 'Done', atpt_ofcdc_sc_code)
    if check:
        data_dict = {
            'ATPT_OFCDC_SC_CODE': atpt_ofcdc_sc_code,
            'DATA': school.get_school_data_list(),
            'UPDATE_DATE': TODAY
        }
        school_data_list.append(data_dict)


def push_school_data_db(data):
    '''
    작성 : 윤서율
    기능 : 만들어진 학교 정보 딕셔너리를 디비에 추가
    '''
    # print('Thread Name :', threading.current_thread().getName(), 'Start', atpt_ofcdc_sc_code)
    School_Info_DB.add_school_info_to_collection(data)
    # print('Thread Name :', threading.current_thread().getName(), 'Done', atpt_ofcdc_sc_code)


def lambda_handler(event, context):
    '''
    작성 : 윤서율
    기능 : 학교정보를 만들고 데이터베이스에 넣는 함수를 비동기 콜
    '''
    init_data()
    msg = '학교 정보 갱신 실패'
    print(ATPT_OFCDC_SC_CODE_LIST)
    with ThreadPoolExecutor() as executor:
        for code in ATPT_OFCDC_SC_CODE_LIST:
            executor.submit(fetch_school_data, code)

    if len(ATPT_OFCDC_SC_CODE_LIST) == len(school_data_list):
        with ThreadPoolExecutor() as executor:
            for data_dict in school_data_list:
                executor.submit(push_school_data_db, data_dict)

        sql_query_0 = {'last_date': LAST_UPDATE_DATE}
        sql_query_1 = {'$set': {'last_date': TODAY}}
        BASED_INFO.update_based_info_to_collection(sql_query_0, sql_query_1)
        msg = '학교 정보 갱신!'

    result = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": msg}}]
        }
    }

    return result