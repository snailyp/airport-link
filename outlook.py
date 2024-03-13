import email
import imaplib
import re
import time
import threading

# 创建一个标志，用于通知其他线程停止检查新邮件
stop_checking = threading.Event()

# 创建一个变量，用于存储检测到新邮件的文件夹的名称
first_new_mail_folder = None


def login(email_user, email_pass):
    # 连接到outlook邮箱服务器
    mail = imaplib.IMAP4_SSL("outlook.office365.com")
    mail.login(email_user, email_pass)
    return mail


def wait_for_new_mail(mail, folder, check_interval=3, timeout=60):
    """
    :param timeout: 最大等待时间（秒）
    :param mail: 已经登录的IMAP4对象
    :param folder: 要检查的邮件文件夹
    :param check_interval: 检查新邮件的间隔时间（秒）
    :return: None
    """

    global first_new_mail_folder
    # 选择要检查的邮件文件夹
    mail.select(folder)

    # 获取当前的邮件数量
    result, data = mail.search(None, "ALL")
    current_mail_count = len(data[0].split())

    start_time = time.time()
    while not stop_checking.is_set():
        # 如果已经超时，就跳出循环
        if time.time() - start_time > timeout:
            print("Timeout, no new mail arrived.")
            break
        # 等待一段时间
        time.sleep(check_interval)

        # 再次获取邮件数量
        result, data = mail.search(None, "ALL")
        new_mail_count = len(data[0].split())

        # 如果邮件数量增加了，那么有新邮件到来
        if new_mail_count > current_mail_count:
            print(f"{folder} New mail arrived!")
            first_new_mail_folder = folder
            stop_checking.set()
            break


def get_verification_code(mail):
    """
    :param mail:
    :return:
    """
    global first_new_mail_folder
    global stop_checking
    # 创建两个线程，分别检查两个邮件文件夹
    thread1 = threading.Thread(target=wait_for_new_mail, args=(mail, "inbox"))
    thread2 = threading.Thread(target=wait_for_new_mail, args=(mail, "Junk"))
    # 启动线程
    thread1.start()
    thread2.start()

    # 等待线程结束
    while thread1.is_alive() or thread2.is_alive():
        time.sleep(1)

    if first_new_mail_folder is None:
        print("No new mail arrived.")
        return None
    # 选择收件箱
    mail.select(first_new_mail_folder)
    # 搜索标题包含"验证码"的邮件
    result, data = mail.uid('search', None, 'ALL')
    if result == 'OK':
        # 获取最新的一封邮件
        latest_email_uid = data[0].split()[-1]
        result, email_data = mail.uid('fetch', latest_email_uid, '(BODY.PEEK[])')

        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # 假设验证码是一串数字，寻找邮件正文中的数字串
        for part in email_message.walk():
            if part.get_content_type() == "text/html":
                body = part.get_payload(decode=True)
                body_str = body.decode('utf-8')  # 使用utf-8'解码
                pattern = re.compile(r'\b\d{6}\b')
                match = pattern.search(body_str)
                if match:
                    return match.group()
    first_new_mail_folder = None
    stop_checking = threading.Event()
    return None
