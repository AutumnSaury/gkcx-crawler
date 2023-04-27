"""自定义类型"""

from typing import Optional
from .meta import *


class EolResponseData(TypedDict):
    """eol.cn的接口返回数据的data字段"""
    item: list[dict]
    numFound: int


class EolResponse(TypedDict):
    """eol.cn的接口返回的数据"""
    code: str
    data: EolResponseData
    encrydata: str
    location: str
    message: str


class Univ(TypedDict):
    """eol.cn的搜索接口返回的大学信息，这接口设计一言难尽"""
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

# region 生成表格用的类型


class MiniumScoreForUnivs(TypedDict):
    """分数线"""
    code: str
    """招生代码，不知道这玩意会不会有前导0，就用字符串了"""
    name: str
    """高校名称"""
    located_province: str
    """高校所在省份"""
    target_province: str
    """招生面向省份"""
    major: str
    """科类，文科/理科/综合（新高考）"""
    year: int
    """年份"""
    enroll_level: str
    """录取批次"""
    enroll_type: str
    """招生类型"""
    minium_score: int
    """最低分"""
    minium_rank: int
    """最低位次"""
    prov_minium_score: str
    """省控线"""
    major_group: Optional[str]
    """专业组，非新高考省份无此值"""
    subject_requirements: Optional[str]
    """选科要求，非新高考省份无此值"""


class EnrollPlan(TypedDict):
    """各专业招生计划"""
    code: str
    """招生代码"""
    name: str
    """高校名称"""
    located_province: str
    """高校所在省份"""
    target_province: str
    """招生面向省份"""
    year: int
    """年份"""
    major: str
    """科类"""
    enroll_level: str
    """招生批次"""
    major_name: str
    """招生专业名称"""
    planned_number: int
    """计划招生人数"""
    duration: str
    """学制"""
    tuition: str
    """学费"""
    major_group: Optional[str]
    """专业组"""
    subject_requirements: Optional[str]
    """选科要求"""


class MiniumScoreForMajors(TypedDict):  # Docstring是这么用的吗，写起来好难受（）
    """各专业录取分数线"""
    code: str
    """招生代码"""
    name: str
    """高校名称"""
    located_province: str
    """高校所在省份"""
    target_province: str
    """招生面向省份"""
    year: int
    """年份"""
    major: str
    """科类"""
    major_name: str
    """招生专业名称"""
    enroll_level: str
    """招生批次"""
    avg_score: str
    """平均分"""
    minium_score: int
    """最低分"""
    minium_rank: int
    """最低位次"""
    major_group: Optional[str]
    """专业组，非新高考省份无此值"""
    subject_requirements: Optional[str]
    """选科要求，非新高考省份无此值"""

# endregion
