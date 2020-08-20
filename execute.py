import json
import os


with open("test_Data.json", "r") as f:
    content = json.load(f)

print(content["lastname"])



def get_fields_names(fdf_file):
    with open(fdf_file, "r") as f:
        content = f.read()

    field_names = []
    
    start = 0
    offset = len("/T (")
    while not content.find("/T", start) == -1:
        field_start = content.find("/T", start)
        field_end = content.find(")", field_start)
        start = field_end
        field_name = content[field_start + offset:field_end]
        field_names.append(field_name)
    
    return field_names


def generate_field_value_mapping_file(pdf_name):
    """
    Creates a field value mapping file that can be manually filled in. This file is stored as a json dictionary.
    """
    os.system("pdftk " + pdf_name + " generate_fdf " + "output " + "fvmf.txt")
    field_names = get_fields_names("fvmf.txt")
    field_names = get_fields_names("fvmf.txt")

    field_names_dict = {}
    for field_name in field_names:
        field_names_dict[field_name] = ""

    with open("fvmf.json", "w") as f:
        json.dump(field_names_dict, f, indent=4)


if __name__ == "__main__":
    generate_field_value_mapping_file("i-129f.pdf")