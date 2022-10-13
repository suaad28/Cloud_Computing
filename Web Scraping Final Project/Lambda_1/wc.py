import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from app.aws import s3_client
import os


#text = "square square mask mask"
#text = ["abc", "ded", "ded", "dasda", "abc", "dasda", "dasda", "dasda"]

#input: list of strings
def generate_wc(l_str, shape = "sphere"):
    text = " ".join(l_str)
    mask = None
    if shape == "sphere":
        x, y = np.ogrid[:300, :300]
        mask = mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
        mask = 255 * mask.astype(int)

    wc = WordCloud(background_color="white", repeat=True, mask=mask)
    wc.generate(text)
    return wc

def generate_bar(list_str):
    # dict_str = {x:list_str.count(x) for x in list_str}
    # print("Dict is ", dict_str)
    bins = []
    nums = []
    for key, value in list_str.items():
        bins.append(key)
        nums.append(value)
    plt.bar(bins, nums, 0.7)
    plt.ylabel('Frequency')
    plt.xlabel('Job Title')
    plt.savefig("/tmp/" + "_bar.png")

#input: list of strings
def generate_hist(l_str):
    print(l_str)
    dict_str = Counter(l_str)
    print(dict_str)
    plt.hist(dict_str, ec="red", fc="blue", density=True, bins='auto') 
    plt.ylabel('Frequency')
    plt.xlabel('Job Title')
    plt.savefig('/tmp/hist.png')
    plt.show()

def show_wc(wc):
    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    plt.show()

def delete_path(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print("The file does not exist")

def upload_to_bucket(wc, fname = "test.png"):
    s3 = s3_client()
    wc.to_file("/tmp/" + fname)
    s3.client.upload_file("/tmp/" + fname, s3.bucketName, fname)
    #delete local file after save to s3
    delete_path("/tmp/" + fname)


def download_from_bucket(fname):
    s3 = s3_client()
    s3.client.download_file(s3.bucketName, fname, "/tmp/d_" + fname)
    #delete local file after save to s3
    #delete_path("/tmp/d_" + fname)

#wc = generate_wc(text)
#show_wc(wc)
#generate_hist(text)