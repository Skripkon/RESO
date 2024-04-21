import requests
from urllib.parse import urlencode
import os
import re
import shutil
from pyunpack import Archive


def download_datasets(data_path='data/',):
    BASE_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    datasets_composers = [f.path for f in
                          os.scandir(data_path) if f.is_dir()]
    for comp in datasets_composers:
        comp_name = os.path.basename(os.path.normpath(comp)).lower()

        try:
            comp_file = open(os.path.join(comp, comp_name + '.txt'))
        except FileNotFoundError:
            print("Error: could not find required file '" +
                  os.path.join(comp, comp_name + '.txt') +
                  "'. Application will not work as intended.")
            continue

        public_key = comp_file.readline()[:-1]
        info = comp_file.readline()[:-1]
        required_files_num = int(re.search(r'\d+', info).group()) + 2

        print(f"{comp_name.capitalize()}: {required_files_num}",
              "files required.")

        # check if we have all the necessary files already
        # (note: not fail-proof, just checks the number of files)
        if len(os.listdir(comp)) == required_files_num:
            print(f"All {comp_name.capitalize()} files",
                  "already present. Skipping\n" + '-' * 30)
            continue
        else:
            print(f"Only {len(os.listdir(comp))} files found.",
                  "Downloading from cloud initialized.")

        # if we have to download, remove all old files except
        # for the link file
        for filename in os.listdir(comp):
            if filename != comp_name + '.txt' and os.path.isfile(
                                   os.path.join(comp, filename)):
                os.remove(os.path.join(comp, filename))

        print(f"Directory {comp} cleared.")
        print(f"Downloading new files from {public_key}")

        final_url = BASE_URL + urlencode(dict(public_key=public_key))
        response = requests.get(final_url)
        download_url = response.json()['href']

        download_response = requests.get(download_url)
        zip_path = os.path.join(comp, 'downloaded_file.zip')
        with open(zip_path, 'wb') as f:
            f.write(download_response.content)

        print("Archive downloaded, unpacking...")
        Archive(zip_path).extractall(comp)
        unarchived_folder_path = os.path.join(comp, comp_name.upper())
        for filename in os.listdir(unarchived_folder_path):
            shutil.move(os.path.join(unarchived_folder_path, filename), comp)

        print("Clearing temporary files...")
        try:
            shutil.rmtree(unarchived_folder_path)
            os.remove(zip_path)
        except:
            print("Error occured while deleting temporary files.",
                  "Stable application work not guaranteed.")
            pass
        print("Completed.\n" + '-' * 30)


if __name__ == "__main__":
    download_datasets()
