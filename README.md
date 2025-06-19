# Ecuador_bills_09_24
This repo shows code to scrape and analyse all bills from the Ecuadorian National Assembly from 2009 to 2024.
The code is written in Python.

Test vs code
## Scrape_bills 
This file contains code to create a dataframe called 'clean_dataframe' with data about all the bills introduced to the Ecuadorian national Assembly in the 2009-2014 period. Each observation is a bill across all the possible legislative stages and contains a link to download the corresponding pdf document for each available stage. 
## Veto_bills
This file contains code to creata a dataframe called 'veto_dataframe' with a subset of 'clean_dataframe' that encompasses only those bills that passed the second debate and were subject to presidential veto. The 'veto_dataframe' includes a cleaned version of the text in second debate.  
## Vetoes_for_analysis
This file contains code to create a dataframe called 'match_veto_dataframe' with a genetic matched version of 'veto_dataframe' ready for further analysis.





