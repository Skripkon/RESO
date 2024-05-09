import os
import re
import shutil
from urllib.parse import urlencode

from pyunpack import Archive
import requests


def request_to_sownload_files():
    while True:
        agree = input((
            "Dow you want do download missing files? [Y/n] "
        ))
        match agree.lower():
            case 'y':
                break
            case 'n':
                return
            case _:
                print('No such option!')

    while True:
        download_models_options = input((
            "Would you like to download models? (necessary)\n"
            "o - only download models for composers that currently have no "
            "models at all\n"
            "s - skip download for composers that have exactly "
            "as many models as required\n"
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
        do_download_notes = input((
            "Would you like to download notes files? (necessary)\n"
            "s - skip download for composers that already have "
            "the notes file\n"
            "f - force update of all notes files\n"
            "n - do not download notes files\n"))

        match do_download_notes.lower():
            case 's':
                download_notes(force=False)
                break
            case 'f':
                download_notes(force=True)
                break
            case 'n':
                break
            case _:
                print("No such option!")

    while True:
        do_download_datasets = input((
            "Would you like to download datasets? (not necessary)\n"
            "s - skip download for composers that have exactly "
            "as many MIDIs as required\n"
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

        model_num = files_cnt(comp_model_path, ['.keras'])
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
            print("Error occurred while downloading models. Aborting.",
                  "Stable application work is not guaranteed.\n" + '-' * 30)
            continue

        try:
            download_url = response.json()['href']
        except KeyError:
            print("Error occurred while downloading models. Aborting.",
                  "Stable application work is not guaranteed.\n" + '-' * 30)
            continue

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


def download_notes(data_path='data/', force=False):
    print('-' * 30)
    print("DOWNLOADING NOTES")
    print('-' * 30)
    BASE_URL = \
        'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    composers = [f.path for f in os.scandir(data_path) if f.is_dir()]

    for comp in composers:
        comp_name = os.path.basename(os.path.normpath(comp)).lower()
        try:
            comp_file = open(os.path.join(comp, comp_name + '.txt'))
        except FileNotFoundError:
            print("Error: could not find required file",
                  f"'{os.path.join(comp, comp_name + '.txt')}'.",
                  "Application may not work as intended." + '-' * 30)
            continue

        if os.path.exists(os.path.join(comp, 'notes')) and not force:
            print(f"Notes file for {comp_name.capitalize()} already present.",
                  "Skipping.\n" + '-' * 30)
            continue
        elif not force:
            print(f"No notes file for {comp_name.capitalize()} found.")
            print("Downloading from cloud initialized.")
        else:
            print("Forcing update from cloud.")
            try:
                os.remove(os.path.join(comp, 'notes'))
            except FileNotFoundError:
                pass

        comp_file.readline()
        comp_file.readline()
        public_key = comp_file.readline()
        print(f"Downloading new files from {public_key}")

        final_url = BASE_URL + urlencode(dict(public_key=public_key))

        try:
            response = requests.get(final_url)
        except Exception:
            print("Error occurred while downloading notes. Aborting.",
                  "Stable application work is not guaranteed.\n" + '-' * 30)
            continue

        try:
            download_url = response.json()['href']
        except KeyError:
            print("Error occurred while downloading notes. Aborting.",
                  "Stable application work is not guaranteed.\n" + '-' * 30)
            continue

        download_response = requests.get(download_url)
        zip_path = os.path.join(comp, 'downloaded_file.zip')
        with open(zip_path, 'wb') as f:
            f.write(download_response.content)

        print("Archive downloaded, unpacking...")
        Archive(zip_path).extractall(comp)
        unarchived_folder_path = os.path.join(comp,
                                              comp_name.upper() + '_NOTES')
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


def files_cnt(path: str, extensions: list):
    return len([file for file in os.listdir(path) if
                os.path.splitext(file)[1] in extensions])


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
        required_files_num = int(re.search(r'\d+', info).group())

        print(f"{comp_name.capitalize()}: {required_files_num}",
              "midis required.")

        # check if we have all the necessary files already
        # (note: not fail-proof, just checks the number of files)
        found_midis_num = files_cnt(comp, ['.mid', '.midi'])
        if found_midis_num == required_files_num and \
           not force:
            print(f"All {comp_name.capitalize()} midis",
                  "already present. Skipping.\n" + '-' * 30)
            continue
        elif not force:
            print(f"Only {found_midis_num} midis found.",
                  "Downloading from cloud initialized.")
        else:
            print("Forcing update from cloud.")

        # if we have to download, remove all old midi files
        for filename in os.listdir(comp):
            if filename != comp_name + '.txt' and \
               os.path.isfile(os.path.join(comp, filename)) and \
               os.path.splitext(filename)[1] in ['.mid', '.midi']:
                os.remove(os.path.join(comp, filename))

        print(f"Directory '{comp}' cleared.")
        print(f"Downloading new files from {public_key}")

        final_url = BASE_URL + urlencode(dict(public_key=public_key))

        try:
            response = requests.get(final_url)
        except Exception:
            print("Error occurred while downloading datasets. Aborting.",
                  "Stable application work is not guaranteed.\n" + '-' * 30)
            continue

        try:
            download_url = response.json()['href']
        except KeyError:
            print("Error occurred while downloading datasets. Aborting.",
                  "Stable application work is not guaranteed.\n" + '-' * 30)
            continue

        download_response = requests.get(download_url)
        zip_path = os.path.join(comp, 'downloaded_file.zip')
        with open(zip_path, 'wb') as f:
            f.write(download_response.content)

        print("Archive downloaded, unpacking...")
        Archive(zip_path).extractall(comp)
        unarchived_folder_path = os.path.join(comp,
                                              comp_name.upper() + '_MIDIS')
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


if __name__ == "__main__":
    request_to_sownload_files()
    # download_datasets(force=False)
    # download_notes(force=False)
    # download_models(all_required=True)
