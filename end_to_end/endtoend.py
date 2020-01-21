# USAGE
# python3 recognize_faces_video2.py --encodings encodings.pickle
# python3 recognize_faces_video.py --encodings encodings.pickle --output output/jurassic_park_trailer_output.avi --display 0

# import the necessary packages
from imutils.video import VideoStream
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
from datetime import datetime
import numpy as np
import base64
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
try:
    resp = cos.meta.client.upload_file(Filename=IMG_FILE, Bucket='w251-securibot', Key=IMAGE_FILE_PATH)
    print("IBM S3 response: " + str(resp))
except ClientError as be:
    print("CLIENT ERROR: {0}\n".format(be))
except Exception as e:
    print("Unable to create text file: {0}".format(e))

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
ap.add_argument("-o", "--output", type=str,
	help="path to output video")
ap.add_argument("-y", "--display", type=int, default=0,
	help="whether or not to display output frame to screen")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=1).start()
writer = None
time.sleep(2.0)

img_list=[]

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
	frame = vs.read()
	
	# convert the input frame from BGR to RGB then resize it to have
	# a width of 750px (to speedup processing)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	rgb = imutils.resize(frame, width=750)
	r = frame.shape[1] / float(rgb.shape[1])

	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input frame, then compute
	# the facial embeddings for each face
	boxes = face_recognition.face_locations(rgb,
		model=args["detection_method"])
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	guery = 2

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding, tolerance=0.5)
		name = "Unknown"

		guery = 0

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)

		# update the list of names
		names.append(name)
		#check if it is Unknown if yes, 
		if name == 'Unknown':
			guery = 1

	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# rescale the face coordinates
		top = int(top * r)
		right = int(right * r)
		bottom = int(bottom * r)
		left = int(left * r)

		# draw the predicted face name on the image
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			0.75, (0, 255, 0), 2)


	# if the video writer is None *AND* we are supposed to write
	# the output video to disk initialize the writer
	if writer is None and args["output"] is not None:
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		writer = cv2.VideoWriter(args["output"], fourcc, 20,
			(frame.shape[1], frame.shape[0]), True)

	# if the writer is not None, write the frame with recognized
	# faces t odisk
	if writer is not None:
		writer.write(frame)


	if guery == 1:
            print("Found an unknown person!")
            img_name = 'unknown-' + datetime.now().strftime("%m_%d_%YT%H_%M_%S") + '.jpg'
            cv2.imwrite(img_name, frame)
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

	if guery == 0:
            print("Found an image of us!")
            img_name = 'us-' + datetime.now().strftime("%m_%d_%YT%H_%M_%S") + '.jpg'
            cv2.imwrite(img_name, frame)
            #this bit sends it to the object storage
            try:
                resp = cos.meta.client.upload_file(Filename=img_name, Bucket='w251-securibot', Key=img_name)
                print("IBM S3 response: " + str(resp))
            except ClientError as be:
                print("CLIENT ERROR: {0}\n".format(be))
            except Exception as e:
                print("Unable to create text file: {0}".format(e))

        # NOTE: This code breaks in Docker since we don't have a frame buffer to open
	# check to see if we are supposed to display the output frame to
	# the screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(10) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break


# check to see if the video writer point needs to be released
if writer is not None:
	writer.release()
