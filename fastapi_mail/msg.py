import asyncio
import time

from datetime import date

from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from email.utils import formatdate, make_msgid

from fastapi_mail.version import PY3
from email.encoders import encode_base64


class MailMsg:
    """
    Preaparation of class for email text
    
    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)
        self.msgId = make_msgid()


    def _mimetext(self, text, subtype="plain"):
        """Creates a MIMEText object"""

        return MIMEText(text, _subtype=self.subtype, _charset=self.charset)


    async def attach_file(self, message, attachment):

        print(attachment)
        
        for file in attachment:
        
            part = MIMEBase(_maintype="application", _subtype="octet-stream")

            
            part.set_payload(await file.read())
            encode_base64(part)

            filename = file.filename

            try:
                filename and filename.encode('ascii')
            except UnicodeEncodeError:
                if not PY3:
                    filename = filename.encode('utf8')

            filename = ('UTF8', '', filename)
            

            part.add_header(
                'Content-Disposition',
                "attachment",
                filename=filename)
            

            self.message.attach(part)


    
    async def _message(self,sender):
        """Creates the email message"""
            
        self.message = MIMEMultipart()
        self.message.set_charset(self.charset)
        self.message['Date'] = formatdate(time.time(), localtime=True)
        self.message['Message-ID'] = self.msgId
        self.message["To"] =  ', '.join(self.receipients)
        self.message["From"] = sender


        if self.subject:
            self.message["Subject"] = (self.subject)
           
        if self.cc:
            self.message["Cc"] = ', '.join(self.cc)
        
        if self.bcc:
            self.message["Bcc"] = ', '.join(self.bcc)

        if self.body:
            self.message.attach(self._mimetext(self.body))

        if self.attachments:
            await self.attach_file(self.message, self.attachments)


        return self.message

    
    async def as_string(self):
        return await self._message().as_string()
        
    def as_bytes(self):
        return self._message().as_bytes()

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()

