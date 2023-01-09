from typing import TypedDict


class MetaProvinceScoreNewsdata(TypedDict):
    """分数线元数据接口返回的newsdata字段"""
    province: list[int]
    """排序过的省份ID"""
    type: dict[str, list[int]]
    """各省各年份科类，键名格式为省份ID_四位年份，如41_2022"""
    year: dict[str, list[int]]
    """各省招生年份，键名即省份ID"""


class MetaMiniumScoreForUnivs(TypedDict):
    """分数线元数据"""
    data: dict
    """看起来不怎么有用的元数据"""
    newsdata: MetaProvinceScoreNewsdata
    """可能比较有用的元数据"""
    pids: list[int]
    """排序过的省份ID"""
    year: list[int]
    """年份列表"""


class MetaSpecialPlanNewsdata(TypedDict):
    """招生计划元数据接口返回的newsdata字段"""
    batch: dict[str, list[int]]
    """各省各年份各科类招生批次，键名格式为省份ID_四位年份_科类，如41_2022_1"""
    group: dict[str, list[dict]]
    """各省各年份各科类专业组，不重要"""
    groups: dict[str, list[dict]]
    """各省各年份各科类各招生批次专业组，不重要"""
    province: list[int]
    """排序过的省份ID"""
    type: dict[str, list[int]]
    """各省各年份科类，键名格式为省份ID_四位年份，如41_2022"""
    year: dict[str, list[int]]
    """各省招生年份，键名即省份ID"""


class MetaEnrollPlan(TypedDict):
    """招生计划元数据"""
    newsdata: MetaSpecialPlanNewsdata
    """可能比较有用的元数据"""
    pids: list[int]
    """排序过的省份ID"""
    year: list[int]
    """年份列表"""


class MetaSpecialScoreNewsdata(TypedDict):
    """专业分数线元数据接口返回的newsdata字段"""
    batch: dict[str, list[int]]
    """各省各年份各科类招生批次，键名格式为省份ID_四位年份_科类，如41_2022_1"""
    group: dict[str, list[dict]]
    """各省各年份各科类专业组，不重要"""
    groups: dict[str, list[dict]]
    """各省各年份各科类各招生批次专业组，不重要"""
    province: list[int]
    """排序过的省份ID"""
    type: dict[str, list[int]]
    """各省各年份科类，键名格式为省份ID_四位年份，如41_2022"""
    year: dict[str, list[int]]
    """各省招生年份，键名即省份ID"""


class MetaMiniumScoreForMajors(TypedDict):
    """专业分数线元数据"""
    newsdata: MetaSpecialScoreNewsdata
    """可能比较有用的元数据"""
    pids: list[int]
    """排序过的省份ID"""
    year: list[int]
    """年份列表"""
