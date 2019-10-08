from flask import Flask, request, make_response, jsonify, render_template
from flask import send_file, make_response, send_from_directory
import os
import sys
import cv2
import numpy as np
import werkzeug
from datetime import datetime
import datetime
from PIL import Image
import shutil

# flask
app = Flask(__name__)

# limit upload file size : 1MB
#app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024


# ------------------------------------------------------------------
#@app.route('/', methods=['POST', "GET"])
@app.route('/')
def upload():
    return render_template('index.html')

#@app.route('/data/upload', methods=['POST'])
@app.route('/upload', methods=['POST', 'GET'])
def upload_multipart():
    try:
        if request.method == 'POST':
            time = str(datetime.datetime.now()).split('.')[0].replace(':', '-')
            name = os.path.dirname(os.path.abspath(__name__))
            joined_path = os.path.join(name, './uploaded_files/'+time+'/')

            try:
                if len(os.listdir(name + '/uploaded_files/')) != 0:
                    print(os.listdir(name + '/uploaded_files/'))
                    shutil.rmtree(name + '/uploaded_files/')
                    os.mkdir(name + '/uploaded_files/')
            except:
                print(os.listdir(name + '/uploaded_files/'))

            os.mkdir(name + '/uploaded_files/'+time)

            uploadFile_list = ['uploadFile_aa','uploadFile_aa2','uploadFile_aa3','uploadFile_aa4','uploadFile_aa5','uploadFile_aa6','uploadFile_aa7','uploadFile_aa8']
            for uploadFile_aa in uploadFile_list:
                try:
                    if uploadFile_aa not in request.files:
                        make_response(jsonify({'result':'uploadFile is required.'}))
                    images = request.files.getlist(uploadFile_aa)
                    for i,image in enumerate(images):#image will be the key
                        file_name = image.filename
                        image.save(joined_path + file_name)
                except:
                    continue

            joined_path = os.path.join(name, './uploaded_files/'+time+'/')
            files = [f for f in os.listdir(joined_path)]
            if len(files)==0:
                os.rmdir(name + '/uploaded_files/'+time)
                return render_template('nofile.html')
            FILES = [joined_path + i for i in files]
            FILES.sort(key=os.path.getmtime)
            files_sorted = []
            for i in FILES:
                l = i.split('/')
                files_sorted.append(l[-1])
            count = 0
            for file in files:
                for ext in [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG", ".gif", ".GIF", ".bmp", ".BMP"]:
                    if ext in file:
                        count += 1
            if count != len(FILES):
                for file in FILES:
                    os.remove(file)
                os.rmdir(name + '/uploaded_files/'+time)
                return render_template('nofile.html')


            def coin_detector(p,f):
                def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
                    try:
                        n = np.fromfile(filename, dtype)
                        img = cv2.imdecode(n, flags)
                        return img
                    except Exception as e:
                        print(e)
                        return None

                def imwrite(filename, img, params=None):
                    try:
                        ext = os.path.splitext(filename)[1]
                        result, n = cv2.imencode(ext, img, params)

                        if result:
                            with open(filename, mode='w+b') as f:
                                n.tofile(f)
                            return True
                        else:
                            return False
                    except Exception as e:
                        print(e)
                        return False


                image_dir = p
                image_file = f
                img = imread(image_dir+image_file)

                ret,th1 = cv2.threshold(img,180,255,cv2.THRESH_BINARY)

                im_gray2 = cv2.cvtColor(th1, cv2.COLOR_RGB2GRAY)
                im_blur2 = cv2.GaussianBlur(im_gray2, (11, 11), 0)

                th = cv2.threshold(im_blur2, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]

                coins_contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                coins_and_contours = np.copy(img)

                min_coin_area = 60
                large_contours = [cnt for cnt in coins_contours if cv2.contourArea(cnt) > min_coin_area]

                os.mkdir(image_dir+image_file.split('.')[0]+'/')

                # for each contour find bounding box and draw rectangle
                bounding_img = np.copy(img)
                n = 0
                for i,contour in enumerate(large_contours):
                    x, y, w, h = cv2.boundingRect(contour)
                    if w < 30 or h < 30:
                        continue
                    if abs(w-h) > 400:
                        continue
                    if h > w*2:
                        continue
                    if w > h*2:
                        continue
                    imwrite(image_dir+image_file.split('.')[0]+'/'+str(n+1)+'.jpg', img[y-int(h*0.1):y+ int(h*1.1),x-int(w*0.1):x+int(w*1.1)])
                    n += 1
                print(image_dir+image_file.split('.')[0])
                return image_dir+image_file.split('.')[0]

            print(os.listdir(name + '/uploaded_files/'))

            trimed_folder = []
            for file in files:
                trimed_folder.append(coin_detector(joined_path, file))

            shutil.make_archive('./uploaded_files/'+time, 'zip', root_dir='./uploaded_files/'+time)
            shutil.rmtree(name + '/uploaded_files/'+time)
            # return render_template('complete.html')
            return send_file('./uploaded_files/'+time+'.zip')

    except:
        return render_template('nofile.html')

# ------------------------------------------------------------------
@app.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_over_max_file_size(error):
    print("werkzeug.exceptions.RequestEntityTooLarge")
    return 'result : file size is overed.'
    #return render_template('toolarge.html')

# ------------------------------------------------------------------
# main
if __name__ == "__main__":
    print(app.url_map)
    #app.run(host='localhost', port=3000)
    app.run()
#
# ------------------------------------------------------------------
