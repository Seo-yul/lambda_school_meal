from DBmanager import BASED_INFO
import datetime

school_data_list = list()
ATPT_OFCDC_SC_CODE_LIST = list()
ATPT_OFCDC_SC_NAME_LIST = list()
LAST_UPDATE_DATE = ''

TODAY = str(datetime.date.today()).replace('-', '')
TOMORROW = str(datetime.date.today() + datetime.timedelta(days=1)).replace('-', '')
NEXT_WEEK = str(datetime.date.today() + datetime.timedelta(days=7)).replace('-', '')


def lambda_handler(event, context):
    '''
    작성 : 서율
    기능 : 최초 데이터 초기화
    '''
    atpt_ofcdc_sc_code_tuple = (
    'B10', 'C10', 'D10', 'E10', 'F10', 'G10', 'H10', 'I10', 'J10', 'K10', 'M10', 'N10', 'P10',
    'Q10', 'R10', 'S10', 'T10')
    atpt_ofcdc_sc_name_tuple = ('서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
                                '경기도', '강원도', '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도')
    data_dict = {
        'ATPT_OFCDC_SC_CODE': atpt_ofcdc_sc_code_tuple,
        'ATPT_OFCDC_SC_NAME': atpt_ofcdc_sc_name_tuple,
        'UPDATE_DATE': TODAY
    }
    last_date = {
        'last_date': TODAY
    }

    BASED_INFO.add_based_info_to_collection(data_dict)
    BASED_INFO.add_based_info_to_collection(last_date)

    msg = '데이터베이스 초기화'

    result = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": "기본 데이터베이스 초기화가 완료되었습니다."}}]
        }
    }

    return result