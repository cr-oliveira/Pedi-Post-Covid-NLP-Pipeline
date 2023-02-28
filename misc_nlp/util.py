import spacy
import medspacy
import os # for in dir(<module>) syntax
import sys # to blockPrint
import re # for identifiying mis entities and splitting text on delimeters
import csv # for reading csv file
from pathlib import Path # for reading csv file

from spacy.tokens import Doc, Span, Token
from spacy import displacy

from .cov_bsv.document_classifier import DocumentClassifier

import misc_nlp.cov_bsv.knowledge_base.preprocess_rules as cov_bsv_preprocess_rules
from .cov_bsv.knowledge_base import concept_tag_rules
from .cov_bsv.knowledge_base import target_rules
from .cov_bsv.knowledge_base import section_rules
from .cov_bsv.knowledge_base import context_rules
from .cov_bsv.knowledge_base import postprocess_rules
from .mis.knowledge_base import mis_preprocess_rules
from .mis.knowledge_base import mis_concept_tag_rules_imported
from .mis.knowledge_base import mis_concept_tag_rules_manual
from .mis.knowledge_base import mis_target_rules
from .mis.knowledge_base import mis_section_rules
from .mis.knowledge_base import mis_context_rules
from .mis.knowledge_base import mis_postprocess_rules
from .mis.knowledge_base import mis_context_rules

FIELD_DELIMITER = ';'
SECOND_FIELD_DELIMITER = '|'

DEFAULT_PIPENAMES = [
    "preprocessor",
    "tagger",
    "parser",
    "concept_tagger",
    "target_matcher",
    "sectionizer",
    "context",
    "postprocessor",
    "document_classifier"
]

CONTEXT_MAPPING = {
    "NEGATED_EXISTENCE": {"is_negated": True},
    "FUTURE/HYPOTHETICAL": {"is_future": True},
    "HISTORICAL": {"is_historical": True},
    "DEFINITE_POSITIVE_EXISTENCE": {"is_positive": True},
    "ADMISSION": {"is_positive": True},
    "NOT_RELEVANT": {"is_not_relevant": True},
    "UNCERTAIN": {"is_uncertain": True},
    "UNLIKELY": {"is_uncertain": True},
    "SCREENING": {"is_screening": True},
    "OTHER_EXPERIENCER": {"is_other_experiencer": True},
    "CONTACT": {"is_other_experiencer": True},
    "PATIENT_EXPERIENCER": {"is_other_experiencer": False, "is_positive": True},
}

# Cov-basv settings
# SECTION_ATTRS = {
#     "diagnoses": {"is_positive": True},
#     "observation_and_plan": {"is_positive": True},
#     "past_medical_history": {"is_positive": True},
#     "problem_list": {"is_positive": True},
# }
SECTION_ATTRS = {
    'addendum': {'is_positive': True},
    'allergy': {'is_hypothetical': True},
    'allergies': {'is_hypothetical': True},
    'chief_complaint': {'is_positive': True},
    'comments': {'is_hypothetical': True},
    'diagnoses': {'is_hypothetical': True},
    'education': {'is_hypothetical': True},
    'family_history': {'is_family': True},
    'hospital_course': {'is_hypothetical': True},
    'imaging': {'is_uncertain': True},
    'labs': {'is_uncertain': True},
    'labs_and_studies': {'is_uncertain': True},
    'medications': {'is_uncertain': True},
    'observation_and_plan': {'is_uncertain': True},
    'other': {'is_uncertain': True},
    'past_medical_history': {'is_historical': True},
    'patient_education': {'is_uncertain': True},
    'patient_instructions': {'is_uncertain': True},
    'problem_list': {'is_hypothetical': True},
    'physical_exam': {'is_uncertain': True},
    'reason_for_examination': {'is_uncertain': True},
    'signature': {'is_uncertain': True},
    'social_history': {'is_hypothetical': True},
    'sexual_and_social_history': {'is_hypothetical': True},
}

# MIS-C ADDITION
# TODO write tests for this as well and maybe relocate code to a library...
# Helper to make a category key -- multiply each part by an exponent of 10 to create a unique id
#
# id - of the format 3.3 or 1.5.7.2 -- expects no more than 4 parts
#
# output - an integer
def category_key_maker(id):
    split_key = id.split('.')
    category_key = ''
    for i in range(4):
        # Handle the case that the id is not 4 parts
        if (i > len(split_key) - 1):
            part = '00'
        elif (int(split_key[i]) < 10):
            part = '0' + str(split_key[i])
        else:
            part = split_key[i]
        # Add +1 to avoid chance of multiplying times 0
        category_key += str(part)
    return int(category_key)

# MIS-C ADDITION
# Returns the initial key used to make the category_key
#
# category_key - integer. a key made by category_key_maker
#
# output - id of the format 3.3 or 1.5.7.2
def category_key_decoder(category_key):
    key_str = str(category_key)
    if len(key_str) < 8:
        key_str = '0' + key_str
    id_str = ''
    for i in [3, 2, 1, 0]:
        # convert to int to get rid of preceding 0 then back to string
        num = int(key_str[2*i:2+(2*i)])
        # do not keep trailing 0's
        if id_str != '' or num != 0:
            id_str = str(num) + '.' + id_str

    # strip away last period
    return id_str[0:-1]

# MIS-C ADDITION
#
# Allow the visualization to take in additional args to pass to displacy
# TODO ability to visualize POS and more perhaps
# TODO MOVE somewhere else / PR for medspacy
def mis_visualize_dep(spanner, **args):
    """Create a dependency-style visualization for
    ConText targets and modifiers in doc. This will show the
    relationships between entities in doc and contextual modifiers.
    """
    token_data = []
    token_data_mapping = {}
    token_data_ids = []
    for token in spanner:
        data = {"text": token.text, "tag": "", "index": token.i}
        token_data.append(data)
        token_data_mapping[token] = data
        token_data_ids.append(token.i)

    # Merge phrases
    targets_and_modifiers = [*spanner.doc._.context_graph.targets]
    targets_and_modifiers += [mod.span for mod in spanner.doc._.context_graph.modifiers]
    for span in targets_and_modifiers:
        first_token = span[0]
        last_token = span[0]
        # Stop this loop if we have context graph information from different parts of the doc
        if not first_token.i in token_data_ids or not last_token.i in token_data_ids:
            #print("1. skipping token: ", first_token.i, ", ", last_token.i) # debug
            break

        data = token_data_mapping[first_token]
        data["tag"] = span.label_

        if len(span) == 1:
            continue

        idx = data["index"]
        for other_token in span[1:]:
            # Add the text to the display data for the first word
            # and remove the subsequent token
            data["text"] += " " + other_token.text
            # Remove this token from the list of display data
            token_data.pop(idx + 1)

        # Lower the index of the following tokens
        for other_data in token_data[idx + 1 :]:
            other_data["index"] -= len(span) - 1

    dep_data = {"words": token_data, "arcs": []}
    # Gather the edges between targets and modifiers
    for target, modifier in spanner.doc._.context_graph.edges:
        if not target[0] in token_data_mapping or not modifier.span[0] in token_data_mapping:
#             print("2. skipping token:", target[0].i, ", ", modifier.span[0])
            break
        target_data = token_data_mapping[target[0]]
        modifier_data = token_data_mapping[modifier.span[0]]
#         print(target[0])
        # Stop this loop if we have context graph information from different parts of the doc
        if not target[0].i in token_data_ids or not modifier.span[0].i in token_data_ids:
#             print("3. skipping token: ", target_data[0].i, ", ", modifier_data[0].i) # debug
            break
        # If a Doc object is passed in Doc.start is not a function
        spanner_start = 0 if "start" not in dir(spanner) else spanner.start
        # index is indexed off of the whole doc rather than spanner, so switch to index based on the span itself
        dep_data["arcs"].append(
            {
                "start": min(target_data["index"], modifier_data["index"]) - spanner_start,
                "end": max(target_data["index"], modifier_data["index"]) - spanner_start,
                "label": modifier.category,
                "dir": "right" if target > modifier.span else "left",
            }
        )
#         print("arcs:", dep_data["arcs"]) # debug
    return displacy.render(dep_data, manual=True, jupyter=True, options=args)

# MIS-C ADDITION
#
def full_details_from_and_to_csv(nlp=None, csv_input_path=None, csv_output_path=None, header_row=False, delim=",", quote_char='"', suppress_output=False, debug=False):
#     """ Given a misc_nlp spaCy language object and a CSV file with one id column and one medical record per row,
#         returns a dictionary of full match details.
#
#         Args:
#             nlp (misc_nlp object): The misc_nlp object obtained from misc_nlp.load
#             csv_input_path (string): The full file path to a csv file of the format col1=row id/some identifier, col2=health record.
#                                      the file should be compatible with UTF-8 format.
#                                      Defaults to no header row.
#             csv_output_path (string): The full file path to write the csv file.
#                                      Defaults to no header row.
#             header_row (boolean): whether there is a header row in the csv file. Defaults to false.
#             delim (string): delimiter for the csv file. Defaults to ,.
#             quote_char (string): quote character for the csv file. Defaults to '"'.
#             suppress_output (boolean): whether to suppress outputting the object. Simply writes to a csv file. Defaults to False.
#             debug (boolean): whether to run this function in debug mode, which prints out date tagging details. Defaults to false
#
#         Returns:
#             1. Outputs a csv file to csv_output_path with the following information
#             2. Also creates a dictionary of MIS-C identifiers where the key is the first column of the csv_file_path,
#             and value matches #get_mis_identifiers(doc)
#
#             id: [entity label, UMLS cui, section category, is_historical, is_hypothetical,
#                  is_negated, is_uncertain, is_family,
#                  had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date,
#                  entity_text, section_title, section_body]
#     """

    outfile = open(csv_output_path, 'w')
    headers = [
          'id',
          'entity_label', 'UMLS_cui', 'section_category', 'is_historical', 'is_hypothetical', 'is_negated',
          'is_uncertain', 'is_family',
          'had_fever', 'fever_date', 'max_fever', 'max_fever_date', 'had_covid', 'covid_date',
          'entity_text', 'section_title', 'section_body']
    writer = csv.writer(outfile, delimiter=delim, quotechar=quote_char, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)

    full_dict = dict()
    with Path(csv_input_path).open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=delim, quotechar=quote_char)

        # skip header row if there is one
        if (header_row):
            next(csvreader)
        for row in csvreader:
            id = row[0]
            health_record = row[1]

            # NLP processing. Medspacy keeps throwing a warning that isn't helpful
            # "'matcher' does not have any patterns defined.", so suppress that
            with HiddenPrints():
              doc = nlp(health_record)

            full_dict[id] = full_details(doc, debug)
            for detail in full_dict[id]:
              writer.writerow([str(id)] + detail)

    outfile.close()

    return None if suppress_output else full_dict

def mis_identifiers_from_csv(nlp=None, csv_file_path=None, header_row=False, delim=",", quote_char='"'):
#   """Given a misc_nlp spaCy language object and a CSV file with one id column and one medical record per row,
#    returns a dictionary of #get_mis_identifiers(doc) per medical record.
#
#     Args:
#         nlp (misc_nlp object): The misc_nlp object obtained from misc_nlp.load
#         csv_file_path (string): The full file path to a csv file of the format col1=row id/some identifier, col2=health record.
#                                 the file should be compatible with UTF-8 format.
#                                 Defaults to no header row.
#         header_row (boolean): whether there is a header row in the csv file. Defaults to false.
#         delim (string): delimiter for the csv file. Defaults to ,.
#         quote_char (string): quote character for the csv file. Defaults to '"'.
#
#     Returns:
#         a dictionary of MIS-C identifiers where the key is the first column of the csv_file_path,
#         and value matches #get_mis_identifiers(doc)
#
#         id: [entity, entity label, UMLS cui, section category, is_historical, is_hypothetical, potential relevant date information]
#     """
    mis_identifiers = dict()
    with Path(csv_file_path).open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=delim, quotechar=quote_char)
        # skip header row if there is one
        if (header_row):
            next(csvreader)
        for row in csvreader:
            id = row[0]
            health_record = row[1]

            # NLP processing. Medspacy keeps throwing a warning that isn't helpful
            # "'matcher' does not have any patterns defined.", so suppress that
            with HiddenPrints():
              doc = nlp(health_record)

            # save the data
            mis_identifiers[id] = get_mis_identifiers(doc)

    return mis_identifiers

def match_rubric_from_csv(nlp=None, csv_file_path=None, header_row=False, delim=",", quote_char='"'):
#   """Given a misc_nlp spaCy language object and a CSV file with one id column and one medical record per row,
#    returns a dictionary of #get_match_rubric(doc) per medical record.
#
#     Args:
#         nlp (misc_nlp object): The misc_nlp object obtained from misc_nlp.load
#         csv_file_path (string): The full file path to a csv file of the format col1=row id/some identifier, col2=health record.
#                                 the file should be compatible with UTF-8 format.
#                                 Defaults to no header row.
#         header_row (boolean): whether there is a header row in the csv file. Defaults to false.
#         delim (string): delimiter for the csv file. Defaults to ,.
#         quote_char (string): quote character for the csv file. Defaults to '"'.
#
#     Returns:
#         a dictionary of MIS-C identifiers where the key is the first column of the csv_file_path,
#         and value matches #get_match_rubric(doc)
#
#         id: [[matching entities], [matching entity labels], [UMLS cuis], had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date]
#     """
    match_rubrics = dict()
    with Path(csv_file_path).open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=delim, quotechar=quote_char)
        # skip header row if there is one
        if (header_row):
            next(csvreader)
        for row in csvreader:
            id = row[0]
            health_record = row[1]

            # NLP processing. Medspacy keeps throwing a warning that isn't helpful
            # "'matcher' does not have any patterns defined.", so suppress that
            with HiddenPrints():
              doc = nlp(health_record)

            # save the data
            match_rubrics[id] = get_match_rubric(doc)

    return match_rubrics

# TODO delete code
# # MIS-C ADDITION
# # Organize data by MIS categories
# # TODO Category 3 needs not ent._.is_historical
# def case_report_categories(doc):
#     categories = {}
#     for ent in doc.ents:
#         if (not ent._.is_negated and not ent._.is_family):
#             case_report_ids = ent._.case_report_ids
#             for id in case_report_ids:
#                 category_key = category_key_maker(id)
#                 if not category_key in categories.keys():
#                     categories[category_key] = []
#                 categories[category_key].append(ent)
#     return categories

def get_mis_identifiers(doc):
# Get entities that have an MIS or covid-19 label
# Given an nlp-processed document
#
# Returns for the doc:
#   [entity, medspacy entity label, UMLS cui, section category, is_historical, is_hypothetical, potential relevant date information]
    matches = []
    for ent in doc.ents:
        if re.match('[mM][iI][sS]_', ent.label_, flags=0) == None and ent.label_ != 'COVID-19':
            continue
        if (not ent._.is_negated and not ent._.is_family and not ent._.is_uncertain):
            date_info = ''
            for mod in ent._.modifiers:
                if mod and hasattr(mod, 'category') and (mod.category.startswith('MIS_DATE_CONTEXT') or mod.category.startswith('FEVER_INITIALLY_DETECTED')):
                    # Uses FIELD_DELIMITER and SECOND_FIELD_DELIMITER in regex here (may not need SECOND_FIELD_DELIMITER)
                    if len(date_info) > 0 and (mod.span.text in re.split(r';|\|', date_info)):
                        continue # do not re-add this date attribute
                    else:
                        if len(date_info) > 0:
                            date_info += FIELD_DELIMITER
                        date_info = date_info + mod.span.text
            section_category = None
            if ent._.section and hasattr(ent._.section, 'category'):
                section_category = ent._.section.category
            matches.append([ent, ent.label_, ent._.cui, section_category, ent._.is_historical, ent._.is_hypothetical, date_info])
    return matches

def get_match_rubric(doc):
# Rank likelihood of covid-19
# Returns:
#   [[matching entities], [matching entity labels], [UMLS cuis], had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date]
    ents = set()
    labels = set()
    cuis = set()
    had_fever = None
    fever_date = ''
    max_fever = None
    max_fever_date = ''
    had_covid = None
    covid_date = ''
    for ent in doc.ents:
        if re.match('[mM][iI][sS]_', ent.label_, flags=0) == None and ent.label_ != 'COVID-19':
            continue
        if (not ent._.is_negated and not ent._.is_family and not ent._.is_uncertain):
            date_info = ''
            for mod in ent._.modifiers:
                if mod and hasattr(mod, 'category') and (mod.category.startswith('MIS_DATE_CONTEXT') or mod.category.startswith('FEVER_INITIALLY_DETECTED')):
                    if len(date_info) > 0:
                        date_info += FIELD_DELIMITER
                    date_info += mod.span.text
            if ent.label_ == 'COVID-19' and ent._.is_positive:
                had_covid = True
                if len(date_info) > 0:
                    if len(covid_date) > 0:
                        covid_date += SECOND_FIELD_DELIMITER
                    covid_date += date_info
            if ent.label_ == 'MIS_FEVER' and ent._.is_positive:
                had_fever = True
                if len(date_info) > 0:
                    if len(fever_date) > 0:
                        fever_date += SECOND_FIELD_DELIMITER
                    fever_date += date_info
            if ent.label_ == 'MIS_MAX_TEMP' and ent._.is_positive:
                had_fever = True
                max_fever = ent
                if len(date_info) > 0:
                    if len(max_fever_date) > 0:
                        max_fever_date += SECOND_FIELD_DELIMITER
                    max_fever_date += date_info
            ents.add(ent)
            labels.add(ent.label_)
            cuis.add(ent._.cui)
    return [ents, labels, cuis,had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date]

def full_details(doc, debug=False):
#     """Given a misc_nlp spaCy processed document, gives the full match details.
#
#       Args:
#           doc (misc_nlp document object): The misc_nlp object obtained from misc_nlp(text)
#           debug (boolean): whether to run this function in debug mode, which prints out date tagging details. Defaults to false
#
#       Returns:
#           [entity label, UMLS cui, section category, is_historical, is_hypothetical,
#            is_negated, is_uncertain, is_family, potential relevant date information, entity text,
#            section_title, section_category, section_body]
#
#     """
    # key - set = ent.label_|section category|is_historical|is_hypothetical|is_negated|is_uncertain|is_family
    full_dict = dict()
    had_fever = None
    fever_date = ''
    max_fever = None
    max_fever_date = ''
    had_covid = None
    covid_date = ''

    # First run through to get the overarching information
    for ent in doc.ents:
        date_info = ''
        for mod in ent._.modifiers:
            if mod and hasattr(mod, 'category') and (mod.category.startswith('MIS_DATE_CONTEXT') or mod.category.startswith('FEVER_INITIALLY_DETECTED')):
                if len(date_info) > 0:
                    date_info += FIELD_DELIMITER
                if debug:
                    date_info += ent + '=' + mod.span.text # debugging
                else:
                    date_info += mod.span.text

        if ent._.is_positive and not ent._.is_uncertain and not ent._.is_family and not ent._.is_negated:
            if ent.label_ == 'COVID-19' and ent._.is_positive:
                had_covid = True
                if len(date_info) > 0:
                    if len(covid_date) > 0:
                        covid_date += SECOND_FIELD_DELIMITER
                    covid_date += date_info
            if ent.label_ == 'MIS_FEVER' and ent._.is_positive:
                had_fever = True
                if len(date_info) > 0:
                    if len(fever_date) > 0:
                        fever_date += SECOND_FIELD_DELIMITER
                    fever_date += date_info
            if ent.label_ == 'MIS_MAX_TEMP' and ent._.is_positive:
                had_fever = True
                max_fever = ent
                if len(date_info) > 0:
                    if len(max_fever_date) > 0:
                        max_fever_date += SECOND_FIELD_DELIMITER
                    max_fever_date += date_info

    # Second run-through to get entity categories
    for ent in doc.ents:
        section_category = None
        if ent._.section and hasattr(ent._.section, 'category'):
            section_category = ent._.section.category
        # key - set = ent.label_|section category|is_historical|is_hypothetical|is_negated|is_uncertain|is_family
        this_tag = ent.label_ + '|' + str(section_category) + '|' + str(ent._.is_historical) + '|' + str(ent._.is_hypothetical) + '|' + str(ent._.is_negated) + '|' + str(ent._.is_uncertain) + '|' + str(ent._.is_family)

        if full_dict.get(this_tag):
            full_dict[this_tag]['entity_text'] = full_dict[this_tag]['entity_text'] + ';' + str(ent)
            # Cuis don't always exist
            if full_dict[this_tag]['cuis']:
              full_dict[this_tag]['cuis'] = full_dict[this_tag]['cuis'] + ';' + str(ent._.cui)
            else:
              full_dict[this_tag]['cuis'] = str(ent._.cui)
        else:
            full_dict[this_tag] = dict()
            full_dict[this_tag]['entity_text'] = str(ent)
            full_dict[this_tag]['cuis'] = str(ent._.cui)
            if ent._.section and hasattr(ent._.section, 'title_span'):
              full_dict[this_tag]['section_title'] = str(ent._.section.title_span)
              full_dict[this_tag]['section_body'] = str(ent._.section.body_span)
            else:
              # This really shouldn't happen, but avoid errors
              full_dict[this_tag]['section_title'] = ''
              full_dict[this_tag]['section_body'] = ent._.section

        # NOTE that I do not currently check dates for uncertain areas of text...

        full_dict[this_tag]['entity_label'] = ent.label_
        full_dict[this_tag]['section_category'] = section_category
        full_dict[this_tag]['is_historical'] = str(ent._.is_historical)
        full_dict[this_tag]['is_hypothetical'] = str(ent._.is_hypothetical)
        full_dict[this_tag]['is_negated'] = str(ent._.is_negated)
        full_dict[this_tag]['is_uncertain'] = str(ent._.is_uncertain)
        full_dict[this_tag]['is_family'] = str(ent._.is_family)

    return_values = []
    for key in sorted(full_dict):
        d = full_dict[key]
        return_values.append([d['entity_label'], d['cuis'], d['section_category'], d['is_historical'], d['is_hypothetical'], d['is_negated'], d['is_uncertain'], d['is_family'], had_fever, fever_date, max_fever, max_fever_date, had_covid, covid_date, d['entity_text'], d['section_title'], d['section_body']])

    return return_values

# From https://stackoverflow.com/a/45669280/2611078
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr.close()
        sys.stderr = self._original_stderr


def _set_attributes():
    # NOTE that force=True avoids errors if multiple matches are in a single span
    # TODO delete this old code
#     Doc.set_extension("case_report_categories", getter=case_report_categories, force=True) # MIS-C ADDITION
#     Span.set_extension("case_report_ids", default=[], force=True) # MIS-C ADDITION
#     Span.set_extension("case_report_type", default="", force=True) # MIS-C ADDITION
    Doc.set_extension("get_mis_identifiers", getter=get_mis_identifiers, force=True)
    Doc.set_extension("get_match_rubric", getter=get_match_rubric, force=True)
    Span.set_extension("is_imported", default=False, force=True) # MIS-C ADDITION --> whether this was an imported rule as opposed to manual
    Span.set_extension("cui", default="", force=True) # MIS-C ADDITION --> umls cui
    Span.set_extension("is_future", default=False, force=True)
    Span.set_extension("is_historical", default=False, force=True)
    Span.set_extension(
        "is_positive", default=False, force=True
    )  # Explicitly has a positive indicator
    Span.set_extension(
        "is_not_relevant", default=False, force=True
    )  # News reports, etc..
    Span.set_extension("is_negated", default=False, force=True)
    Span.set_extension("is_uncertain", default=False, force=True)
    Span.set_extension("is_screening", default=False, force=True)
    Span.set_extension("is_other_experiencer", default=False, force=True)
    Span.set_extension("concept_tag", default="", force=True)

def load(model="default", enable=None, disable=None, load_rules=True, concept_file=None, set_attributes=True):
    """Load a spaCy language object with cov_bsv and mis pipeline components.
    By default, the base model will be 'en_core_web_sm' with the 'tagger'
    and 'parser' pipeline components, supplemented with the following custom
    components:
        - preprocessor (set to be nlp.tokenizer): Modifies the preprocessed text and returns
            a tokenized Doc. Preprocess rules are defined in cov_bsv/mis.knowledge_base.preprocess_rules
        - concept_tagger: Assigns a semantic tag in a custom attribute "token._.concept_tag"
            to each Token in a Doc, which helps with concept extraction and normalization.
            Concept tag rules are defined in cov_bsv.knowledge_base.concept_tag_rules,
            mis.knowledge_base.concept_tag_rules_imported and mis.knowledge_base.concept_tag_rules_manual.
        - target_matcher: Extracts spans to doc.ents using extended rule-based matching.
            Target rules are defined in cov_bsv/mis.knowledge_base.target_rules.
        - sectionizer: Identifies note section headers in the text and assigns section titles to
            entities and tokens contained in that section. Section patterns are defined in
            cov_bsv/mis.knowledge_base.section_patterns.
        - context: Identifies semantic modifiers of entities and asserts attributes such as
            positive status, negation, and other experiencier. Context rules are defined in
            cov_bsv/mis.knowledge_base.context_rules.
        - postprocessor: Modifies or removes the entity based on business logic. This handles
            special cases or complex logic using the results of earlier entities. Postprocess rules
            are defined in cov_bsv/mis.knowledge_base.postprocess_rules.
        - document_classifier: Assigns a label of "POS", "UNK", or "NEG" to the doc._.cov_classification.
            A document will be classified as positive if it has at least one positive, non-excluded entity.

    Args:
        model: The name of the base spaCy model to load. If "default" will load the tagger and parser
            from "en_core_web_sm".
        enable (iterable or None): A list of component names to include in the pipeline.
        If None, will include all pipeline components listed above.
        disable (iterable or None): A list of component names to exclude.
            Cannot be set if `enable` is not None.
        concept_file (string): file path to a csv file with one header row and 3 columns of the format:
            - symptom name
            - UMLS cui identifier
            - comma+space-separated list of terms that should be assigned to this category.
              Note that the capitalization of terms in the third row does not matter. e.g.
              Lymphopenia   C0024312    lymphopenia, lymphocytopenia, low lymphocyte number
        load_rules (bool): Whether or not to include default rules for custom components. Default True.
        set_attributes (bool): Whether or not to register custom attributes to spaCy classes. If load_rules is True,
            this will automatically be set to True because the rules in the knowledge base rely on these custom attributes.
            The following extensions are registered (all defaults are False unless specified):
                Span._.cui # UMLS cui id, if available
                Span._.is_imported # indicates imported concept_tag_rules
                Span._.is_future
                Span._.is_historical
                Span._.is_positive
                Span._.is_not_relevant
                Span._.is_negated
                Span._.is_uncertain
                Span._.is_screening
                Span._.is_other_experiencer
                Span._.concept_tag (default "")

    Returns:
        nlp: a spaCy Language object
    """
    if enable is not None and disable is not None:
        raise ValueError("Either `enable` or `disable` must be None.")
    if disable is not None:
        # If there's a single pipe name, nest it in a set
        if isinstance(disable, str):
            disable = {disable}
        else:
            disable = set(disable)
        enable = set(DEFAULT_PIPENAMES).difference(set(disable))
    elif enable is not None:
        if isinstance(enable, str):
            enable = {enable}
        else:
            enable = set(enable)
        disable = set(DEFAULT_PIPENAMES).difference(enable)
    else:
        enable = DEFAULT_PIPENAMES
        disable = set()

    if model == "default":
        model = "en_core_web_sm"
        disable.add("ner")


    if set_attributes:
        _set_attributes()

    import spacy
    nlp = spacy.load(model, disable=disable)
    if "preprocessor" in enable:
        from medspacy.preprocess import Preprocessor
        preprocessor = Preprocessor(nlp.tokenizer)
        if load_rules:
            preprocessor.add(cov_bsv_preprocess_rules)
            if len(mis_preprocess_rules):
                preprocessor.add(mis_preprocess_rules)
        nlp.tokenizer = preprocessor

    if "concept_tagger" in enable:
        from spacy.tokens import Token

        Token.set_extension("concept_tag", default="", force=True)
        from medspacy.ner import ConceptTagger

        concept_tagger = nlp.add_pipe("medspacy_concept_tagger")
        if load_rules:
            for (_, rules) in concept_tag_rules.items():
                concept_tagger.add(rules)
            if concept_file:
                for (_, rules) in mis_concept_tag_rules_imported(concept_file).items():
                    concept_tagger.add(rules)
            for (_, rules) in mis_concept_tag_rules_manual.items():
                concept_tagger.add(rules)

    if "target_matcher" in enable:
        from medspacy.ner import TargetMatcher

        target_matcher = nlp.add_pipe("medspacy_target_matcher")
        if load_rules:
            for (_, rules) in target_rules.items():
                target_matcher.add(rules)
            for (_, rules) in mis_target_rules(concept_file).items():
                target_matcher.add(rules)

    if "sectionizer" in enable:
        from medspacy.section_detection import Sectionizer
        sectionizer = nlp.add_pipe("medspacy_sectionizer", config={"rules":None, "add_attrs": SECTION_ATTRS})
        if load_rules:
            sectionizer.add(section_rules)
            if len(mis_section_rules):
                sectionizer.add(mis_section_rules)

    if "context" in enable:
        from medspacy.context import ConTextComponent

        context = nlp.add_pipe("medspacy_context", config={"rules": None, "add_attrs": CONTEXT_MAPPING, "remove_overlapping_modifiers": True})
        if load_rules:
            context.add(context_rules)
            if len(mis_context_rules):
                context.add(mis_context_rules)

    if "postprocessor" in enable:
        from medspacy.postprocess import Postprocessor

        postprocessor = nlp.add_pipe("medspacy_postprocessor", config={"debug": False})
        if load_rules:
            postprocessor.add(postprocess_rules)
            if len(mis_postprocess_rules):
                postprocessor.add(mis_postprocess_rules)


    if "document_classifier" in enable:
        document_classifier = nlp.add_pipe("cov_classification")

    return nlp


def visualize_doc(doc, document_id=None, jupyter=True, colors=None):
    """Display a processed doc using an NER-style spaCy visualization.
    By default, this will highlight entities, modifiers, and section titles
    and will display the document classification as a header.

    doc: A spaCy Doc which has been processed by the cov_bsv pipeline.
    document_id: An optional document identifier to be displayed as a header.
    jupyter (bool): If True, will display the resulting HTML inline in a notebook.
        If False, will return the HTML as a string.
    """
    from IPython.display import display, HTML
    from medspacy.visualization import visualize_ent

    html = "<h2>Document Classification: {0}</h2>".format(doc._.cov_classification)
    if document_id is not None:
        html += "<h3>Document ID: {0}</h3>".format(document_id)
    html += visualize_ent(doc, colors=colors, jupyter=False)
    if jupyter is True:
        display(HTML(html))
    else:
        return html

#in need to update
def preserve_dates(file_name):
    """
    Given a file_name, writes a list of dates to exclude from the NPM scrubber
    """
    with open(file_name, 'w') as file:
        for year_idx in range(10):
          year = 20 + year_idx
          file.write("20" + str(year) + "\n")
          for month_idx in range(12):
            month = 1 + month_idx
            month_with_zero = month
            if month < 10:
                month_with_zero = "0" + str(month)
            for day_idx in range(31):
                day = 1 + day_idx
                day_with_zero = day
                if day < 10:
                    day_with_zero = "0" + str(day)
                file.write(str(day) + "/" + str(month) + "\n")
                file.write(str(day) + "/" + str(month) + "/" + str(year) + "\n")
                file.write(str(day) + "-" + str(month) + "-" + str(year) + "\n")
                file.write(str(day) + "/" + str(month) + "/20" + str(year) + "\n")
                file.write(str(day) + "-" + str(month) + "-20" + str(year) + "\n")
                file.write("20" + str(year) + "-" + str(month) + "-" + str(day) + "\n")

                file.write(str(day_with_zero) + "/" + str(month_with_zero) + "\n")
                file.write(str(day_with_zero) + "/" + str(month_with_zero) + "/" + str(year) + "\n")
                file.write(str(day_with_zero) + "-" + str(month_with_zero) + "-" + str(year) + "\n")
                file.write(str(day_with_zero) + "/" + str(month_with_zero) + "/20" + str(year) + "\n")
                file.write(str(day_with_zero) + "-" + str(month_with_zero) + "-20" + str(year) + "\n")
                file.write("20" + str(year) + "-" + str(month_with_zero) + "-" + str(day_with_zero)  + "\n")

        for month_name in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
            file.write(month_name + "\n")

        for month_abbrev in ["Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            file.write(month_abbrev + "\n")

        for month_alt_abbrev in ["Aprl", "Sept", "Octob", "Novem", "Decem"]:
            file.write(month_alt_abbrev + "\n")

