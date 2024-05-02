from urllib.parse import urlencode
from pyunpack import Archive
import requests
import shutil
import os
import re


def request_to_sownload_files():
    while True:
        download_models_options = input((
            "Would you like to download models?\n"
            "o - only download models for composers that currently have no "
            "models at all\n"
            "s - skip download for composers that have exactly "
            "as many models as intended\n"
            "f - force update of all models\n"
            "n - do not download models\n"))

        match download_models_options.lower():
            case 'o':
                download_models(all_required=False, force=False)
                break
            case 's':
                download_models(all_required=True, force=False)
                break
            case 'f':
                download_models(all_required=True, force=True)
                break
            case 'n':
                break
            case _:
                print("No such option!")

    while True:
        do_download_datasets = input((
            "Would you like to download datasets?\n"
            "s - skip download for composers that have exactly "
            "as many MIDIs as intended\n"
            "f - force update of all datasets\n"
            "n - do not download datasets\n"))

        match do_download_datasets.lower():
            case 's':
                download_datasets(force=False)
                break
            case 'f':
                download_datasets(force=True)
                break
            case 'n':
                break
            case _:
                print("No such option!")
    return


def download_datasets(data_path='data/', force=False):
    print('-' * 30)
    print("DOWNLOADING DATASETS")
    print('-' * 30)
    BASE_URL = \
        'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    datasets_composers = [f.path for f in
                          os.scandir(data_path) if f.is_dir()]
    for comp in datasets_composers:
        comp_name = os.path.basename(os.path.normpath(comp)).lower()

        try:
            comp_file = open(os.path.join(comp, comp_name + '.txt'))
        except FileNotFoundError:
            print("Error: could not find required file",
                  f"'{os.path.join(comp, comp_name + '.txt')}'.",
                  "Application may not work as intended.")
            continue

        public_key = comp_file.readline()[:-1]
        info = comp_file.readline()[:-1]
        required_files_num = int(re.search(r'\d+', info).group()) + 2

        print(f"{comp_name.capitalize()}: {required_files_num}",
              "files required.")

        # check if we have all the necessary files already
        # (note: not fail-proof, just checks the number of files)
        if len(os.listdir(comp)) == required_files_num and not force:
            print(f"All {comp_name.capitalize()} files",
                  "already present. Skipping.\n" + '-' * 30)
            continue
        elif not force:
            print(f"Only {len(os.listdir(comp))} files found.",
                  "Downloading from cloud initialized.")
        else:
            print("Forcing update from cloud.")

        # if we have to download, remove all old files except
        # for the link file
        for filename in os.listdir(comp):
            if filename != comp_name + '.txt' and os.path.isfile(
                                   os.path.join(comp, filename)):
                os.remove(os.path.join(comp, filename))

        print(f"Directory '{comp}' cleared.")
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
        except Exception:
            print("Error occurred while deleting temporary files.",
                  "Stable application work is not guaranteed.")
            pass
        print("Completed.\n" + '-' * 30)


def download_models(models_path='generators/neural/lstm/models',
                    all_required=True,
                    force=False):
    print('-' * 30)
    print("DOWNLOADING MODELS")
    print('-' * 30)
    BASE_URL = \
        'https://cloud-api.yandex.net/v1/disk/public/resources/download?'

    try:
        links_file = open(os.path.join(models_path, 'links.txt'))
    except FileNotFoundError:
        print("Error: could not find required file",
              f"'{os.path.join(os.path.join(models_path, 'links.txt'))}."
              "Application will not work as intended.")
        pass

    while True:
        comp_name = links_file.readline()[:-1]
        if not comp_name:
            break
        info = links_file.readline()[:-1]
        public_key = links_file.readline()[:-1]
        required_models_num = int(re.search(r'\d+', info).group())

        # check whether any models are available
        if required_models_num == 0:
            print(f"{comp_name.capitalize()}: no models",
                  "required.")
            print('-' * 30)
            continue

        print(f"{comp_name.capitalize()}: {required_models_num} models",
              "required.")
        comp_model_path = os.path.join(models_path, comp_name.capitalize())
        os.makedirs(comp_model_path, exist_ok=True)

        model_num = len(os.listdir(comp_model_path))
        if not all_required and not force and model_num > 0 and \
                model_num < required_models_num:
            print(f"Have found {model_num} out of {required_models_num}",
                  f"{comp_name.capitalize()} models. Skipping because",
                  "at least one model was asked.\n" + '-' * 30)
            continue
        elif model_num == required_models_num and not force:
            print(f"All {comp_name.capitalize()} models already present.",
                  "Skipping.\n" + '-' * 30)
            continue

        if not force:
            print(f"Only {model_num} models found.",
                  "Downloading from cloud initialized.")
        else:
            print("Forcing update from cloud.")

        # if we have to download, remove all old files except
        # for the link file
        for filename in os.listdir(comp_model_path):
            if os.path.isfile(os.path.join(comp_model_path, filename)):
                os.remove(os.path.join(comp_model_path, filename))

        print(f"Directory '{comp_model_path}' cleared.")
        print(f"Downloading new files from {public_key}")

        final_url = BASE_URL + urlencode(dict(public_key=public_key))

        try:
            response = requests.get(final_url)
        except Exception:
            print("Error occurred while downloading models.",
                  "Stable application work is not guaranteed.\n" + '-' * 30)
            continue

        download_url = response.json()['href']
        download_response = requests.get(download_url)
        zip_path = os.path.join(comp_model_path, 'downloaded_file.zip')
        with open(zip_path, 'wb') as f:
            f.write(download_response.content)

        print("Archive downloaded, unpacking...")
        Archive(zip_path).extractall(comp_model_path)
        unarchived_folder_path = os.path.join(comp_model_path,
                                              comp_name.upper())
        for filename in os.listdir(unarchived_folder_path):
            shutil.move(os.path.join(unarchived_folder_path, filename),
                        comp_model_path)

        print("Clearing temporary files...")
        try:
            shutil.rmtree(unarchived_folder_path)
            os.remove(zip_path)
        except Exception:
            print("Error occurred while deleting temporary files.",
                  "Stable application work is not guaranteed.")
            pass
        print("Completed.\n" + '-' * 30)


if __name__ == "__main__":
    download_datasets()
    download_models(all_required=True)
