import email
import imaplib
import re
import time


def login(email_user, email_pass):
    # 连接到outlook邮箱服务器
    mail = imaplib.IMAP4_SSL("outlook.office365.com")
    mail.login(email_user, email_pass)
    return mail


def wait_for_new_mail(mail, folder, check_interval=3):
    """
    :param mail: 已经登录的IMAP4对象
    :param folder: 要检查的邮件文件夹
    :param check_interval: 检查新邮件的间隔时间（秒）
    :return: None
    """
    # 选择要检查的邮件文件夹
    mail.select(folder)

    # 获取当前的邮件数量
    result, data = mail.search(None, "ALL")
    current_mail_count = len(data[0].split())

    while True:
        # 等待一段时间
        time.sleep(check_interval)

        # 再次获取邮件数量
        result, data = mail.search(None, "ALL")
        new_mail_count = len(data[0].split())

        # 如果邮件数量增加了，那么有新邮件到来
        if new_mail_count > current_mail_count:
            print("New mail arrived!")
            break


def get_verification_code(mail, folder):
    """
    :param mail:
    :param folder:
    :return:
    """
    wait_for_new_mail(mail, folder)
    # 选择"inbox"（收件箱）
    mail.select(folder)
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
                else:
                    if folder == "Junk":
                        return None
                    else:
                        get_verification_code(mail, folder)

    return None