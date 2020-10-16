from openAPI import MealInfo
from DBmanager import BASED_INFO, USER_INFO
import datetime

school_data_list = list()
ATPT_OFCDC_SC_CODE_LIST = list()
ATPT_OFCDC_SC_NAME_LIST = list()
LAST_UPDATE_DATE = ''

TODAY = str(datetime.date.today()).replace('-', '')
TOMORROW = str(datetime.date.today() + datetime.timedelta(days=1)).replace('-', '')

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


def get_user_info(user_id):
    '''
    작성 : 서율
    기능 : 유저 데이터 가져오기
    '''
    sql_query_0 = {'user_id': user_id}
    sql_query_1 = {'_id': 0}

    result_dict = USER_INFO.get_user_info_from_collection(sql_query_0, sql_query_1)
    return result_dict


def lambda_handler(event, context):
    '''
    작성 : 서율
    기능 : 교육청 코드와 학교 코드로 MealInfo 객체를 만들어 급식 내용을 가져오는 API 호출한다.
    atpt_ofcdc_sc_code : 교육청 코드
    code : 학교 코드
    return : 급식 일주일 list
    '''
    init_data()
    msg = ''
    try:
        user_id = event['userRequest']['user']['id']
        params = event['action']['params']
        target_day = params['targetDay']

        if target_day == '오늘':
            target_day = TODAY
        elif target_day == '내일':
            target_day = str(datetime.date.today() + datetime.timedelta(days=1)).replace('-', '')
        elif target_day == '모레':
            target_day = str(datetime.date.today() + datetime.timedelta(days=2)).replace('-', '')
        else:
            target_day = str(datetime.date.today() + datetime.timedelta(days=3)).replace('-', '')

        user_info_dict = list(get_user_info(user_id))[0]
        atpt_ofcdc_sc_code = user_info_dict['ATPT_OFCDC_SC_CODE']
        sd_schul_code = user_info_dict['SD_SCHUL_CODE']

        mi = MealInfo(atpt_ofcdc_sc_code, sd_schul_code, target_day)
        check = mi.call_data()
        meal_list = mi.get_meal_data_list()

        for data in meal_list:
            msg += data['MMEAL_SC_NM'] + '\n'
            msg += data['DDISH_NM']
    except Exception as e:
        print(e)
        msg = '식단정보가 없습니다.'

    print(msg)
    result = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": msg}}]
        }
    }

    return result