image-downloader

Example of arguments

  python imgdownloader.py --mode google --inputfolder input --destfolder download
  python imgdownloader.py --m g --if input --df download
        : download images to "./download" from google by using images inside "./input"

  python imgdownloader.py --mode google --inputfolder input --destfolder download --limit 10
  python imgdownloader.py --m g --if input --df download -l 10
        : download images to "./download" from google by using images inside "./input" but limit only 10 images

  python imgdownloader.py --mode google --inputfolder input --destfolder download --removedupe
  python imgdownloader.py --m g --if input --df download -rd
        : download images to "./download" from google by using images inside "./input" and remove duplicate files after download
  python imgdownloader.py --mode google --keyword "cat" --destfolder download --removedupe
  python imgdownloader.py --m g -k "cat" --df download -rd
        : download images to "./download" from google by using keyword "cat" and remove duplicate files after download

  python imgdownloader.py --mode unsplash --keyword "cat" --destfolder download
  python imgdownloader.py --m u -k "cat" --df download
        : download images to "./download" from unsplash by using keyword "cat" and remove duplicate files after download        

  python imgdownloader.py --destfolder download --removedupe
  python imgdownloader.py --df download -rd
        : remove duplicate files inside "./download"

  python imgdownloader.py --destfolder download --count
  python imgdownloader.py --df download -c
        : count files inside "./download"
