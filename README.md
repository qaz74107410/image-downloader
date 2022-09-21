# image-downloader

A program that download image from google.com and unsplash.com

## Example of arguments

download images to "./download" from google by using images inside "./input"

```bash
python imgdownloader.py --mode google --inputfolder input --destfolder download
python imgdownloader.py --m g --if input --df dow#nload
```

download images to "./download" from google by using images inside "./input" but limit only 10 images

```bash
python imgdownloader.py --mode google --inputfolder input --destfolder download --limit 10
python imgdownloader.py --m g --if input --df download -l 10
```

download images to "./download" from google by using images inside "./input" and remove duplicate files after download

```bash
python imgdownloader.py --mode google --inputfolder input --destfolder download --removedupe
python imgdownloader.py --m g --if input --df download -rd
```

download images to "./download" from google by using keyword "cat" and remove duplicate files after 

```bash
python imgdownloader.py --mode google --keyword "cat" --destfolder download --removedupe
python imgdownloader.py --m g -k "cat" --df download -rd
```

download images to "./download" from unsplash by using keyword "cat" and remove duplicate files after download

```bash
python imgdownloader.py --mode unsplash --keyword "cat" --destfolder download
python imgdownloader.py --m u -k "cat" --df download
```

remove duplicate files inside "./download"

```bash
python imgdownloader.py --destfolder download --removedupe
python imgdownloader.py --df download -rd
```

count files inside "./download"

```bash
python imgdownloader.py --destfolder download --count
python imgdownloader.py --df download -c
```
