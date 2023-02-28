# misc_nlp

This library uses spaCy natural language processing to process medical text.  It is particularly aimed at catching MIS-C, but is easily configurable to process other medical texts. Change the [signs and symptoms](misc_nlp/assets/covid19_signs_symptoms.csv) input file to refine which data it looks for. [util.py](misc_nlp/util.py) has most of the code logic. This code is built upon [Alec Chapman's COV BSV work](https://github.com/abchapman93/VA_COVID-19_NLP_BSV). This code focuses on detecting COVID-19, and we utilize some of his code in the cov_bsv subfolder.

This library by default uses the spaCy small web language library. Any library can be used as long as it is compatiable with the verison of spaCy in use.

## Data Cleansing

See https://github.com/JewlsIOB/nlm-scrubber-docker for code to assist in cleansing HIPAA data before data processing. Please ensure you follow your organization's specific policies on HIPAA.

## Sample Usage

### Visualize Data
Outputs each input document with entities highlighted in different colors.
```
import misc_nlp

nlp = misc_nlp.load(model="default", concept_file="[misc_nlp installation dir]/misc_nlp/misc_nlp/assets/covid19_signs_symptoms.csv", load_rules=True)

file_names = ['note_1188.txt', 'note_261.txt', 'note_449.txt', 'note_681.txt', 'note_758.txt']
docs = {}
for file_name in file_names:
print(file_name + ":")

    # read whole file to a string
    text_file = open("[directory]/non_hippa_files/" + file_name, "r")
    text = text_file.read()

    docs[file_name] = nlp(text)

    # close file
    text_file.close()

    misc_nlp.visualize_doc(docs[file_name])
```

### Inclusion criteria

```
for file_name in docs:
  print("DOC:" + file_name)
  for ent in docs[file_name].ents:
    if (not ent._.is_negated and not ent._.is_family and not ent._.is_historical):
      print(ent, ent._.is_negated, ent._.is_family, ent._.is_historical, ent._.target_rule.literal, ent._.cui)
```
Sample output:
```
DOC:note_1188.txt
fever False False False <MIS_FEVER> C0015967
COVID infection False False False <COVID-19> infection
malaise False False False <MIS_MALAISE> C0231218
fever, False False False <MIS_FEVER> C0015967
tmax 104 False False False <MIS_MAX_TEMP> C0015967
fevers False False False <MIS_FEVER> C0015967
...
```

### Many files at once

```
import misc_nlp

nlp_obj = misc_nlp.load(model="default", concept_file="<misc_nlp path>/misc_nlp/misc_nlp/assets/covid19_signs_symptoms.csv", load_rules=True)

file = "<path>/deidentified_notes.csv"

mis_identifiers = misc_nlp.mis_identifiers_from_csv(nlp=nlp_obj, csv_file_path=file)
print("mis identifiers:")
print(mis_identifiers)

matches = misc_nlp.match_rubric_from_csv(nlp=nlp_obj, csv_file_path=file)
print("matches:")
print(matches)
```

Sample output:
```
mis identifiers:
{'301': [[abdominal pain., 'MIS_GASTROINTESTINAL', 'C0000737', 'chief_complaint', False, False, ''], [vomiting,, 'MIS_GASTROINTESTINAL', 'C0042963', 'chief_complaint', False, False, ''], [Covid-19, 'COVID-19', 'C5203670', 'past_medical_history', True, False, ''], [Pneumococcal, 'MIS_RESPIRATORY', 'C0032285', 'past_medical_history', True, False, '']], '415': [[fever [, 'MIS_FEVER', 'C0015967', 'chief_complaint', False, False, ''], [fever., 'MIS_FEVER', 'C0015967', 'chief_complaint', False, False, ''], [vomiting, 'MIS_GASTROINTESTINAL', 'C0042963', 'chief_complaint', False, False, ''], [abdominal pain., 'MIS_GASTROINTESTINAL', 'C0000737', 'chief_complaint', False, False, ''], [fever., 'MIS_FEVER', 'C0015967', 'past_medical_history', True, False, ''], [38.4 C, 'MIS_FEVER', 'C0015967', 'past_medical_history', True, False, 'Last 24 hours']], '478': [[Fever [, 'MIS_FEVER', 'C0015967', 'chief_complaint', False, False, 'mother'], [chronic lung disease,, 'MIS_CHRONIC_LUNG_DISEASE', 'C0746102', 'chief_complaint', False, False, 'mother'], [fevers, 'MIS_FEVER', 'C0015967', 'chief_complaint', False, False, 'mother'], [fever, 'MIS_FEVER', 'C0015967', 'chief_complaint', False, False, 'around 104'], [fever, 'MIS_FEVER', 'C0015967', 'chief_complaint', False, False, ''], [covid, 'COVID-19', 'C5203670', 'chief_complaint', False, False, ''], [Chronic lung disease, 'MIS_CHRONIC_LUNG_DISEASE', 'C0746102', 'past_medical_history', True, False, ''], [Fever., 'MIS_FEVER', 'C0015967', 'past_medical_history', True, False, 'Last Dose11/10/2020']]}

matches:
{'\ufeff103': [{SARS CoV-2, fever., SARS CoV-2, SARS-CoV2 infection, known SARS CoV-2 exposure, abdominal pain,, vomiting., Pneumococcal, rash, Pneumococcal, vomiting, diarrhea., rash, diarrhea,, abdominal pain,, fevers,}, {'MIS_FEVER', 'MIS_GASTROINTESTINAL', 'COVID-19', 'MIS_RESPIRATORY', 'MIS_DERMATALOGIC'}, {'', 'C0497365', 'C5203670', 'C011991', 'C0000737', 'C0032285', 'C0042963', 'C0015967'}, True, '', None, '', True, '2 weeks agofor 3 daysdosing dexamethasone'], '301': [{Covid-19, vomiting,, Pneumococcal, abdominal pain.}, {'MIS_GASTROINTESTINAL', 'MIS_RESPIRATORY', 'COVID-19'}, {'C0042963', 'C0032285', 'C5203670', 'C0000737'}, None, '', None, '', None, ''], '415': [{fever., 38.4 C, abdominal pain., vomiting, fever., fever [}, {'MIS_FEVER', 'MIS_GASTROINTESTINAL'}, {'C0042963', 'C0015967', 'C0000737'}, True, '', None, '', None, ''], '478': [{Fever., Fever [, fevers, fever, Chronic lung disease, covid, chronic lung disease,, fever}, {'MIS_FEVER', 'MIS_CHRONIC_LUNG_DISEASE', 'COVID-19'}, {'C0015967', 'C0746102', 'C5203670'}, True, 'around 104', None, '', True, '']}
```

### Save to CSV with extra detail

```
import misc_nlp

nlp_obj = misc_nlp.load(model="default", concept_file="<misc_nlp file path>/misc_nlp/misc_nlp/assets/covid19_signs_symptoms.csv", load_rules=True)

in_file = "<path>/deidentified_notes.csv"
out_file = "<path>/deidentified_notes_output.csv"
full = misc_nlp.full_details_from_and_to_csv(nlp=nlp_obj, csv_input_path=in_file, csv_output_path=out_file)

print(full)
```

Outputs a python object as well as writing the information to a CSV file with the headers:
```
id (from file), entity label, UMLS cui, section category, is_historical, is_hypothetical,
is_negated, is_uncertain, is_family,
had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date,
entity_text, section_title, section_body
```


### R

Please see the [R/README.md](R/README.md) file in the R sub-folder for instructions on how to use misc_nlp in R.
