# pdf-tools

The main goal of pdf-tools is to create a pdf filing microservice. Pdf-tools requires three inputs:a pdf file to fill, the data to fill it, and a data-to-pdf mapping file. The data must be in json format as must the data-to-pdf mapping file. The data-to-pdf mapping file allows any one to easily use the software to fill a new pdf without having to touch any of the application's code

I will create a tool for linking json data files with the
appropriate form fields to fill. The user data will be read in with
json.load to create a python object for easy transitioning. 

The pdftk tool is very useful  for this process the most useful commands are

To create an empty fdf file:
pdftk <PDF_FILE> generate_fdf output <OUTPUT_FILE_NAME>

To read a json data file:
this package can handle this using json.load

To create a mapping file:
This package allows the user to easily create a document which lists
which json data fields correspond to which form fields

To fill the fdf:
This package can use the mapping file to fill out the fdf with the 
data from a specific json file. Allowing for form filling automation.

To fill a pdf with a properly filled in fdf file:

pdftk <PDF_TO_FILL> fill_form <FDF_FILE> output <FILLED_PDF_NAME>


Note:
I am removing the fdfgen dependency. The only thing that it seems to do is 
fill in the slots in the fdf file. I think I can do this easily enough and
remove a dependency. 
