from field_value_mapping import Field_Value_Mapping
import os

if __name__ == "__main__":
    inst = Field_Value_Mapping("i-129f.pdf")
    inst.create_mapped_fdf_file("test_Data.json")
    