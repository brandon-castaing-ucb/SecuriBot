# -*- coding: utf-8 -*-
"""Sendemail.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lCNdknOoJOetK9lPSLn9mY3XiEObrWGa
"""

from google.colab import drive
drive.mount('/content/drive')

#email
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
#from email import encoders
#from email.message import Message
#from email.mime.audio import MIMEAudio
#from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

class Bimail:
    def __init__(self,subject,recipients):
        self.subject = subject
        self.recipients = recipients
        self.htmlbody = ''
        self.sender = "securibotberkeley@gmail.com"
        self.senderpass = 'securibot@2019'
        self.attachments = []
 
    def send(self):
        msg = MIMEMultipart('alternative')
        msg.set_charset("utf-8")
        msg['From']=self.sender
        msg['Subject']=self.subject
        msg['To'] = ", ".join(self.recipients) # to must be array of the form ['mailsender135@gmail.com']
        msg.preamble = "Unknown subject detected"
        
        #check if there are attachments if yes, add them
        if self.attachments:
            self.attach(msg)
        #add html body after attachments
        msg.attach(MIMEText(self.htmlbody, 'html','utf-8'))
        #send
        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login(self.sender,self.senderpass)
        s.sendmail(self.sender, self.recipients, msg.as_string().encode('utf-8'))
        #test
        #print(msg)
        s.quit()
    
    def htmladd(self, html):
        self.htmlbody = self.htmlbody+'<p></p>'+html
 
    def attach(self,msg):
        for f in self.attachments:
        
            ctype, encoding = mimetypes.guess_type(f)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
                
            maintype, subtype = ctype.split("/", 1)
 
            if maintype == "image":
                fp = open(f, "rb")
                attachment = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "text":
                fp = open(f)
                # Note: we should handle calculating the charset
                attachment = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "audio":
                fp = open(f, "rb")
                attachment = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(f, "rb")
                attachment = MIMEBase(maintype, subtype)
                attachment.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=f)
            attachment.add_header('Content-ID', '<{}>'.format(f))
            msg.attach(attachment)
    
    def addattach(self, files):
        self.attachments = self.attachments + files

import time

from datetime import datetime

# subject and recipients
mymail = Bimail(('Unknown Subject Detection'),['eduarda.espindola@berkeley.edu','bcastaing@berkeley.edu','arthur.lima@berkeley.edu'])
# start html body
mymail.htmladd('Unknown subject detection at '+datetime.now().strftime("%I:%M:%S %p"))
mymail.addattach(['/content/drive/My Drive/prisonmike.png'])
# refer to image in html
mymail.send()

datetime.now().strftime("%I:%M:%S %p")

from tzlocal import get_localzone
local_tz = get_localzone()

