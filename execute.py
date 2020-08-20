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

def map_values(data_file):
    """
    Creates a mapped json value tuples file.
    """
    with open("fvmf.json", "r") as fmvf:
        contents = json.load(fmvf)
    with open(data_file, "r") as data_file:
        data = json.load(data_file)
    
    for field in contents.keys():
        for attribute in data.keys():
            if contents[field] == attribute:
                contents[field] = data[attribute]
    
    with open("mapped.json", "w") as fmvf:
        json.dump(contents, fmvf, indent=4)
    

def populate_fdf_file(mapped_values_file, fdf_file):
    """
    This function uses the mapped values file to populate the fdf file so that 
    it can be used to populate the pdf
    """
    with open(mapped_values_file, "r") as mapped:
        mapped_values = json.load(mapped)

    with open(fdf_file, "r") as fdf_file:
        fdf = fdf_file.read()

    start = 0
    offset = len("/V (")
    while not fdf.find("/V", start) == -1:
        value_start = fdf.find("/V", start)
        value_end = fdf.find("/T", value_start)
        start = value_end

        # get the name of the field we are currently replacing
        field_end = fdf.find(")", value_end)
        field_name = fdf[value_end + len("/V ("): field_end]

        # get the replacement value
        value = mapped_values[field_name] + ")\n"

        # insert the value into the string
        first_content = fdf[:value_start + len("/V (")]
        last_content = fdf[value_end:]
        fdf = first_content + str(value) + last_content

    with open("test.fdf", "wb") as f:
        f.write(fdf)
    

if __name__ == "__main__":
    #run this then fill in values then run next line
    #generate_field_value_mapping_file("first.pdf")
    map_values("test_Data.json")
    #populate_fdf_file("mapped.json", "fvmf.txt")