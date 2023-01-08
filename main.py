import math
import requests
import csv
import logging
import time
from typing import TypedDict, Optional, Optional
import hashlib
import random

NO_UNIV_SCORE = True  # 是否不查询分数线
NO_ENROLL_PLAN = True  # 是否不查询招生计划
NO_MAJOR_SCORE = False  # 是否不查询专业分数线
PAGE_RANGE = []  # 大学列表页数范围
YEAR_SINCE = 2020  # 数据起始年份
QUERY_INTERVAL = 6  # 每次查询的间隔，单位为秒，低于5的值可能导致IP被封
PROVINCE = '河南'  # 大学所在的省份，可以参考下面的PROVIENCE_DICT填写

# region 但是这是碰都不能碰的Region

# 数字ID（行政区划代码）到省份名的映射，比较搞笑的是eol.cn的接口用到的ID有的是数字有的是字符串
PROVIENCE_DICT = {
    11: '北京',
    12: '天津',
    13: '河北',
    14: '山西',
    15: '内蒙古',
    21: '辽宁',
    22: '吉林',
    23: '黑龙江',
    31: '上海',
    32: '江苏',
    33: '浙江',
    34: '安徽',
    35: '福建',
    36: '江西',
    37: '山东',
    41: '河南',
    42: '湖北',
    43: '湖南',
    44: '广东',
    45: '广西',
    46: '海南',
    50: '重庆',
    51: '四川',
    52: '贵州',
    53: '云南',
    54: '西藏',
    61: '陕西',
    62: '甘肃',
    63: '青海',
    64: '宁夏',
    65: '新疆'
}


# 把上面的字典进行一个反的转
REV_PROVIENCE_DICT = {v: k for k, v in PROVIENCE_DICT.items()}


def generate_random_hash() -> str:
    '''生成随机的8位hash'''
    return hashlib.md5(str(random.random()).encode()).hexdigest()[:8]


HASH = generate_random_hash()  # 本次运行的HASH，用于标识CSV批次

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s] %(message)s'
                    )

# region 一些自定义类型


class Univ(TypedDict):
    '''eol.cn的搜索接口返回的大学信息，这接口设计一言难尽'''
    admissions: str
    answerurl: str
    belong: str
    central: str
    city_id: str
    city_name: str
    code_enroll: str  # 后面加了两个0的五位招生代码
    county_id: str
    county_name: str
    department: str
    doublehigh: str
    dual_class: str
    dual_class_name: str
    f211: str
    f985: str
    is_logo: str
    is_recruitment: str
    is_top: int  # ?
    level: str
    level_name: str
    name: str  # 高校名称
    nature: str
    nature_name: str
    province_id: str
    province_name: str
    rank: str
    rank_type: str
    school_id: int  # 高校ID
    school_type: str
    special: list
    type: str
    type_name: str
    view_month: str
    view_month_number: str
    view_total: str
    view_total_number: str
    view_week: str
    view_week_number: str
    view_year: int


class MiniumScoreForUnivs(TypedDict):
    '''分数线'''
    code: str
    '''招生代码，不知道这玩意会不会有前导0，就用字符串了'''
    name: str
    '''高校名称'''
    located_province: str
    '''高校所在省份'''
    target_province: str
    '''招生面向省份'''
    major: str
    '''科类，文科/理科/综合（新高考）'''
    year: int
    '''年份'''
    enroll_level: str
    '''录取批次'''
    enroll_type: str
    '''招生类型'''
    minium_score_and_rank: str
    '''最低分/最低位次'''
    prov_minium_score: str
    '''省控线'''
    major_group: Optional[str]
    '''专业组，非新高考省份无此值'''
    major_requirements: Optional[str]
    '''选科要求，非新高考省份无此值'''


class EnrollPlan(TypedDict):
    '''各专业招生计划'''
    code: str
    '''招生代码'''
    name: str
    '''高校名称'''
    located_province: str
    '''高校所在省份'''
    target_province: str
    '''招生面向省份'''
    year: int
    '''年份'''
    major: str
    '''科类'''
    enroll_level: str
    '''招生批次'''
    major_name: str
    '''招生专业名称'''
    planned_number: int
    '''计划招生人数'''
    duration: str
    '''学制'''
    tuition: str
    '''学费'''
    major_requirements: Optional[str]
    '''选科要求'''


class MiniumScoreForMajors(TypedDict):  # Docstring是这么用的吗，写起来好难受（）
    '''各专业录取分数线'''
    code: str
    '''招生代码'''
    name: str
    '''高校名称'''
    located_province: str
    '''高校所在省份'''
    target_province: str
    '''招生面向省份'''
    year: int
    '''年份'''
    major: str
    '''科类'''
    major_name: str
    '''招生专业名称'''
    enroll_level: str
    '''招生批次'''
    avg_score: str
    '''平均分'''
    minium_score_and_rank: str
    '''最低分/最低位次'''
    major_requirements: Optional[str]
    '''选科要求，非新高考省份无此值'''


# region 接口返回的元数据


class MetaProvinceScoreNewsdata(TypedDict):
    '''分数线元数据接口返回的newsdata字段'''
    province: list[int]
    '''排序过的省份ID'''
    type: dict[str, list[int]]
    '''各省各年份科类，键名格式为省份ID_四位年份，如41_2022'''
    year: dict[str, list[int]]
    '''各省招生年份，键名即省份ID'''


class MetaMiniumScoreForUnivs(TypedDict):
    '''分数线元数据'''
    data: dict
    '''看起来不怎么有用的元数据'''
    newsdata: MetaProvinceScoreNewsdata
    '''可能比较有用的元数据'''
    pids: list[int]
    '''排序过的省份ID'''
    year: list[int]
    '''年份列表'''


class MetaSpecialPlanNewsdata(TypedDict):
    '''招生计划元数据接口返回的newsdata字段'''
    batch: dict[str, list[int]]
    '''各省各年份各科类招生批次，键名格式为省份ID_四位年份_科类，如41_2022_1'''
    group: dict[str, list[dict]]
    '''各省各年份各科类专业组，不重要'''
    groups: dict[str, list[dict]]
    '''各省各年份各科类各招生批次专业组，不重要'''
    province: list[int]
    '''排序过的省份ID'''
    type: dict[str, list[int]]
    '''各省各年份科类，键名格式为省份ID_四位年份，如41_2022'''
    year: dict[str, list[int]]
    '''各省招生年份，键名即省份ID'''


class MetaEnrollPlan(TypedDict):
    '''招生计划元数据'''
    newsdata: MetaSpecialPlanNewsdata
    '''可能比较有用的元数据'''
    pids: list[int]
    '''排序过的省份ID'''
    year: list[int]
    '''年份列表'''


class MetaSpecialScoreNewsdata(TypedDict):
    '''专业分数线元数据接口返回的newsdata字段'''
    batch: dict[str, list[int]]
    '''各省各年份各科类招生批次，键名格式为省份ID_四位年份_科类，如41_2022_1'''
    group: dict[str, list[dict]]
    '''各省各年份各科类专业组，不重要'''
    groups: dict[str, list[dict]]
    '''各省各年份各科类各招生批次专业组，不重要'''
    province: list[int]
    '''排序过的省份ID'''
    type: dict[str, list[int]]
    '''各省各年份科类，键名格式为省份ID_四位年份，如41_2022'''
    year: dict[str, list[int]]
    '''各省招生年份，键名即省份ID'''


class MetaMiniumScoreForMajors(TypedDict):
    '''专业分数线元数据'''
    newsdata: MetaSpecialScoreNewsdata
    '''可能比较有用的元数据'''
    pids: list[int]
    '''排序过的省份ID'''
    year: list[int]
    '''年份列表'''
# endregion

# endregion


class NetworkException(Exception):
    '''发生网络错误时抛的异常'''
    pass


def load_dictionary() -> dict[str, str]:
    '''加载用于渲染表格的字典'''
    try:
        res = requests.get(
            'https://static-data.gaokao.cn/www/2.0/config/dicprovince/dic.json')
    except requests.exceptions.RequestException:
        raise NetworkException('加载字典时发生网络错误')
    return res.json()['data']


def query_with_retry(url: str, headers: dict, json: dict, retry_interval=120) -> requests.Response:
    def inner():
        return requests.post(url, headers=headers, json=json)
    retries = 1

    while (data := inner()).json()['code'] == '1069':
        logging.error('第%s次重试：访问频率过高，将在等待%s秒后重试' % (retries, retry_interval))
        time.sleep(retry_interval)
        retries += 1

    if (retries > 1):
        logging.info('第%s次重试成功' % retries)

    return data


def get_univ_list(prov: str, rev_prov_dict: dict[str, int] = REV_PROVIENCE_DICT) -> list[Univ]:
    '''Get the list of universities in a province.

    Args:
        prov (str): Name of the province, e.g. '河南'
        prov_dict (dict[str, str], optional): A dictionary from names to IDs for provinces. Defaults to REV_PROVIENCE_DICT.

    Returns:
        list: A list containing the list of universities in the province.

    Raises:
        NetworkException: If the request fails.

    生成Docstring的插件只提供了英文模板，那我就写英文了
    '''
    prov_id: int = rev_prov_dict[prov]
    try:
        preflight_res = query_with_retry(
            'https://api.eol.cn/web/api/',
            headers={
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'user-agent': 'Mozilla/5.0'
            },
            json={
                'province_id': prov_id,
                'uri': 'apidata/api/gk/school/lists',
                'page': 1,
                'request_type': 1
            }
        )

        if preflight_res.status_code != 200:
            raise NetworkException('网络错误')

    except requests.exceptions.RequestException:
        raise NetworkException('网络错误')

    item_count: int = preflight_res.json()['data']['numFound']
    page_count = math.ceil(item_count / 20)
    start_page = 1
    if len(PAGE_RANGE) == 2:
        page_count = min(PAGE_RANGE[1], math.ceil(item_count / 20))
        start_page = max(PAGE_RANGE[0], 1)

    univ_list = []

    for page in range(start_page, page_count + 1):
        try:
            res = query_with_retry(
                'https://api.eol.cn/web/api/',
                json={
                    'province_id': int(prov_id),
                    'uri': 'apidata/api/gk/school/lists',
                    'size': 20,
                    'page': page,
                    'request_type': 1
                },
                headers={
                    'accept': 'application/json, text/plain, */*',
                    'content-type': 'application/json;charset=UTF-8',
                    'user-agent': 'Mozilla/5.0'
                    # 确实做了UA检测，但是没完全做
                }
            )

            if res.status_code != 200:
                raise NetworkException('网络错误')

            time.sleep(QUERY_INTERVAL)

        except requests.exceptions.RequestException:
            raise NetworkException('网络错误')

        univ_list += res.json()['data']['item']

    return univ_list


def get_minium_score_of_univ(univ: Univ, dictionary: dict[str, str], prov_dict: dict[int, str] = PROVIENCE_DICT) -> list[MiniumScoreForUnivs]:
    '''获取高校各省各年份分数线'''
    school_id = univ['school_id']
    try:
        res = requests.get(
            'https://static-data.gaokao.cn/www/2.0/school/%s/dic/provincescore.json' % school_id)
    except requests.exceptions.RequestException:
        raise NetworkException('网络错误')
    metadata: MetaMiniumScoreForUnivs = res.json()['data']

    ret_list: list[MiniumScoreForUnivs] = []

    for prov_id in metadata['newsdata']['province']:
        year_list = metadata['newsdata']['year'][str(prov_id)]
        year_list = filter(lambda x: x >= YEAR_SINCE, year_list)
        for year in year_list:
            for major_id in metadata['newsdata']['type']['%s_%s' % (prov_id, year)]:
                try:
                    res = requests.get('https://static-data.gaokao.cn/www/2.0/schoolprovinceindex/%s/%s/%s/%s/1.json'
                                       % (year, school_id, prov_id, major_id)
                                       )
                    if res.status_code != 200:
                        raise NetworkException('网络错误')
                except requests.exceptions.RequestException:
                    raise NetworkException('网络错误')
                data = res.json()['data']
                for item in data['item']:
                    new_row: MiniumScoreForUnivs = {
                        'code': univ['code_enroll'][:5],
                        'name': univ['name'],
                        'located_province': univ['province_name'],
                        'target_province': prov_dict[prov_id],
                        'major': dictionary[str(major_id)],
                        'year': year,
                        'enroll_level': item['local_batch_name'],
                        'enroll_type': item['zslx_name'],
                        'minium_score_and_rank': '%s/%s' % (item['min'], item['min_section']),
                        'prov_minium_score': item['proscore'],
                        'major_group': item['sg_name'],
                        'major_requirements': item['sg_info']
                    }
                    ret_list.append(new_row)

    return ret_list


def get_enroll_plan_of_majors(univ: Univ, dictionary: dict[str, str], prov_dict: dict[int, str] = PROVIENCE_DICT) -> list[EnrollPlan]:
    '''获取高校招生计划'''
    school_id = univ['school_id']
    try:
        res = requests.get(
            'https://static-data.gaokao.cn/www/2.0/school/%s/dic/specialplan.json' % school_id)
    except requests.exceptions.RequestException:
        raise NetworkException('网络错误')
    metadata: MetaEnrollPlan = res.json()['data']

    ret_list: list[EnrollPlan] = []

    for prov_id in metadata['newsdata']['province']:
        year_list = metadata['newsdata']['year'][str(prov_id)]
        year_list = filter(lambda x: x >= YEAR_SINCE, year_list)
        for year in year_list:
            for major_id in metadata['newsdata']['type']['%s_%s' % (prov_id, year)]:
                for batch_id in metadata['newsdata']['batch']['%s_%s_%s' % (prov_id, year, major_id)]:
                    try:
                        res = query_with_retry(
                            'https://api.eol.cn/web/api/',
                            headers={
                                'accept': 'application/json, text/plain, */*',
                                'content-type': 'application/json;charset=UTF-8',
                                'user-agent': 'Mozilla/5.0'
                            },
                            json={
                                'local_batch_id': batch_id,
                                'local_province_id': prov_id,
                                'local_type_id': str(major_id),
                                'page': 1,
                                'school_id': school_id,
                                'size': 30,
                                'uri': 'apidata/api/gkv3/plan/school',
                                'year': year
                            }
                        )
                    except requests.exceptions.RequestException:
                        raise NetworkException('网络错误')

                    total_items = res.json()['data']['numFound']
                    total_pages = math.ceil(total_items / 30)

                    for page in range(1, total_pages + 1):
                        try:
                            time.sleep(QUERY_INTERVAL)
                            res = query_with_retry(
                                'https://api.eol.cn/web/api/',
                                headers={
                                    'accept': 'application/json, text/plain, */*',
                                    'content-type': 'application/json;charset=UTF-8',
                                    'user-agent': 'Mozilla/5.0'
                                },
                                json={
                                    'local_batch_id': batch_id,
                                    'local_province_id': prov_id,
                                    'local_type_id': str(major_id),
                                    'page': page,
                                    'school_id': school_id,
                                    'size': 30,
                                    'uri': 'apidata/api/gkv3/plan/school',
                                    'year': year
                                }
                            )
                        except requests.exceptions.RequestException:
                            raise NetworkException('网络错误')

                        data = res.json()['data']

                        for item in data['item']:
                            new_row: EnrollPlan = {
                                'code': univ['code_enroll'][:5],
                                'name': univ['name'],
                                'located_province': univ['province_name'],
                                'target_province': prov_dict[prov_id],
                                'year': year,
                                'major': dictionary[str(major_id)],
                                'enroll_level': data['item'][0]['local_batch_name'],
                                'major_name': item['spname'],
                                'planned_number': item['num'],
                                'duration': item['length'],
                                'tuition': item['tuition'],
                                'major_requirements': item['sp_info'],
                            }
                            ret_list.append(new_row)

    return ret_list


def get_minium_score_of_majors(univ: Univ, dictionary: dict[str, str], prov_dict: dict[int, str] = PROVIENCE_DICT) -> list[MiniumScoreForMajors]:
    '''获取高校专业分数线'''
    school_id = univ['school_id']
    try:
        res = requests.get(
            'https://static-data.gaokao.cn/www/2.0/school/%s/dic/specialplan.json' % school_id)
    except requests.exceptions.RequestException:
        raise NetworkException('网络错误')
    metadata: MetaMiniumScoreForMajors = res.json()['data']

    ret_list: list[MiniumScoreForMajors] = []

    for prov_id in metadata['newsdata']['province']:
        year_list = metadata['newsdata']['year'][str(prov_id)]
        year_list = filter(lambda x: x >= YEAR_SINCE, year_list)
        for year in year_list:
            for major_id in metadata['newsdata']['type']['%s_%s' % (prov_id, year)]:
                for batch_id in metadata['newsdata']['batch']['%s_%s_%s' % (prov_id, year, major_id)]:
                    try:
                        res = query_with_retry(
                            'https://api.eol.cn/web/api/',
                            headers={
                                'accept': 'application/json, text/plain, */*',
                                'content-type': 'application/json;charset=UTF-8',
                                'user-agent': 'Mozilla/5.0'
                            },
                            json={
                                'local_batch_id': batch_id,
                                'local_province_id': prov_id,
                                'local_type_id': str(major_id),
                                'page': 1,
                                'school_id': school_id,
                                'size': 30,
                                'uri': 'apidata/api/gk/score/special',
                                'year': year
                            }
                        )
                    except requests.exceptions.RequestException:
                        raise NetworkException('网络错误')

                    total_items = res.json()['data']['numFound']
                    total_pages = math.ceil(total_items / 30)

                    for page in range(1, total_pages + 1):
                        try:
                            time.sleep(QUERY_INTERVAL)
                            res = query_with_retry(
                                'https://api.eol.cn/web/api/',
                                headers={
                                    'accept': 'application/json, text/plain, */*',
                                    'content-type': 'application/json;charset=UTF-8',
                                    'user-agent': 'Mozilla/5.0'
                                },
                                json={
                                    'local_batch_id': batch_id,
                                    'local_province_id': prov_id,
                                    'local_type_id': str(major_id),
                                    'page': page,
                                    'school_id': school_id,
                                    'size': 30,
                                    'uri': 'apidata/api/gk/score/special',
                                    'year': year
                                }
                            )
                        except requests.exceptions.RequestException:
                            raise NetworkException('网络错误')

                        data = res.json()['data']

                        for item in data['item']:
                            new_row: MiniumScoreForMajors = {
                                'code': univ['code_enroll'][:5],
                                'name': univ['name'],
                                'located_province': univ['province_name'],
                                'target_province': prov_dict[prov_id],
                                'year': year,
                                'major': dictionary[str(major_id)],
                                'major_name': item['spname'],
                                'enroll_level': data['item'][0]['local_batch_name'],
                                'avg_score': item['average'],
                                'minium_score_and_rank': '%s/%s' % (item['min'], item['min_section']),
                                'major_requirements': item['sp_info'],
                            }
                            ret_list.append(new_row)
    return ret_list


def main():
    try:
        logging.info('开始获取大学列表')
        univ_list: list[Univ] = get_univ_list('河南')
    except NetworkException:
        logging.fatal('获取大学列表时发生网络异常')
        exit(1)

    try:
        logging.info('开始获取专业字典')
        dictionary = load_dictionary()
    except NetworkException:
        logging.fatal('获取专业字典时发生网络异常')
        exit(1)

    if not NO_UNIV_SCORE:
        logging.info('开始获取高校各省分数线')
        with open('min_score_%s.csv' % HASH, 'w', encoding='utf-8') as csvfile:
            csvwriter = csv.DictWriter(
                csvfile, fieldnames=MiniumScoreForUnivs.__annotations__.keys()
            )
            csvwriter.writeheader()
            for univ in univ_list:
                try:
                    logging.info('正在获取%s分数线' % univ['name'])
                    score_list = get_minium_score_of_univ(univ, dictionary)
                except NetworkException:
                    logging.fatal('获取%s的分数线时发生网络异常' % univ['name'])
                    exit(1)
                for score in score_list:
                    csvwriter.writerow(score)
                logging.info('成功获取%s分数线信息' % univ['name'])
        logging.info('已获取全部高校分数线信息')

    if not NO_ENROLL_PLAN:
        logging.info('开始获取高校各专业招生计划')
        with open('enroll_plan_%s.csv' % HASH, 'w', encoding='utf-8') as csvfile:
            csvwriter = csv.DictWriter(
                csvfile, fieldnames=EnrollPlan.__annotations__.keys()
            )
            csvwriter.writeheader()
            for univ in univ_list:
                try:
                    logging.info('正在获取%s招生计划' % univ['name'])
                    plan_list = get_enroll_plan_of_majors(univ, dictionary)
                except NetworkException:
                    logging.fatal('获取%s的招生计划时发生网络异常' % univ['name'])
                    exit(1)
                for plan in plan_list:
                    csvwriter.writerow(plan)
                logging.info('成功获取%s招生计划信息' % univ['name'])
        logging.info('已获取全部高校招生计划信息')

    if not NO_MAJOR_SCORE:
        logging.info('开始获取高校各专业分数线')
        with open('major_score_%s.csv' % HASH, 'w', encoding='utf-8') as csvfile:
            csvwriter = csv.DictWriter(
                csvfile, fieldnames=MiniumScoreForMajors.__annotations__.keys()
            )
            csvwriter.writeheader()
            for univ in univ_list:
                try:
                    logging.info('正在获取%s各专业分数线' % univ['name'])
                    major_score = get_minium_score_of_majors(univ, dictionary)
                except NetworkException:
                    logging.fatal('获取%s的各专业分数线时发生网络异常' % univ['name'])
                    exit(1)
                for score in major_score:
                    csvwriter.writerow(score)
                logging.info('成功获取%s各专业分数线信息' % univ['name'])
        logging.info('已获取全部高校各专业分数线信息')

    logging.info('已成功爬取所有数据')


main()

# endregion