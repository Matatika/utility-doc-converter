import mammoth
import click
import os
import yaml

from pathlib import Path

def check_file_type(file_path):
    abs_file_path = os.path.abspath(file_path)
    _, file_ext = os.path.splitext(abs_file_path)
    if file_ext == ".docx":
        return True
    if file_ext == '.md':
        click.secho("File already of type markdown, not converting", fg="yellow")
        return False
    else:
        click.secho("File is not of type .doc or .docx, not converting", fg="red")
        return False


def convert_files_in_dir(file_path):

    if file_path[-1] != "/":
        file_path += "/"

    for file in os.listdir(file_path):
        if file.endswith(".doc") or file.endswith(".docx"):
            print(f"Converting {file}...")
            file_abs_path = os.path.abspath(file_path + file)
            convert_to_dataset(file_abs_path)
        else:
            print(f"File: {file} not .doc or .docx. Skipping conversion")


def convert_to_dataset(file_path):

    abs_file_path_no_ext, _ = os.path.splitext(os.path.abspath(file_path))


    with open(file_path, "rb") as docx_file:
        result = mammoth.convert_to_markdown(docx_file)

    _, file_name = os.path.split(abs_file_path_no_ext)

    try:
        _, title = file_name.split("DTN profile ")
    except:
        print("Could not find 'DTN profiles' to split on. Using full file name.")
        title = file_name

    abs_path = str(Path(abs_file_path_no_ext).parent.resolve()) + "/"

    try:
        _, markdown = result.value.split("\n\nDescription ").replace("\\#", "#")
        markdown = "![" + markdown
    except:
        print("Cannot find image at top of profile. Attempting raw conversion.")
        markdown = result.value.replace("\\#", "#")

    dataset = {
        "description": markdown,
        "source": "DTN Profiles",
        "title": title,
        "version": "datasets/v0.2"        
    }

    dataset_path = abs_path + file_name.lower().replace(' ', '-')

    with open(dataset_path + '.yml', "w") as yaml_file:
        yaml.dump(dataset, yaml_file, default_flow_style=False)
