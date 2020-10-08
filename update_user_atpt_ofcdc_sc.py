from DBmanager import BASED_INFO, USER_INFO
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
    기능 : 유저 지역 이름 등록, 수정
    처음 등록이라면 디비에 등록, 아니라면 수정
    user_id : 챗봇 유저 아이디
    atpt_ofcdc_sc_name : 지역명
    '''
    init_data()
    msg = ''
    try:
        user_id = event['userRequest']['user']['id']
        params = event['action']['params']
        atpt_ofcdc_sc_name = params['AtptOfcdcScName']

        index = ATPT_OFCDC_SC_NAME_LIST.index(atpt_ofcdc_sc_name)
        user_info_dict = get_user_info(user_id)
        ck = len(list(user_info_dict))

        if ck:
            sql_query_0 = {'user_id': user_id}
            sql_query_1 = {
                '$set': {'ATPT_OFCDC_SC_NAME': atpt_ofcdc_sc_name,
                         'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE_LIST[index]}}
            USER_INFO.update_user_info_to_collection(sql_query_0, sql_query_1)
            msg = atpt_ofcdc_sc_name + "로 지역을 변경하였습니다."
        else:
            sql_query = {
                'user_id': user_id,
                'ATPT_OFCDC_SC_NAME': atpt_ofcdc_sc_name,
                'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE_LIST[index]
            }
            USER_INFO.add_user_info_to_collection(sql_query)
            msg = atpt_ofcdc_sc_name + "로 지역을 등록하였습니다."


    except:
        msg = '지역등록과 학교등록을 확인해주시기 바랍니다.'

    result = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": msg}}]
        }
    }

    return result