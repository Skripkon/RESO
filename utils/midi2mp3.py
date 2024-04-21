import os


def midi2mp3(filename: int):
    """
    Converts a specified .mid file into an .mp3 file
    and puts it into the same directory
    """
    mp3_file = os.path.join("generated_data", f"{filename}.mp3")
    filepath = os.path.join("generated_data", f"{filename}.mid")
    os.system(
        f'timidity {filepath} -Ow -o {mp3_file} --volume=200'
    )
    return mp3_file
