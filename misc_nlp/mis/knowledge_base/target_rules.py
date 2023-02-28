from medspacy.ner import TargetRule
import re
from .concept_tag_rules_imported import mis_concept_tag_rules_imported
from .concept_tag_rules_manual import mis_concept_tag_rules_manual

def mis_target_rules(imported_file_path):
    # Combine the two files together
    if (imported_file_path):
        mis_concept_tag_rules = mis_concept_tag_rules_manual | mis_concept_tag_rules_imported(imported_file_path)
    else:
        mis_concept_tag_rules = mis_concept_tag_rules_manual

    #
    # MIS-C ADDITION
    #
    # Dynamically add misc-c symptom categories
    target_rules = { }
    for key in mis_concept_tag_rules.keys():
        key = key.upper()
        if (re.search('^MIS_', key)):
            target_rules[key] = [
                TargetRule(
                    "<" + key + ">",
                    key,
                    pattern=[{"_": {"concept_tag": key}, "OP": "+"}],
                ),
            ]

    return target_rules

mis_target_rules