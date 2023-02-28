from medspacy.ner import TargetRule
import csv
from pathlib import Path

def mis_concept_tag_rules_imported(file_path):
    # TODO determine best file name / **environment variable** configurable option
    # entities_loc = Path.cwd().parent / "config" / "covid19_signs_symptoms.csv"

    names = dict()
    descriptions = dict()
    concept_tag_rules = { }
    with Path(file_path).open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        next(csvreader) # skip header row
        for row in csvreader:
            name = row[0]
            qid = row[1]
            mis_name = 'mis_' + name.lower().replace(' ', '_').replace(',', '_')

            names = row[2].split(" or ")
            matches = [name.lower() for name in names]

            concept_tag_rules[mis_name] = [
                TargetRule(
                    literal=name.lower(),
                    category=mis_name.upper(),
                    attributes={"cui": qid, "is_imported": True},
                    pattern=[{"LOWER": {"IN":
                        matches
                    }}]
                )
            ]

    return concept_tag_rules

mis_concept_tag_rules_imported