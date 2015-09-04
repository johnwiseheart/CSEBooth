from flask import Flask, render_template, jsonify, send_file, request
import time
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import threading
import subprocess
import calendar
import time

gmail_user = "cseopenday@gmail.com"
gmail_pwd = "bradhall"

def mail(to, subject, attach):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject
   msg.preamble = subject

   msg.attach(MIMEImage(open(attach, 'rb').read()))
   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()



app = Flask(__name__)

@app.route('/')
def index():
    return render_template("booth.html")


@app.route('/take_photo')
def take_photo():
    os.system("killall PTPCamera")
    p = subprocess.Popen([
        'gphoto2',
        '--capture-image-and-download',
        '--force-overwrite'
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    print(p.returncode)
    if p.returncode == 0 and os.path.isfile('capt0000.jpg'):

        timestamp = calendar.timegm(time.gmtime())
        os.rename('capt0000.jpg', 'pictures/%s.jpg' % timestamp)

        proc = subprocess.Popen([
            'epeg',
            '--width=10%',
            '--height=10%',
            'pictures/%s.jpg' % timestamp,
            'thumb/%s.jpg' % timestamp
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, _ = proc.communicate()

        return jsonify({
            "success": True,
            "name": "%s.jpg" % timestamp
        })
    else:
        print('uh oh:', output, err)
        if not os.path.isfile('capt0000.jpg'):
            err = ' *** Photo taking failed; perhaps you were out of focus? *** '
        return jsonify({
            "success": False,
            "error": str(err).split('***')[1]
        })

@app.route('/save_photo/<name>', methods=['POST'])
def save_photo(name):
   print(name)
   caption = request.form["caption"]
   email = request.form["email"]
   with Image(filename='pictures/' + name) as img:
         with Image(filename='static/img/cse.png') as logo:
            img.composite(logo, top=img.height-200, left=img.width-200)
            if caption:
               with Drawing() as draw:
                  draw.font = 'font.otf'
                  draw.font_size = 250
                  draw.stroke_color = Color('#000')
                  draw.fill_color = Color('#fff')
                  draw.text_alignment = "center"
                  draw.text(int(img.width/2), int(img.height - 100), caption)
                  draw(img)
            img.save(filename='generated/' + name)
   if email:
      with open("images.csv", "a") as myfile:
         myfile.write("%s,%s\n" % (name, email))
      # thr = threading.Thread(target=mail, args=(email,
      #    "Your photo from CSE @ UNSW Open Day",
      #    "generated/" + name), kwargs={})
      # thr.start() # will run "foo"
   return "Success"

@app.route('/pictures/<name>')
def get_photo(name):
    return send_file('thumb/' + name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
