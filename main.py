import json
import logging
import os

import requests

import outlook

ACCOUNTS_FILE_PATH = "outlook_accounts.txt"
WEBSITES_FILE_PATH = "websites.txt"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/121.0.0.0 Safari/537.36'}
# 注册uri
REGISTER_SUFFIX_URI = "/api/v1/passport/auth/register"
# 登录uri
LOGIN_SUFFIX_URI = "/api/v1/passport/auth/login"
# 发送邮箱uri
SEND_EMAIL_SUFFIX_URI = "/api/v1/passport/comm/sendEmailVerify"
# 获取套餐uri
PLAN_FETCH_SUFFIX_URI = "/api/v1/user/plan/fetch"
# 校验优惠码uri
CHECK_COUPON_SUFFIX_URI = "/api/v1/user/coupon/check"
# 获取支付方式uri
PAYMENT_METHOD_URI = "/api/v1/user/order/getPaymentMethod"
# 下单uri
ORDER_SUFFIX_URI = "/api/v1/user/order/save"
# 结账uri
CHECK_OUT_SUFFIX_URI = "/api/v1/user/order/checkout"
# 获取订阅地址uri
GET_SUBSCRIBE_URI = "/api/v1/user/getSubscribe"

# 配置文件路径
CONFIG_PATH = os.path.join('', 'config.json')

response = None
auth_data = None
mail = None


# 读取配置文件
with open(CONFIG_PATH, 'r') as f:
    config_json = json.load(f)
    proxy = config_json['proxy']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('myLogger')
console_handler = logging.StreamHandler()
console_handler.setLevel(level="WARNING")
console_fmt = "%(name)s--->%(asctime)s--->%(message)s--->%(lineno)d"
console_handler.setFormatter(fmt=logging.Formatter(fmt=console_fmt))


# 发送post请求
def send_post_request(url, data, headers=None):
    global response
    response = requests.post(url, data=json.dumps(data), headers=headers, proxies={"http": proxy, "https": proxy})
    return response


def send_post_json_request(url, data, headers=None):
    global response
    response = requests.post(url, data=data, headers=headers, proxies={"http": proxy, "https": proxy})
    return response


# 发送get请求
def send_get_request(url, headers=None):
    global response
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
                origin, email_verify, coupon_code = line.split(',')
                websites.append((origin, email_verify, coupon_code))
    return websites


# 登录
def login(origin, email_user, email_pass):
    global response
    header = HEADERS
    header['Accept'] = "application/json, text/plain, */*"
    header['Content-Type'] = "application/json"
    header['Content-Language'] = "lang=zh-CN"

    data = {
        "email": email_user,
        "password": email_pass
    }
    url = origin + LOGIN_SUFFIX_URI
    try:
        response = send_post_request(url, data, header)
        data = json.loads(response.text)['data']
        return data
    except Exception as e:
        logger.error(f"{email_user}登录失败，错误:{e},返回信息：{response.text}")
        return None


# 发送邮箱验证码
def send_email_verify(origin, email_user):
    header = HEADERS
    header['Content-Type'] = "application/x-www-form-urlencoded"
    header['Accept'] = "application/json, text/plain, */*"

    data = {
        'email': email_user
    }
    url = origin + SEND_EMAIL_SUFFIX_URI
    global response
    try:
        response = send_post_json_request(url, data, header)
        data = json.loads(response.text)['data']
        return data
    except Exception as e:
        logger.error(f"{email_user}发送验证码错误:{e},返回信息：{response.text}")
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
    global response
    try:
        response = send_post_json_request(url, data, header)
        if response.status_code == 200:
            obj = json.loads(response.text)
            logger.info(f"{email_user}注册成功!")
            return obj['data']['auth_data']
        else:
            logger.error(f"{email_user}注册失败:{response.json()['message']}")
            return None
    except Exception as e:
        logger.error(f"{email_user}注册错误:{e},返回信息：{response.text}")
        return None


# 获取套餐
def fetch_plan(origin, email_user, auth_data):
    header = HEADERS
    header['Content-Type'] = "application/json;charset=UTF-8"
    header['Accept'] = "application/json"
    header['Authorization'] = auth_data
    url = origin + PLAN_FETCH_SUFFIX_URI
    global response
    try:
        response = send_get_request(url, header)
        obj = json.loads(response.text)
        logger.info(f"{email_user}获取套餐成功！")
        return obj['data'][0]['id']
    except Exception as e:
        logger.error(f"{email_user}获取套餐错误:{e},返回信息：{response.text}")
        return None


# 校验优惠码
def check_coupon(origin, email_user, auth_data, coupon_code, plan_id):
    header = HEADERS
    header['Content-Type'] = "application/json;charset=UTF-8"
    header['Accept'] = "application/json"
    header['Authorization'] = auth_data
    data = {
        "code": coupon_code,
        "plan_id": plan_id
    }
    url = origin + CHECK_COUPON_SUFFIX_URI
    global response
    try:
        response = send_post_request(url, data, header)
        obj = json.loads(response.text)
        logger.info(f"{email_user}校验优惠码成功！")
        return obj
    except Exception as e:
        logger.error(f"{email_user}校验优惠码错误:{e},返回信息：{response.text}")
        return None


# 下单
def order(origin, email_user, auth_data, coupon_code, plan_id):
    header = HEADERS
    header['Accept'] = "application/json, text/plain, */*"
    header['Authorization'] = auth_data
    data = {
        "coupon_code": coupon_code,
        "period": "month_price",
        "plan_id": plan_id,
    }
    url = origin + ORDER_SUFFIX_URI
    global response
    try:
        response = send_post_request(url, data, header)
        if response.status_code == 200:
            obj = json.loads(response.text)
            logger.info(f"{email_user}下单成功！")
            return obj
        else:
            logger.error(f"{email_user}下单失败:{response.json()['message']}")
            return None
    except Exception as e:
        logger.error(f"{email_user}下单错误:{e},返回信息：{response.text}")
        return None


# 获取支付方式
def get_payment_method(origin, email_user, auth_data):
    header = HEADERS
    header['Accept'] = "application/json, text/plain, */*"
    header['Authorization'] = auth_data
    url = origin + PAYMENT_METHOD_URI
    global response
    try:
        response = send_get_request(url, header)
        obj = json.loads(response.text)
        logger.info(f"{email_user}获取支付方式成功！")
        return obj['data'][0]['id']
    except Exception as e:
        logger.error(f"{email_user}获取支付方式错误:{e},返回信息：{response.text}")
        return None


# 结账
def check_out(origin, email_user, auth_data, trade_no, payment_method):
    header = HEADERS
    header['Accept'] = "application/json, text/plain, */*"
    header['Authorization'] = auth_data
    url = origin + CHECK_OUT_SUFFIX_URI
    data = {
        "trade_no": trade_no,
        "method": payment_method
    }
    global response
    try:
        response = send_post_request(url, data, header)
        obj = json.loads(response.text)
        logger.info(f"{email_user}结账成功！")
        return obj
    except Exception as e:
        logger.error(f"{email_user}结账错误:{e},返回信息：{response.text}")
        return None


# 获取机场订阅
def get_subscribe(origin, email_user, auth_data):
    header = HEADERS
    header['Accept'] = "application/json, text/plain, */*"
    header['Authorization'] = auth_data
    url = origin + GET_SUBSCRIBE_URI
    global response
    try:
        response = send_get_request(url, header)
        subscribe_url = json.loads(response.text)['data']['subscribe_url']
        logger.info("获取订阅成功！")
        return subscribe_url
    except Exception as e:
        logger.error(f"{email_user}获取订阅url错误:{e},返回信息：{response.text}")
        return None


def main():
    # 读取txt文件中的邮箱信息
    credentials = read_credentials(ACCOUNTS_FILE_PATH)
    global mail
    for email_user, email_pass in credentials:
        try:
            mail = outlook.login(email_user, email_pass)
            logger.info(f"\n邮箱：{email_user}登录成功！")
        except Exception as e:
            logger.error(f"\n邮箱：{email_user}\n" +
                         f"登录异常:{e}")
            continue

        websites = read_websites(WEBSITES_FILE_PATH)
        for origin, email_verify, coupon_code in websites:
            # 登录判断是否已经注册
            login_res = login(origin, email_user, email_pass[:16])
            global auth_data
            if login_res is not None:
                logger.info(f"{email_user}已经在{origin}注册！")
                auth_data = login_res['auth_data']
            else:
                logger.info(f"{email_user}未在{origin}注册！")
                verification_code = None
                if email_verify == 't':
                    # 有邮箱验证，则发送验证码到邮箱
                    if send_email_verify(origin, email_user):
                        logger.info(f"已向邮箱{email_user}发送验证码！")
                        verification_code = outlook.get_verification_code(mail)
                        if verification_code is None:
                            logger.error(f"获取邮箱{email_user}验证码失败！")
                            continue
                        logger.info(f"Verification code for {email_user} is {verification_code}")
                    else:
                        continue
                # 注册账号，获得授权码
                auth_data = register(origin, email_user, verification_code, email_pass[:16])
                if auth_data is None:
                    continue

            # 判断是否有优惠码
            if coupon_code is not None and coupon_code != "":
                # 获取套餐
                plan_id = fetch_plan(origin, email_user, auth_data)
                if plan_id is None:
                    continue
                # 校验优惠码
                check_out_res = check_coupon(origin, email_user, auth_data, coupon_code, plan_id)
                if check_out_res is None:
                    continue
                # 下单
                order_res = order(origin, email_user, auth_data, coupon_code, plan_id)
                if order_res is None:
                    continue
                trade_no = order_res['data']
                # 获取支付方式
                payment_method = get_payment_method(origin, email_user, auth_data)
                if payment_method is None:
                    continue
                # 结账
                check_out_res = check_out(origin, email_user, auth_data, trade_no, payment_method)
                if check_out_res is None:
                    continue
            else:
                pass
            # 获取订阅地址
            subscribe_url = get_subscribe(origin, email_user, auth_data)
            airport_link_info = f"账号：{email_user}" + f"\n密码：{email_pass[:16]}" + f"\n订阅地址：{subscribe_url}\n"
            logger.info("\n" + airport_link_info)
            with open("airport_link_info.txt", "a", encoding="utf-8") as file:
                file.write(airport_link_info)
        # 邮箱退出登录
        mail.logout()


if __name__ == "__main__":
    main()
