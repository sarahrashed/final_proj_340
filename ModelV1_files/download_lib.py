import os
import urllib.request
import tarfile

# dataset destination
url = "https://data.vision.ee.ethz.ch/cvl/food-101.tar.gz"
filename = "food-101.tar.gz"
extract_dir = "food-101"

# download file
if not os.path.exists(filename):
    urllib.request.urlretrieve(url, filename)

# extract data
if not os.path.exists(extract_dir):
    with tarfile.open(filename, "r:gz") as tar:
        tar.extractall()
else:
    pass


