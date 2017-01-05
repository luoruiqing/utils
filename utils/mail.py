# coding:utf-8
from os import path
from smtplib import SMTP
from email.header import Header
from traceback import format_exc
from logging import getLogger, DEBUG
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = getLogger()
logger.setLevel(DEBUG)


def send_mail(to, subject, msg, smtpserver, username, password, _subtype='plain'):
    msg = MIMEText(msg, _subtype=_subtype, _charset='utf-8')
    msg['Subject'], msg['From'], msg['To'] = subject, username, ";".join(to)
    try:
        smtp = SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(username, to, msg.as_string())
        smtp.close()
        logger.info("Send mail end.")
    except Exception, e:
        print str(e)
        logger.warning("Send mail Fail.")


def send_mail_files(to, subject, content, smtp_server,
                    username, password, sender=None, _subtype="plain",
                    file_paths=None, send_filename=None,
                    port=0, charset="utf-8", debug=True, retry=3):
    """可以携带附件的发送邮件模块"""
    sender = sender or username
    to_list = lambda attr: attr if isinstance(attr, (list, tuple)) else [attr]

    mail = MIMEMultipart()

    mail['To'] = Header(";".join(to_list(to)), charset)
    mail['From'] = Header(sender, charset)
    mail['Subject'] = Header(subject, charset)
    mail.attach(MIMEText(content, _subtype=_subtype, _charset=charset))
    if not file_paths is None:
        file_paths = to_list(file_paths)
        send_filename = send_filename if len(file_paths) == 1 else None

        for file_path in file_paths:
            if not path.exists(file_path):
                raise OSError("Does not exist of file_path \"%s\"" % file_path)
            file = MIMEText(open(file_path, 'rb').read(), 'base64', charset)
            file["Content-Type"] = 'application/octet-stream'
            file["Content-Disposition"] = 'attachment; filename="%s"' % (
                send_filename or path.basename(file_path))
            mail.attach(file)
    for _ in range(retry):
        try:
            client = SMTP()
            client.connect(host=smtp_server, port=port)
            client.login(username, password)
            client.sendmail(from_addr=sender,
                            to_addrs=to_list(to),
                            msg=mail.as_string())
            client.close()
            return True
        except:
            logger.error(format_exc())

    return False
