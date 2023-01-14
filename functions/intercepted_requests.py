from type import EolResponseData, EolResponse
from functions.session import session
from exceptions import NetworkException
import copy
import requests
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    datefmt="%m/%d %H:%M:%S",
    format='[%(asctime)s][%(levelname)s] %(message)s'
)

QUERY_INTERVAL = 10


def intercepted_eol_request(payload: dict, retry_interval=120) -> EolResponseData:
    """向eol.cn的接口发送请求"""
    logging.debug('正在向eol.cn发送请求')

    def send_request(payload):
        return session.post('https://api.eol.cn/web/api/', json=payload)

    # region 嗯造拦截器
    retries: int = 0
    data: requests.Response | None = None
    while True:
        data = send_request(payload)
        body: EolResponse = data.json()
        code = body['code']

        logging.debug(f'响应代码：{code}')

        if code == '0000':
            """正常"""
            if retries > 0:
                logging.info(f'第{retries}次重试成功')
            break

        if code == '1069':
            """被限速"""
            retries += 1
            logging.warning(f'请求频率过高，{retry_interval}秒后进行第{retries}次重试')
            time.sleep(retry_interval)
            continue

        if code == '1090':
            """响应体大小超出限制"""
            logging.warning('响应体大小超出限制，处理中')
            modified_payload = copy.deepcopy(payload)
            modified_payload['size'] = payload['size']
            modified_payload['page'] = (payload['page'] - 1) * 2 + 1

            time.sleep(QUERY_INTERVAL)
            page_1 = intercepted_eol_request(modified_payload)

            modified_payload['page'] += 1

            time.sleep(QUERY_INTERVAL)
            page_2 = intercepted_eol_request(modified_payload)

            page_1['item'] += page_2['item']
            logging.info('处理完成')
            return page_1

        # 上边的if一个都没匹配到的话会跑到这里来
        logging.fatal(f'未知错误：{code}')
        logging.fatal(body['message'])
        raise NetworkException('请求失败')
    # endregion

    return body['data']
