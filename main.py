import os
import argparse
import base64
import time
import requests

import hashlib

from datetime import datetime
from PIL import Image
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from google_images_download import google_images_download

URL_GOOGLE = "https://www.google.com/imghp?sbi=1"
URL_UNSPLASH = "https://unsplash.com"

ROOT_DIR = os.path.join(os.getcwd(), "")


def image_to_data_url(filename):
    ext = filename.split('.')[-1]
    prefix = f'data:image/{ext};base64,'
    with open(filename, 'rb') as f:
        img = f.read()
    return prefix + base64.b64encode(img).decode('utf-8')


def generate_datetimestr():
    return datetime.now().strftime("%Y-%m-%d %H_%M_%S")


def getUserInput():

    def does_file_exist_in_dir(path):
        return len(os.listdir(path)) > 0

    parser = argparse.ArgumentParser(
        prog='imgdownloader',
        # usage='%(prog)s [options]',
        description='Image downloader for googleimage and unsplash website.')
    parser.add_argument(
        '-p', '--print', help='print the URLs of the images', required=False, action='store_true')
    parser.add_argument(
        '-rd', '--removedupe', help='remove duplicate images', required=False, action='store_true')
    parser.add_argument(
        '-m', '--mode', help='which site to download from google:g or unsplash:u (default=g)', required=False, choices=['g', 'u', 'google', 'unsplash'])
    parser.add_argument(
        '-k', '--keyword', help='delimited list input', type=str, required=False)
    parser.add_argument(
        '-l', '--limit', help='limit the download count', type=int, required=False, default=10)
    parser.add_argument(
        '-if', '--inputfolder', help='delimited input folder', type=str, required=False, default="inputs")
    parser.add_argument(
        '-df', '--destfolder', help='delimited destination folder', type=str, required=False, default="downloads")
    parser.add_argument(
        '-u', '--url', help='search with google image URL', type=str, required=False)
    parser.add_argument(
        '-nc', '--no-autoclose', help='stop close driver on program exit', required=False, action='store_true', default=False)
    parser.add_argument(
        '-c', '--count', help='count images in desination folder', required=False, action='store_true', default=False)
    parser.add_argument(
        '-cd', '--chromedriver', help='specify the path to chromedriver executable in your local machine', type=str, required=False, default=ROOT_DIR + "chromedriver.exe")
    parser.add_argument(
        '-i', '--image_directory', help='download images in a specific sub-directory', type=str, required=False)

    args = parser.parse_args()
    arguments = vars(args)

    if arguments["limit"] <= 0:
        raise ValueError('Limit must greater then 0')
    if not arguments["keyword"] and not arguments["url"]:
        if not os.path.isdir(os.path.join(ROOT_DIR, arguments["inputfolder"])):
            raise ValueError('Input folder {} is not a folder'.format(
                os.path.join(ROOT_DIR, arguments["inputfolder"])))
        elif not does_file_exist_in_dir(os.path.join(ROOT_DIR, arguments["inputfolder"])):
            raise ValueError('Input folder {} not contain any files'.format(
                os.path.join(ROOT_DIR, arguments["inputfolder"])))
    if not os.path.isdir(os.path.join(ROOT_DIR, arguments["destfolder"])):
        os.mkdir(os.path.join(ROOT_DIR, arguments["destfolder"]))
    if not arguments["removedupe"] and not arguments["mode"]:
        arguments["mode"] = 'g'
    if arguments["mode"] == 'google':
        arguments["mode"] = 'g'
    elif arguments["mode"] == 'unsplash':
        arguments["mode"] = 'unsplash'

    # normalize user path
    arguments["inputfolder"] = os.path.join(
        ROOT_DIR, arguments["inputfolder"]) if not arguments["keyword"] and not arguments["url"] else None
    arguments["destfolder"] = os.path.join(ROOT_DIR, arguments["destfolder"])

    return(arguments)


def googleScrape(userinput):

    ggldownloader = google_images_download.googleimagesdownload()
    timeout = 5  # seconds
    arguments = {
        "limit": userinput["limit"],
        "print_urls": userinput["print"],
        "chromedriver": userinput["chromedriver"],
        "output_directory": userinput["destfolder"],  # default downloads
        # "image_directory": userinput["destfolder"], # default images name
    }

    def scapeByKeyword(keyword):
        arguments["keywords"] = keyword  # array is acceptable
        # let google_images_download do their job by keyword
        ggldownloader.download(arguments)

    def scapeByUrl(url):
        arguments["url"] = url
        ggldownloader.download(arguments)

    def scapeByFilename(filename):
        absfilename = os.path.join(userinput["inputfolder"], filename)

        # default define as filename if exist
        with open(absfilename, 'rb') as f:
            if not userinput.get("image_directory"):
                arguments["image_directory"] = os.path.splitext(
                    os.path.basename(f.name))[0]
        print(arguments)

        # 1 img to dataurl
        img_dataurl = image_to_data_url(absfilename)

        # 2 locate to img search
        driver.get(URL_GOOGLE)

        try:
            element_present = EC.presence_of_element_located(
                (By.NAME, 'image_url'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Loading took too much time!")

        # 3 paste dataurl into searchbox
        driver.execute_script(
            "document.getElementsByName('image_url')[0].setAttribute('value', '{}');".format(img_dataurl))

        # 4 search
        driver.find_element_by_name('image_url').send_keys(Keys.RETURN)

        # 5 get relative img url
        a_list = driver.find_elements_by_tag_name('a')
        relimg_url = None
        for a in a_list:
            href = a.get_attribute("href")
            if href and "tbm=isch&sa" in href:
                relimg_url = href
                break

        # 6 let google_images_download do their job by img url
        scapeByUrl(relimg_url)

    if userinput["keyword"]:  # input by keyword
        scapeByKeyword(userinput["keyword"])
        print("\nKeyword {} scraping have been done".format(
            userinput["keyword"]))

    elif userinput["url"]:  # input by url
        scapeByUrl(userinput["url"])
        print("\nUrl {} scraping have been done".format(userinput["url"]))

    elif userinput["inputfolder"]:  # input by whole img inside input folder
        for filename in os.listdir(userinput["inputfolder"]):
            scapeByFilename(filename)
            print("\nImage {} scraping have been done".format(filename))

    else:
        raise ValueError(
            'None of keyword, folder or url input found (use --help for more info)')


def unsplashScrape(userinput):

    timeout = 5  # seconds

    def scapeByKeyword(keyword):
        url = "https://unsplash.com/s/photos/" + keyword
        scapeByUrl(url)

    def scapeByFilename(fileame):

        # due the noway to search by images. we have to know what is it by
        # searching it in google. and get image's name

        # 1 img to dataurl
        absfilename = os.path.join(userinput["inputfolder"], filename)
        img_dataurl = image_to_data_url(absfilename)

        # 2 locate to img search
        driver.get(URL_GOOGLE)

        try:
            element_present = EC.presence_of_element_located(
                (By.NAME, 'image_url'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Loading took too much time!")

        # 3 paste dataurl into searchbox
        driver.execute_script(
            "document.getElementsByName('image_url')[0].setAttribute('value', '{}');".format(img_dataurl))

        # 4 search
        driver.find_element_by_name('image_url').send_keys(Keys.RETURN)

        # 5 get image property name
        # keyword = driver.find_element_by_xpath(
        #     '//input[@aria-label="Search"]').get_attribute("value")
        keyword = driver.find_element_by_name("q").get_attribute("value")

        # 6 let scrape by keyword
        scapeByKeyword(keyword)

    def scapeByUrl(url):
        result_folder = os.path.join(
            ROOT_DIR, userinput["destfolder"], generate_datetimestr())
        scroll = 1000
        driver.get(url)

        paths = []

        # 1 keep scrolling until figure load
        while True:
            time.sleep(timeout)
            driver.execute_script("window.scrollBy(0,"+str(scroll)+");")

            # 2 get all img (src contain images.unsplash.com/photo in img tag AND not saved)
            driver.find_elements_by_tag_name("img")
            img_elems = driver.find_elements_by_css_selector(
                "img[src *= 'images.unsplash.com/photo']:not([saved *= 'true'])")

            print(img_elems)

            if len(img_elems) <= 0:
                break

            # 3 scrape all visible img
            i = 0
            for img_elem in img_elems:

                # 4 check if we already saved
                if img_elem.get_attribute("saved"):
                    break
                img_url = img_elem.get_attribute("src").split("?")[0]
                img_object = requests.get(img_url)

                if not os.path.exists(result_folder):
                    os.makedirs(result_folder)

                img_name = img_elem.get_attribute("alt").replace(" ", "_")
                img = Image.open(BytesIO(img_object.content))

                # 5 save img
                i = i + 1
                img.save("{}/{}_{}.{}".format(result_folder,
                                              i, img_name, img.format), img.format)

                # TODO : 6 mark img_elem attr as saved
                driver.execute_script(
                    "arguments[0].setAttribute('saved','true')", img_elem)

    if userinput["keyword"]:  # input by keyword
        scapeByKeyword(userinput["keyword"])
        print("\nKeyword {} scraping have been done".format(
            userinput["keyword"]))

    elif userinput["url"]:  # input by url
        scapeByUrl(userinput["url"])
        print("\nUrl {} scraping have been done".format(userinput["url"]))

    elif userinput["inputfolder"]:  # input by whole img inside input folder
        for filename in os.listdir(userinput["inputfolder"]):
            scapeByFilename(filename)
            print("\nImage {} scraping have been done".format(filename))

    else:
        raise ValueError(
            'None of keyword, folder or url input found (use --help for more info)')


def removeDuplicate(userinput):

    downloadfolder = os.path.join(ROOT_DIR, userinput["destfolder"])
    dupefound = 0

    hash_keys = dict()
    for root, _, files in os.walk(downloadfolder, topdown=False):
        for name in files:
            relfile = os.path.relpath(os.path.join(root, name), ROOT_DIR)
            with open(relfile, 'rb') as f:
                filehash = hashlib.sha1(f.read()).hexdigest()
            if filehash not in hash_keys:
                hash_keys[filehash] = relfile
            else:
                print("Duplicate found : \n\t{}\n\t{}".format(
                    hash_keys[filehash], relfile))
                os.remove(relfile)
                dupefound = dupefound + 1
    return dupefound


def countFiles(path):
    return sum([len(files) for r, d, files in os.walk(path)])


def main():

    userinput = getUserInput()

    # count files in directory and sub-directory
    if userinput["count"]:
        lenfile = countFiles(userinput["destfolder"])
        print("Files total in '{}' : \n\t{}".format(
            userinput["destfolder"], lenfile))
        return True

    # define driver (browser)
    if userinput["mode"] == "g" or userinput["mode"] == "u":  # both
        global driver
        try:
            driver = webdriver.Chrome(
                os.path.join(ROOT_DIR, "chromedriver.exe"))

            # scrape things from ..
            if userinput["mode"] == "g":  # google
                googleScrape(userinput)
            if userinput["mode"] == "u":  # unsplash
                unsplashScrape(userinput)
            return True

        finally:
            if not userinput["no_autoclose"]:
                driver.close()

    if userinput["removedupe"]:  # remove duplication files
        dupefound = removeDuplicate(userinput)
        if not dupefound:
            print("No Duplication files found in {}.".format(
                userinput["destfolder"]))
        return True


if __name__ == "__main__":
    main()
