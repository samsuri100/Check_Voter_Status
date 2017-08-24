# Check_Voter_Status
Program reads a CSV file and checks the Dallas County Registrar of Voter's website to verify registration status using Python and the Selenium library. This program was developed for Battleground Texas, a political non-profit in Austin, Texas. The program was developed in order to investigate the error rate of the Dallas County Registrar of Voters in correctly registering applicants, and to provide evidence for a civil lawsuit if evidence of voter suppression was found. 

The program uses Selenium, and geckodriver (FireFox) to automate the process. Excel can modify dates strings that contain 0's, so the program reformats date strings so that they are always 10 characters long. The program also scans each first and last name to make sure that it is not blank and only contains valid alphabetical characters, with the addition of '.', '-', ' ', and "'".

## To Make Changes to the Program
The current program was made to work exclusively for the Dallas County Registrar of Voter's website, and xpaths in the program point to locations on that website. In addition, the program was designed to read a CSV file that has 7 columns. The verified status would be appended to the 8th column. The position of the seven patterns is important, as each row became a python list, with the index position indicating the column number. 

Future users can modify the number of columns that are read by the program. If their content falls in different columns that mine, they can point to a different index position accordingly. Xpaths can also be changed easily.
