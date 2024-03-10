import json
import logging
import time

import requests

import outlook

ACCOUNTS_FILE_PATH = "outlook_accounts.txt"
WEBSITES_FILE_PATH = "websites.txt"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/74.0.3729.131 Safari/537.36'}
# 注册uri
REGISTER_SUFFIX_URI = "/api/v1/passport/auth/register"
# 发送邮箱uri
SEND_EMAIL_SUFFIX_URI = "/api/v1/passport/comm/sendEmailVerify"
# 下单uri
ORDER_SUFFIX_URI = "/api/v1/user/order/save"
# 结账uri
CHECK_OUT_SUFFIX_URI = "/api/v1/user/order/checkout"
# 获取订阅地址uri
GET_SUBSCRIBE_URI = "/api/v1/user/getSubscribe"


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('myLogger')


# 发送post请求
def send_post_request(url, data, headers=None):
    response = requests.post(url, data=data, headers=headers)
    return response


# 发送get请求
def send_get_request(url, headers=None):
    response = requests.get(url, headers=headers)
    return response


# 读取邮箱账号和密码
def read_credentials(filename):
    credentials = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                account, password = line.split(':')
                credentials.append((account, password))
    return credentials


# 读取机场地址，邮箱是否验证，以及优惠码
def read_websites(filename):
    websites = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                origin, email_verify, discount_code = line.split(',')
                websites.append((origin, email_verify, discount_code))
    return websites


# 发送邮箱验证码
def send_email_verify(origin, email_user):
    header = HEADERS
    header['Content-Type'] = "application/x-www-form-urlencoded"
    header['Accept'] = "application/json, text/plain, */*"

    data = {
        'email': email_user
    }
    url = origin + SEND_EMAIL_SUFFIX_URI
    try:
        response = send_post_request(url, data, header)
        data = json.loads(response.text)['data']
        return data
    except Exception as e:
        logger.error(f"向{email_user}发送邮箱验证码错误:{e}")
        return False


# 注册机场账号
def register(origin, email_user, verify_code, password):
    header = HEADERS
    header['Content-Type'] = "application/x-www-form-urlencoded"
    header['Accept'] = "application/json, text/plain, */*"
    data = {
        "email": email_user,
        "password": password,
        "email_code": verify_code
    }

    url = origin + REGISTER_SUFFIX_URI
    try:
        response = send_post_request(url, data, header)
        obj={}
        if response.status_code == 200:
            obj = json.loads(response.text)
            logger.info(f"{email_user}注册成功!")
            return obj['data']['auth_data']
        else:
            logger.error(f"{email_user}注册失败!")
            return None
    except Exception as e:
        logger.error(f"{email_user}注册错误:{e}")
        return None


# 获取机场订阅
def get_subscribe(origin, email_user, auth_data):
    header = HEADERS
    header['Accept'] = "application/json, text/plain, */*"
    header['Authorization'] = auth_data
    url = origin + GET_SUBSCRIBE_URI
    try:
        response = send_get_request(url, header)
        subscibe_url = json.loads(response.text)['data']['subscribe_url']
        logger.info("获取订阅成功！")
        return subscibe_url
    except Exception as e:
        logger.error(f"{email_user}获取订阅url错误:{e}")
        return None


def main():
    # 读取txt文件中的邮箱信息
    credentials = read_credentials(ACCOUNTS_FILE_PATH)
    mail = None
    for email_user, email_pass in credentials:
        try:
            mail = outlook.login(email_user, email_pass)
            logger.info(f"\n邮箱：{email_user}登录成功！")
        except Exception as e:
            logger.error(f"\n邮箱：{email_user}\n" +
                         f"登录异常:{e}")
            continue

        websites = read_websites(WEBSITES_FILE_PATH)
        for origin, email_verify, discount_code in websites:
            verification_code = ''
            if email_verify == 't':
                # 有邮箱验证，则发送验证码到邮箱
                if send_email_verify(origin, email_user):
                    logger.info(f"向邮箱{email_user}发送验证成功！")
                    # 从邮箱获取验证码,10s等待邮箱到来
                    time.sleep(10)
                    verification_code = outlook.get_verification_code(mail, "Junk")
                    logger.info(f"Verification code for {email_user} is {verification_code}")
                else:
                    continue

            # 注册账号
            auth_data = register(origin, email_user, verification_code, email_pass)
            # 获取订阅
            subscribe_url = get_subscribe(origin, email_user, auth_data)
            logger.info(f"\n账号：{email_user}"
                        + f"\n密码：{email_pass}"
                        + f"\n订阅地址：{subscribe_url}")


if __name__ == "__main__":
    main()
