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
app.config['MAX_CONTENT_LENGTH'] = 2.5 * 1024 * 1024


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
            try:
                print(os.listdir(name + '/uploaded_files/'))
                shutil.rmtree(name + '/uploaded_files/')
                print(os.listdir(name + '/uploaded_files/'))
            except:
                print(os.listdir(name + '/uploaded_files/'))

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

                im_gray2 = cv2.cvtColor(th1, cv2.COLOR_RGB2GRAY) #(B)
                im_blur2 = cv2.GaussianBlur(im_gray2, (11, 11), 0) #(C)

                th = cv2.threshold(im_blur2, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]

                contours, _ = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                def getRectByPoints(points):
                    # prepare simple array
                    points = list(map(lambda x: x[0], points))

                    points = sorted(points, key=lambda x:x[1])
                    top_points = sorted(points[:2], key=lambda x:x[0])
                    bottom_points = sorted(points[2:4], key=lambda x:x[0])
                    points = top_points + bottom_points

                    left = min(points[0][0], points[2][0])
                    right = max(points[1][0], points[3][0])
                    top = min(points[0][1], points[1][1])
                    bottom = max(points[2][1], points[3][1])
                    return (top, bottom, left, right)

                def getPartImageByRect(rect):
                    img = imread(image_dir + image_file, 1)
                    #print(rect[0], rect[2], rect[1], rect[3])
                    return img[rect[0]:rect[2], rect[1]:rect[3]]

                os.mkdir(image_dir+image_file.split('.')[0]+'/')

                th_area = img.shape[0] * img.shape[1] / 1000
                contours_large = list(filter(lambda c:cv2.contourArea(c) > th_area, contours))

                outputs = []
                rects = []
                approxes = []
                c = 0

                for (i,cnt) in enumerate(contours_large):
                    arclen = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.02*arclen, True)
                    if len(approx) < 4:
                        continue
                    approxes.append(approx)
                    rect = getRectByPoints(approx)
                    rects.append(rect)
                    #print(c,rects)
                    outputs.append(getPartImageByRect(rects[c]))
                    c += 1


                for n in range(len(rects)):
                    x1 = rects[n][0]
                    x2 = rects[n][0]+(rects[n][3]-rects[n][2])
                    y1 = rects[n][2]
                    y2 = rects[n][3]
                    abs_x = int((x2-x1)*0.4)
                    abs_y = int((y2-y1)*0.4)
                    X1 = x1-int(abs_x*0.7)
                    Y1 = x2+int(abs_x*0.7)
                    X2 = y1-int(abs_y*0.7)
                    Y2 = y2+int(abs_y*0.7)
                    imwrite(image_dir+image_file.split('.')[0]+'/'+str(n)+'.jpg', img[X1:Y1,X2:Y2])

                return image_dir+image_file.split('.')[0]



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
