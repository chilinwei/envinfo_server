import smtplib, ConfigParser
from email.mime.text import MIMEText

conf = ConfigParser.ConfigParser()
conf.read('settings.ini')

_user = conf.get('email','user')
_password = conf.get('email','password')
_smtp = conf.get('email','smtp')
_port = conf.get('email','port')
_receiver = conf.get('email','receiver')

def send(msg):
    content = MIMEText(msg)
    content['Subject'] = 'Warning, something is going wrong.'
    content['From'] = _user
    content['To'] = _receiver

    # Send the message via our own SMTP server, but don't include the envelope header.
    s = smtplib.SMTP(_smtp,_port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(_user, _password)
    s.sendmail(_user, [_receiver], content.as_string())
    s.quit()