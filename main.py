import os
import argparse
import base64

import hashlib

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from google_images_download import google_images_download  # importing the library

URL_GOOGLE = "https://www.google.com/imghp?sbi=1"

ROOT_DIR = os.path.join(os.getcwd(), "")


def image_to_data_url(filename):
    ext = filename.split('.')[-1]
    prefix = f'data:image/{ext};base64,'
    with open(filename, 'rb') as f:
        img = f.read()
    return prefix + base64.b64encode(img).decode('utf-8')


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
        '-m', '--mode', help='which site to download (google, unsplash, both)', type=str, required=False, choices=['g', 'u', 'b'])
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

    args = parser.parse_args()
    arguments = vars(args)

    if arguments["limit"] <= 0:
        raise ValueError('Limit must greater then 0')
    if not arguments["keyword"] and not arguments["url"]:
        if arguments["inputfolder"]:
            if not os.path.isdir(os.path.join(ROOT_DIR, arguments["inputfolder"])):
                raise ValueError('Input folder {} is not a folder'.format(
                    os.path.join(ROOT_DIR, arguments["inputfolder"])))
            elif not does_file_exist_in_dir(os.path.join(ROOT_DIR, arguments["inputfolder"])):
                raise ValueError('Input folder {} not contain any files'.format(
                    os.path.join(ROOT_DIR, arguments["inputfolder"])))
    if arguments["destfolder"]:
        if not os.path.isdir(os.path.join(ROOT_DIR, arguments["destfolder"])):
            os.mkdir(os.path.join(ROOT_DIR, arguments["destfolder"]))
    if not arguments["removedupe"]:
        arguments["mode"] = 'g'

    # normalize user path
    arguments["inputfolder"] = os.path.join(
        ROOT_DIR, arguments["inputfolder"]) if not arguments["keyword"] and not arguments["url"] else None
    arguments["destfolder"] = os.path.join(ROOT_DIR, arguments["destfolder"])

    return(arguments)


def googleScrape(userinput):

    arguments = {
        "keywords": userinput["keyword"],
        "limit": userinput["limit"],
        "print_urls": userinput["print"],
    }

    if userinput["keyword"]:  # input by keyword

        # let google_images_download do their job by keyword
        ggldownloader = google_images_download.googleimagesdownload()
        paths = ggldownloader.download(arguments)

    elif userinput["url"]:  # input by url

        arguments["url"] = userinput["url"]
        paths = ggldownloader.download(arguments)
        print("\nUrl {} scraping have been done".format(userinput["url"]))

    elif userinput["inputfolder"]:  # input by whole img inside input folder

        timeout = 5  # seconds

        for filename in os.listdir(userinput["inputfolder"]):

            absfilename = os.path.join(userinput["inputfolder"], filename)

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
            ggldownloader = google_images_download.googleimagesdownload()
            arguments["url"] = relimg_url
            paths = ggldownloader.download(arguments)
            print("\nImage {} scraping have been done".format(filename))

            # driver.close()

    else:
        raise ValueError(
            'None of keyword, folder or url input found (use --help for more info)')


def unsplashScrape(userinput):
    pass


def removeDuplicate(userinput):

    downloadfolder = os.path.join(ROOT_DIR, userinput["destfolder"])

    hash_keys = dict()
    # listdir('.') = current directory
    for root, dirs, files in os.walk(downloadfolder, topdown=False):
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


def main():

    userinput = getUserInput()

    if userinput["mode"] is "g" or userinput["mode"] is "b" or userinput["mode"] is "u":
        global driver
        driver = webdriver.Chrome(ROOT_DIR + "chromedriver.exe")

    if userinput["mode"] is "g" or userinput["mode"] is "b":  # google
        googleScrape(userinput)
    if userinput["mode"] is "u" or userinput["mode"] is "b":  # unsplash
        pass
    if userinput["removedupe"]:
        removeDuplicate(userinput)


if __name__ == "__main__":
    main()
