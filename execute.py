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


def write_sorted_json_dict_file(file_name, keys):
    """
    Previously this was used but it is not in the order of the form
      with open("fvmf.json", "w") as f:
        json.dump(field_names_dict, f, indent=4, sort_keys=True)
    """
    file_data = "{\n"
    for key in keys[:-1]:
        file_data += "    \"" + str(key) + "\": \"\",\n"

    # Handle the last line here since json does not allow a "," on the last element
    file_data += "    \"" + str(keys[len(keys)-1]) + "\": \"\"\n"
    file_data += "}\n"
    with open(file_name, "w") as f:
        f.write(file_data)

def generate_field_value_mapping_file(pdf_name):
    """
    Creates a field value mapping file that can be manually filled in. This file is stored as a json dictionary.
    """
    os.system("pdftk " + pdf_name + " generate_fdf " + "output " + "fvmf.txt")
    field_names = get_fields_names("fvmf.txt")
    
    write_sorted_json_dict_file("fvmf.json", field_names)

if __name__ == "__main__":
    generate_field_value_mapping_file("i-129f.pdf")