"""
https://github.com/ccnmtl/fdfgen



"""
import json
from fdfgen import forge_fdf
import os
import argparse


def test_read_user_data_file():
    user_data_dict = {
        "surname": "Clifton",
        "first name": "johnston",
        "id": "1231"
    }

    assert(user_data_dict == read_user_data_file("test_user_data_file.txt"))

def read_user_data_file(user_data_file):
    """
    The user datafile is a text file that uses colons ":" as delimiters within lines
    each piece of user data is on its own line and the name of the data field goes before
    the colon while the actual data value is after the colon and separated from it by
    a space. These data field names are used in the value_mapping_file to identify which
    value should be used to fill that pdf form field. 
    """
    with open(user_data_file, "r") as f:
        contents = f.read()
    content_lines = contents.split("\n")
    user_data_dict = {}
    
    def parse_user_data_line(line):
        colon_index = line.find(":")
        attribute_name = line[:colon_index].strip()
        attribute_value = line[colon_index+1:].strip()
        #print(attribute_name, ":", attribute_value)
        return attribute_name, attribute_value

    for index, line in enumerate(content_lines):
        attribute_name, attribute_value = parse_user_data_line(line)
        user_data_dict[attribute_name] = attribute_value
    #print(user_data_dict)
    return user_data_dict

def create_field_mapping_dict(completed_data_fields_mapping_file):
    """
        Takes a data_fields_mapping_file that has been manually filled in and
        returns a dictionary containing all the field names as the keys and
        all the names of the corresponding user data fields as the values.
    """
    with open(completed_data_fields_mapping_file, "r") as f:
        contents = f.read()

    contents_array = contents.split("\n")
    field_mapping_dict = {}
    for index, line in enumerate(contents_array):
        if line.startswith("FieldName:"):
            _, field_name = parse_data_line(line)
            if index >= len(contents_array)-1:
                raise Exception("Missing FieldValueMapping: line after fieldname")
            else:
                _, value_mapping = parse_data_line(contents_array[index+1])
                # only fields that have been filled in will be added
                if not value_mapping == "":
                    print(value_mapping)
                    field_mapping_dict[field_name] = value_mapping
    return field_mapping_dict

def print_dict(d):
    for key in field_mapping_dict.keys():
        print(key, field_mapping_dict[key])

def parse_data_line(line):
        colon_index = line.find(":")
        attribute_name = line[:colon_index].strip()
        attribute_value = line[colon_index+1:].strip()
        #print(attribute_name, ":", attribute_value)
        return attribute_name, attribute_value

def create_fieldname_value_tuples_list(completed_data_fields_mapping_file, user_data_file):
    #Warning do not allow users to enter True or False in text fields

    base_file_name = completed_data_fields_mapping_file

    with open("checkbox_mapping_"+base_file_name[:-4]+".json", "r") as f:
        checkbox_mapping_dict = json.load(f)


    user_data_dict = read_user_data_file(user_data_file)
    field_mapping_dict = create_field_mapping_dict(completed_data_fields_mapping_file)
    
    fieldname_value_tuples = []
    for key in field_mapping_dict.keys():
        print(key)
        fieldname_value_tuples.append((key, user_data_dict[field_mapping_dict[key]]))

    # Replace values of True and False with the appropriate export value for the checkbox
    for index, field in enumerate(fieldname_value_tuples):
        # Check if the field is a button (Checkbox)
        if field[1] == "True" or field[1] == "False":
            if field[1] == "True":
                fieldname_value_tuples[index] = (field[0], checkbox_mapping_dict[field[0]])
            else:
                fieldname_value_tuples[index] = (field[0], "Off")
    return fieldname_value_tuples

def create_fdf(fields, fvm):
    fdf = forge_fdf("", fields, [], [] , [])

    filename = fvm[-4]+".fdf"
    with open(filename, "wb") as fdf_file:
        fdf_file.write(fdf)
    return filename


# Try setting teh value in the field to True. it looks like this is auto interpreted correctly.""
if __name__ == "__main__":
    #create_fieldname_value_tuples_list("i-129f_fields.txt", "test_user_data_file.txt")
    parser = argparse.ArgumentParser(description="A tool for populating pdfs")
    parser.add_argument("--udf", required=True, default=None, type=str, help="the raw user data")
    parser.add_argument("--fvm", required=True, default=None, type=str, help="field value mapping file")
    parser.add_argument("--pdf", required=True, default=None, type=str, help="the pdf to fill")
    parser.add_argument("--out", required=True, default=None, type=str, help="The name of the filled pdf")
    args = parser.parse_args()
    fields = create_fieldname_value_tuples_list(args.fvm, args.udf)
    print(fields)
    fdf_file = create_fdf(fields, args.fvm)
    os.system("pdftk "+args.pdf+" fill_form "+fdf_file+" output "+args.out)
    #fields = [('form1[0].#subform[0].Pt1Line4_Checkboxes[0]', "A")]
    #fields = [('form1[0].#subform[0].Pt1Line8_State[0]', "OR")]
    #fields = [('form1[0].#subform[0].Pt1Line6a_FamilyName[0]', "Pinckard"),("form1[0].#subform[0].Pt1Line6c_MiddleName[0]", "david")]
    #fields = [('form1[0].#subform[0].Pt1Line6a_FamilyName[0]', 'Clifton'), ('form1[0].#subform[0].Pt1Line6b_GivenName[0]', 'johnston')] #was working
    """ fdf = forge_fdf("", fields, [], [] , [])

    filename = "testszz.fdf"
    with open(filename, "wb") as fdf_file:
        fdf_file.write(fdf) """