
import os
import argparse
import json

def create_pdftk_dump_data_fields_file(input_file, output_file):
    """
        Takes a pdf file as its input. It them executes the 
        pdftk dump_data_fields command and stores the result
        in output_file.
    """
    os.system("pdftk " + input_file + " dump_data_fields > " + output_file)


def create_checkbox_TF_mapping(filename):
    """
    creates a dictionary with the FieldName as the key and the Selected_Value of the checkbox as the value.
    This enables a value of true stored in user data to be mapped to the
    correct export value for the corresponding checkbox. This dictionary is stored in the new file
    checkbox_mapping_[filename]_.json

    This function should be called before create value mapping.
    """
    field_name_value_dict = {}

    def parse_user_data_line(line):
        colon_index = line.find(":")
        attribute_name = line[:colon_index].strip()
        attribute_value = line[colon_index+1:].strip()
        #print(attribute_name, ":", attribute_value)
        return attribute_name, attribute_value

    contents = ""

    with open(filename, "r") as f:
        contents = f.read()
    
    chunks = contents.split("---")

    button_chunks = []

    for chunk in chunks:
        lines = chunk.split("\n")
        chunk_dict = {}

        is_button = False
        has_field_state = False

        for line in lines:
            if not line.find(":") == -1:
                attribute_name, attribute_value = parse_user_data_line(line)
                #print(attribute_name, attribute_value)
                if attribute_value == "Button":
                    is_button = True

                # Avoids overwriting the export value with the default value of off
                # This only matters when multiple field state options are given
                if attribute_name == "FieldStateOption":
                    has_field_state = True
                    if not attribute_value == "Off":
                        chunk_dict[attribute_name] = attribute_value
                else:
                    chunk_dict[attribute_name] = attribute_value
       
        if is_button:
            if not has_field_state:
                print("Error no field state defined for button")
                chunk_dict["FieldStateOption"] = "Yes"
            
            field_name_value_dict[chunk_dict["FieldName"]] = chunk_dict["FieldStateOption"]
            #print(chunk_dict["FieldName"], chunk_dict["FieldStateOption"])
            
    with open('checkbox_mapping_'+filename[:-4]+'.json', 'w') as f:
        json.dump(field_name_value_dict, f, indent=4)

def keep_line(line):
    """Return True if the line should be retained and false otherwise."""
    return line.startswith("FieldName")

def create_value_mapping_file(filename):
    """
        This function should only be called after create_pdftk_dump_data_fields
        _file has been called.
    """
    contents = ""

    with open(filename, "r") as f:
        contents = f.read()
    
    contents_array = contents.split("\n")
    mapping_file_array = []
    
    # filter out irrelevant lines from the file
    # insert additional mapping fields
    for index, line in enumerate(contents_array):
        if keep_line(line):
            mapping_file_array.append(line)
            if line.startswith("FieldName:"):
                mapping_file_array.append("FieldValueMapping: ")

    with open(filename, "w") as f:
        for line in mapping_file_array:
            f.write(line+"\n")

def generate_data_fields_mapping_file(input_file, output_file):
    """
    This function gets raw information about data fields in
    the input_file and modifies them to create the 
    value mapping file, which takes the name stored in output_file.
    It also creates the checkbox true false mapping json file
    """
    create_pdftk_dump_data_fields_file(input_file, output_file)
    create_checkbox_TF_mapping(output_file)
    create_value_mapping_file(output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A tool to generate field value mapping files")
    parser.add_argument("--pdf", required=True, default=None, type=str, help="the input pdf")
    args = parser.parse_args()
    generate_data_fields_mapping_file(args.pdf, "fvm_"+args.pdf[:-4]+".txt")