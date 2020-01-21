#email
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import numpy as np
import cv2
import base64
from datetime import datetime
import paho.mqtt.client as mqtt
import ibm_boto3
from ibm_botocore.client import Config, ClientError

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

bucket_hash = {
  "apikey": "w33MXGnWMRGKzVX71L_d__2EI54kItvXltg4BOU3ghRK",
  "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:a/d9bb57eeeae440448da30b78af11846a:302ad5ed-98fd-4707-8d32-1d0d7113e985::"
}
client = ibm_boto3.client('s3')
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=bucket_hash['apikey'],
    ibm_service_instance_id=bucket_hash['resource_instance_id'],
    ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
    config=Config(signature_version="oauth"),
    endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
)


client=mqtt.Client()

#callback from CONNACK response
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #subscribing in on_connect() to renew subscriptions in the case of a lost connection
    client.subscribe("faces/unknown")
    client.subscribe("faces/us")

img_list=[]

def on_message(client, userdata, msg):
    print("Message receive on " + msg.topic + ": " + str(msg.payload)[:30])

    jpg_as_np = np.frombuffer(base64.b64decode(msg.payload), dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)


    if msg.topic=='faces/unknown':
        img_name = 'unknown-' + datetime.now().strftime("%m_%d_%YT%H_%M_%S") + '.jpg'
        cv2.imwrite(img_name, img)
        #this bit sends it to the object storage
        try:
            resp = cos.meta.client.upload_file(Filename=img_name, Bucket='w251-securibot', Key=img_name)
            print("IBM S3 response: " + str(resp))
        except ClientError as be:
            print("CLIENT ERROR: {0}\n".format(be))
        except Exception as e:
            print("Unable to create text file: {0}".format(e))

        #this bit sends an email every 10 unknown sub detected
        if len(img_list)<10:
            img_list.append(img_name)
        else:
            mymail = Bimail(('Unknown Subject Detection'),['eduarda.espindola@berkeley.edu','bcastaing@berkeley.edu','arthur.lima@berkeley.edu'])
            # start html body
            mymail.htmladd('Unknown subject detection at '+datetime.now().strftime("%I:%M:%S %p"))
            mymail.addattach(img_list)
            mymail.send()
            #resetting the img_list
            img_list=[]

    if msg.topic=='faces/us':
        img_name = 'us-' + datetime.now().strftime("%m_%d_%YT%H_%M_%S") + '.jpg'
    	cv2.imwrite(img_name, img)
        #this bit sends it to the object storage
        try:
            resp = cos.meta.client.upload_file(Filename=img_name, Bucket='w251-securibot', Key=img_name)
            print("IBM S3 response: " + str(resp))
        except ClientError as be:
            print("CLIENT ERROR: {0}\n".format(be))
        except Exception as e:
            print("Unable to create text file: {0}".format(e))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mosquittocloud",1883,60)


#keep it running
client.loop_forever()

