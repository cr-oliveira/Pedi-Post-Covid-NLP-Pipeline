# misc_nlp in R

## Setup

### General Setup
While misc_nlp is still in active development:

1. Clone the [Inside Out Box misc_nlp](https://github.com/JewlsIOB/misc_nlp) project locally.
2. git checkout the branch / tag you would like to work on. For example: `git checkout v1.0.1.5`
3. Put all of this code into an .R studio file.
4. Change the `<misc_nlp project path>` in the sample usage code below to the location you cloned https://github.com/JewlsIOB/misc_nlp
5. If desired, scrub some of the HIPAA information from your clinical notes using https://github.com/JewlsIOB/nlm-scrubber-docker
   Maintain the date information if you would like to have that analyzed and reported on in your R code.
6. Change`<path>` and the `file` name in the sample usage code below to the data you would like to analyze.
   This file needs to be a comma-delimited csv file without a header line and with one id column
   and one full text column in quotes. See the `full_details_from_and_to_csv` function in
   [util.py](misc_nlp/util.py) for more csv file delimiter options if needed.
7. Change `<path>` and the `out_file` name in the sample usage code below to the csv file you would like to output.

## Sample Usage
Create an R studio .R file with all the code below and run it.  The first time it will take about 30-45 minutes to run,
depending on the speed of your computer. This is because it needs to install many packages into a consolidated
location so as to avoid version conflicts.
```
#
# 1. Install this R package
#
install.packages("<misc_nlp project path>/R/miscnlp_1.0.1.5.tar.gz", dependencies=TRUE, repos=NULL, lib.loc="<misc_nlp project path>/R/miscnlp_1.0.1.5.tar.gz", type = "source")

#
# 2. Use this R package
#
library(miscnlp)

#
# 3. Load the NLP engine
#
# See [util.py#load](misc_nlp/util.py) for options to use different dictionaries, etc.
miscnlp_env$nlp <- miscnlp_env$misc_nlp$load(model="default", concept_file="<misc_nlp project path>/misc_nlp/assets/covid19_signs_symptoms.csv", load_rules=TRUE)
miscnlp_env$nlp$pipe_names

#
# 4. Run the NLP code against a csv file.
#
file <- "<path>/deidentified_data.csv"
out_file <- "<path>/deidentified_data_output.csv"
# Uncomment this line to see more results in an R object `mis_identifiers` (function does *not* output a csv file)
# mis_identifiers <- miscnlp_env$misc_nlp$mis_identifiers_from_csv(nlp=miscnlp_env$nlp, csv_file_path=file)
# Uncomment this line to see more results in an R object `matches` (function does *not* output a csv file)
# matches <- miscnlp_env$misc_nlp$match_rubric_from_csv(nlp=miscnlp_env$nlp, csv_file_path=file)
full <- miscnlp_env$misc_nlp$full_details_from_and_to_csv(nlp=miscnlp_env$nlp, csv_input_path=file, csv_output_path=out_file)

#
# 5. Results
#     Check the location of `out_file` to see the resultant CSV file.
#     the `full` variable should now have all the results loaded into an R variable. 
#
```

## Sample Output

### miscnlp_env$misc_nlp$mis_identifiers_from_csv
```
id: list of mis-c related symptoms:
   [entity, medspacy entity label, UMLS cui, medspacy section category, medspacy is_historical, medspacy is_hypothetical, potential relevant date information]
```

### miscnlp_env$misc_nlp$match_rubric_from_csv
```
id: [[matching entities], [matching entity labels], [UMLS cuis], had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date]
```

### miscnlp_env$misc_nlp$full_details_from_and_to_csv
```
id (from file), entity label, UMLS cui, section category, is_historical, is_hypothetical,
is_negated, is_uncertain, is_family,
had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date,
entity_text, section_title, section_body
```

## Troubleshooting

### To update the misc_nlp python library:
Do this if any changes were made to the python code:
1. Close R
2. [back this up first if you are concerned...] `rm -rf ~/.RData; rm -rf ~/.Rprofile`
3. Remove the conda environment: `conda remove -p /Users/me/Library/r-miniconda/envs/miscnlp --all`
4. Reopen R

### To update the R library:
Do this if any changes were made to the R code:
1. `cd <misc_nlp project path>/R`
2. `R CMD build .`
3. Close and reopen R
4. Ensure your `install.packages` command has the correct tar.gz file in *both* the initial argument and `lib.loc` value.

### General Troubleshooting
1. To compile from the command line (note that you need to restart R to capture the newer version):

      ```R CMD build ./```

2. To increase RAM in R (if needed):

      ```
      vim ~/.Renviron
      R_MAX_VSIZE=20Gb
      ```

3. To Remove RData

      ```
      # To Remove the conda environment
      conda remove -p /Users/me/Library/r-miniconda/envs/miscnlp --all

      # To Remove a virtual environment if you accidentally created one (will cause problems!!)
      rm -rf ~/.virtualenvs/miscnlp

      # If there are lots of odd errors in your environment
      rm -rf ~/.RData; rm -rf ~/.Rprofile
      ```
