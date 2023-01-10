from type import Univ
from main import get_minium_score_of_univ, get_enroll_plan_of_majors, get_minium_score_of_majors, load_dictionary
import unittest
import requests
import json


class UnivTestCase(unittest.TestCase):
    univ_name = ''

    def setUp(self):
        self.dictionary = load_dictionary()
        res = requests.post(
            'https://api.eol.cn/web/api/',
            headers={
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'user-agent': 'Mozilla/5.0'
            },
            json={
                'keyword': self.univ_name,
                'uri': 'apidata/api/gk/school/lists',
                'page': 1,
                'size': 1,
                'request_type': 1
            }
        )
        self.assertTrue(len(res.json()['data']['item']) != 0)
        self.univ: Univ = res.json()['data']['item'][0]

    def test_get_minium_score_of_univ(self):
        error = False
        try:
            data = get_minium_score_of_univ(self.univ, self.dictionary)
            print(json.dumps(data, ensure_ascii=False, indent=4))
        except:
            error = True
        self.assertFalse(error)

    def test_get_enroll_plan_of_majors(self):
        error = False
        try:
            data = get_enroll_plan_of_majors(self.univ, self.dictionary)
            print(json.dumps(data, ensure_ascii=False, indent=4))
        except:
            error = True
        self.assertFalse(error)

    def test_get_minium_score_of_majors(self):
        error = False
        try:
            data = get_minium_score_of_majors(self.univ, self.dictionary)
            print(json.dumps(data, ensure_ascii=False, indent=4))
        except:
            error = True
        self.assertFalse(error)


class ZzucvcTestCase(UnivTestCase):
    univ_name = '郑州城建职业学院'


class SdnuTestCase(UnivTestCase):
    univ_name = '山东师范大学'


class XyqczyTestCase(UnivTestCase):
    univ_name = '襄阳汽车职业技术学院'


if __name__ == '__main__':
    unittest.main()
