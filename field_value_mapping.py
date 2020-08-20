import os
import json


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


class Field_Value_Mapping:

    def __init__(self, pdf_name):
        """
        Creates a field value mapping file that can be manually filled in. This file is stored as a json dictionary.
        """
        os.system("pdftk " + pdf_name + " generate_fdf " + "output " + "fvmf.txt")
        field_names = get_fields_names("fvmf.txt")
        
        write_sorted_json_dict_file("fvmf.json", field_names)
        self.fvmf = "fvmf.json"
        self.pdf_name = pdf_name
        os.remove("fvmf.txt")

    def create_mapped_fdf_file(self, data_file):
        """
        Given a datafile and the class's field value mapping file creates a mapped fdf file

        """
        # get the name of the fdf file
        file_extension = data_file.find(".")
        fdf_file_name = data_file[:file_extension] + "_mapped.fdf"

        # create a fdf file to overwrite with the data
        os.system("pdftk " + self.pdf_name + " generate_fdf " + "output " + fdf_file_name)

        # create mapped json values file
        mapped_values_file = self.map_values(data_file)

        # create a mapped fdf file
        self.populate_fdf_file(mapped_values_file, fdf_file_name)

    def map_values(self, data_file):
        """
        Creates a mapped json value tuples file. Uses the name of the datafile to create mapped
        values with unique names.
        """
        with open("fvmf.json", "r") as fmvf:
            contents = json.load(fmvf)
        with open(data_file, "r") as df:
            data = json.load(df)
        
        for field in contents.keys():
            for attribute in data.keys():
                if contents[field] == attribute:
                    contents[field] = data[attribute]

        file_extension = data_file.find(".")

        with open(data_file[:file_extension] + "_mapped.json", "w") as fmvf:
            json.dump(contents, fmvf, indent=4)

    def populate_fdf_file(self, mapped_values_file, fdf_file):
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
        