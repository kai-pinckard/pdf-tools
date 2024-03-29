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

    def __init__(self, pdf_name, fvmf=None):
        """
        Creates a field value mapping file that can be manually filled in. This file is stored as a json dictionary.
        """
        self.pdf_name = pdf_name

        if fvmf is None:
            os.system("pdftk " + pdf_name + " generate_fdf " + "output " + "fvmf.txt")
            field_names = get_fields_names("fvmf.txt")
            
            write_sorted_json_dict_file("fvmf.json", field_names)
            self.fvmf = "fvmf.json"
            os.remove("fvmf.txt")
        else:
            self.fvmf = fvmf

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

        contents = self.shrink_dict_(contents)

        file_extension = data_file.find(".")
        mapped_values_file = data_file[:file_extension] + "_mapped.json"
        with open(mapped_values_file, "w") as fmvf:
            json.dump(contents, fmvf, indent=4)

        return mapped_values_file

    def shrink_dict_(self, sparse_dict):
        """
        Creates a new dict that has all the keys whose corresponding values
        are not the empty string.
        """
        new_dict = {}
        for key in sparse_dict.keys():
            if sparse_dict[key] != "":
                print(sparse_dict[key])
                new_dict[key] = sparse_dict[key]
        return new_dict

    def remove_empty_fdf_fields(self, fdf_file, fvmf_dict):
        with open(fdf_file, "r") as fdf:
            fdf_str = fdf.read()
        field_names = get_fields_names(fdf_file)
        for field in field_names:
            if not field in fvmf_dict.keys():
                #print(fdf_str)
                #print("========================================")
                fdf_str = self.remove_fdf_field(fdf_str, field)
                #print(fdf_str)
                
        
        print(fdf_str)
        with open(fdf_file, "w") as fdf_f:
            fdf_f.write(fdf_str)

    def remove_fdf_field(self, fdf_str, field_name):
        """
        Takes the string contents of an fdf file and returns the 
        string contents with the specified field removed.
        """
        index = fdf_str.find(field_name)
        print(field_name, index)
        if index == -1:
            print("error field_name not found and not removed")
        
        # Find and the next >>
        close_index = fdf_str.find(">>", index)
        close_index += len(">>")
        """
        Consider adjusting this
        """
        if fdf_str[close_index] != "]":
            close_index += 2

        # Find the previous <<
        open_index = fdf_str.rfind("<<", 0, index)

        # Remove the field

        if self.is_form_field(fdf_str, open_index, close_index):
            fdf_start = fdf_str[:open_index]

            fdf_end = fdf_str[close_index:]
            print("=============")
            print(fdf_str[open_index:close_index])
            fdf_str = fdf_start + fdf_end
        else:
            print(field_name, "is not a field and was not removed")

        return fdf_str
    
    def is_form_field(self, fdf_str, start, end):
        """
        This method checks if the item has more than one /T
        This is so that subforms are not attempted to be removed like fields.
        """
        count = 0
        ind = fdf_str.find("/T", start, end)
        ind = fdf_str.find("/T", ind+1, end)

        return -1 == ind


    def populate_fdf_file(self, mapped_values_file, fdf_file):
        """
        This function uses the mapped values file to populate the fdf file so that 
        it can be used to populate the pdf
        """
        with open(mapped_values_file, "r") as mapped:
            mapped_values = json.load(mapped)


        self.remove_empty_fdf_fields(fdf_file, mapped_values)

        with open(fdf_file, "r") as fdf_f:
            fdf = fdf_f.read()

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
        