from DBmanager import School_Info_DB, BASED_INFO, USER_INFO
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


def get_local_school_list(atpt_ofcdc_sc_code, schul_nm) -> list:
    '''
    작성 : 서율
    기능 : 교육청에 따른 학교 정보 가져오는 함수
    atpt_ofcdc_sc_code : 교육청 코드
    schul_nm : 학교이름
    return : data_list 지역의 학교 정보
    '''
    sql_query_0 = {'ATPT_OFCDC_SC_CODE': atpt_ofcdc_sc_code, 'UPDATE_DATE': LAST_UPDATE_DATE}
    sql_query_1 = {'_id': 0, 'ATPT_OFCDC_SC_CODE': 0, 'UPDATE_DATE': 0}

    db_cursor = School_Info_DB.get_school_info_from_collection(sql_query_0, sql_query_1)
    db_dict = list(db_cursor)[0]

    data_list = [data for data in db_dict['DATA'] if data['SCHUL_NM'] == schul_nm]
    return data_list


def lambda_handler(event, context):
    '''
    작성 : 서율
    기능 : 교육청 코드와 학교 코드로 MealInfo 객체를 만들어 급식 내용을 가져오는 API 호출한다.
    atpt_ofcdc_sc_code : 교육청 코드
    code : 학교 코드
    return : 급식 일주일 list
    '''

    init_data()
    msg = '?'
    try:
        user_id = event['userRequest']['user']['id']
        params = event['action']['params']
        schul_grade = params['SchulGrade']
        schul_nm = params['SchulNm'] + schul_grade

        print(schul_nm)
        msg = '먼저 지역을 등록해 주세요'
        user_info_dict = list(get_user_info(user_id))[0]
        atpt_ofcdc_sc_code = user_info_dict['ATPT_OFCDC_SC_CODE']

        msg = '학교 전체 이름을 바르게 입력해주세요.'
        sc_data_list = get_local_school_list(atpt_ofcdc_sc_code, schul_nm)[0]
        sd_schul_code = sc_data_list['SD_SCHUL_CODE']

        if not user_info_dict.get('SCHUL_NM'):
            msg = '학교를 등록하였습니다.'

        else:
            msg = '학교를 변경하였습니다.'
        sql_query_0 = {'user_id': user_id}
        sql_query_1 = {'$set': {'SCHUL_NM': schul_nm, 'SD_SCHUL_CODE': sd_schul_code}}
        USER_INFO.update_user_info_to_collection(sql_query_0, sql_query_1)
    except Exception as e:
        print('에러발생', e)

    result = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": msg}}]
        }
    }

    return result