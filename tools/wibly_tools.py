import os
import cv2
import glob
from tqdm import tqdm
import requests
import hashlib
import tools.wibly_logging

LOGGER = tools.wibly_logging.getLogger()

def md5_hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()

def extract_frames(file, folder, name_mask="frame%d.jpg", cmax=0):
    vidcap = cv2.VideoCapture(file)
    success,image = vidcap.read()

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    LOGGER.info("Detected %s fps" % fps)
    count = 0
    i = 0
    while success:
        if count % fps == 0:
            LOGGER.info("Saved frame to : " + str(os.path.join(folder, name_mask % i)))
            cv2.imwrite(os.path.join(folder, name_mask % i), image)     # save frame as JPEG file      
            i += 1
        success,image = vidcap.read()
        
        count += 1

        if cmax > 0 and i >= cmax:
            break

def get_frames(folder, name_mask="frame%d.jpg"):
    return glob.glob(os.path.join(folder,name_mask.replace('%d', "*")))

def get_file_auto(filename, url, verbose=0):
    LOGGER.info("Saving url %s to file %s" % (url, filename))
    with open(filename, 'ab') as f:
        headers = {}
        pos = f.tell()
        if pos:
            headers['Range'] = f'bytes={pos}-'
        response = requests.get(url, headers=headers, stream=True)
        if pos:
            pass
            #validate_as_you_want_(pos, response)
        total_size = int(response.headers.get('content-length'))  
        for data in tqdm(iterable = response.iter_content(chunk_size = 1024), total = total_size//1024, unit = 'KB'):
            f.write(data)