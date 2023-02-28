from medspacy.ner import TargetRule

# TODO may be able to get rid of most of this code since it intersects with manually input code
mis_concept_tag_rules_manual = {
    # MIS-C ADDITION
    #
    # NOTE that the case_report attributes are defined via Span.set_extension in util.py and is available via
    #      ent._.case_report or span._.case_report depending on other settings
    "mis_cardiac": [
        TargetRule(
            literal="arrhythmia",
            category="MIS_CARDIAC",
            attributes={"cui": "C0003811", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "arryth|aryth|arrhythmia|arythmia|arythmia$"}}, {"IS_PUNCT": True, "OP": "?"}], # include a few potential mis-spellings
        ),
        TargetRule(
            literal="cardiac dysfunction",
            category="MIS_CARDIAC",
            attributes={"cui": "C3277906", "is_imported": False},
            pattern=[{"LOWER": {"IN": ["card", "cardiac"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"IN": ["dys", "dysfunction"]}}],
        )
    ],
    "mis_renal": [
        TargetRule(
            literal="acute kidney injury",
            category="MIS_RENAL",
            attributes={"cui": "C0022660", "is_imported": False},
            pattern=[{"LOWER": {"IN": ["ac", "act", "acute"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"IN": ["kid", "kd", "kidney"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"IN": ["inj", "injure", "injur", "injury"]}}]
        ),
        TargetRule(
            literal="renal failure",
            category="MIS_RENAL",
            attributes={"cui": "C0035078", "is_imported": False},
            pattern=[{"LOWER": {"IN": ["ren", "rn", "renal", "rneal"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"IN": ["fail", "falr", "flr", "failure", "falure"]}}]
        ),
    ],
    "mis_respiratory": [
        TargetRule(
            literal="pneumonia",
            category="MIS_RESPIRATORY",
            attributes={"cui": "C0032285", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "pneum|pneumonia|pna$"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="ARDS",
            category="MIS_RESPIRATORY",
            attributes={"cui": "C0748355", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "ards"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="ARDS",
            category="MIS_RESPIRATORY",
            attributes={"cui": "C0748355", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "acute|act"}}, {"IS_PUNCT": True, "OP": "?"},
                {"LOWER": {"REGEX": "resp|respir|rsp"}}, {"IS_PUNCT": True, "OP": "?"},
                {"LOWER": {"REGEX": "distress|distres|distrs"}}, {"IS_PUNCT": True, "OP": "?"},
                {"LOWER": {"REGEX": "syndrom|syndrome|syn|synd"}}, {"IS_PUNCT": True, "OP": "?"}
            ],
        ),
    ],
    "mis_gastrointestinal": [
        TargetRule(
            literal="diarrhea",
            category="MIS_GASTROINTESTINAL",
            attributes={"cui": "C011991", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "diar|diarrhea"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="vomiting",
            category="MIS_GASTROINTESTINAL",
            attributes={"cui": "C0042963", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "vomiting|vomit|vmt"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="vomiting",
            category="MIS_GASTROINTESTINAL",
            attributes={"cui": "C0042963", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "threw|throwing|thrown"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "up"}}],
        ),
        TargetRule(
            literal="abdominal pain",
            category="MIS_GASTROINTESTINAL",
            attributes={"cui": "C0000737", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "abd|abdominal|stomach|stm|stom"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "pain|pn"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="abdominal pain",
            category="MIS_GASTROINTESTINAL",
            attributes={"cui": "C0000737", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "upset"}}, {"LOWER": {"REGEX": "stm|stom|stomach"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    "mis_dermatalogic": [
        TargetRule(
            literal="rash",
            category="MIS_DERMATALOGIC",
            attributes={"cui": "C0497365", "is_imported": False},
        )
    ],
    "mis_neurological": [
        TargetRule(
            literal="encephalopathy",
            category="MIS_NEUROLOGICAL",
            attributes={"cui": "C0085584", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "encephalopathy|enceph|encephal"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="confusion",
            category="MIS_NEUROLOGICAL",
            attributes={"cui": "C0009676", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "confusion|confused"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="altered mental status",
            category="MIS_NEUROLOGICAL",
            attributes={"cui": "C2830440", "is_imported": False},
            pattern=[{"LOWER": {"IN": ["alt", "al", "altered"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"IN": ["m", "ment", "mental"]}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"IN": ["stat", "status"]}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="altered mental status",
            category="MIS_NEUROLOGICAL",
            attributes={"cui": "C2830440", "is_imported": False},
            pattern=[{"LOWER": "ams"}]
        ),
    ],
    "mis_immunosuppressive_disorder": [
        TargetRule(
            literal="immunosuppressive disorder",
            category="MIS_IMMUNOSUPPRESSIVE_DISORDER",
            attributes={"cui": "C5555332", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "immuno|imm|immunosuppressive"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "dis|disorder"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="malignancy",
            category="MIS_IMMUNOSUPPRESSIVE_DISORDER",
            attributes={"cui": "C1707251", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "malig|malignant|malignancy"}}, {"IS_PUNCT": True, "OP": "?"}],
        )
    ],
    "mis_obesity": [
        TargetRule(
            literal="obesity",
            category="MIS_OBESITY",
            attributes={"cui": "C0028754", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "obese|obesity"}}],
        ),
        TargetRule(
            literal="bmi above",
            category="MIS_OBESITY",
            attributes={"cui": "C0028754", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "bmi|body\smass|body\smass\sindex"}},
                {"LOWER": {"REGEX": ">|=|gt|ov|over|above|abv|is"}},
                {"LOWER": {"REGEX": "(^[3-9][0-9])|(^[1-9][0-9][0-9])"}},
            ],
        ),
        TargetRule(
            literal="bmi",
            category="MIS_OBESITY",
            attributes={"cui": "C0028754", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "bmi|body\smass|body\smass\sindex"}},
                {"LOWER": {"REGEX": "(^[3-9][0-9])|(^[1-9][0-9][0-9])"}},
            ],
        )
    ],
    "mis_diabetes_one": [
        TargetRule(
            literal="type 1 diabetes",
            category="MIS_DIABETES_ONE",
            # TODO this cui is non-specific to type of diabetes
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "type|typ"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "1|one"}}, {"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="type1 diabetes",
            category="MIS_DIABETES_ONE",
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "type1|typ1"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="diabetes type 1",
            category="MIS_DIABETES_ONE",
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "type|typ"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "1|one"}}],
        ),
        TargetRule(
            literal="diabetes type1",
            category="MIS_DIABETES_ONE",
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "type1|typ1"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    "mis_diabetes_two": [
        TargetRule(
            literal="type 2 diabetes",
            category="MIS_DIABETES_TWO",
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "type|typ"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "2|two"}}, {"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="type2 diabetes",
            category="MIS_DIABETES_TWO",
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "type2|typ2"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="diabetes type 2",
            category="MIS_DIABETES_TWO",
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "type|typ"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "2|two"}}],
        ),
        TargetRule(
            literal="diabetes type2",
            category="MIS_DIABETES_TWO",
            attributes={"cui": "C0011849", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "diabetes|db|diab|diabetic"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "type2|typ2"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    "mis_seizures": [
        TargetRule(
            literal="seizures",
            category="MIS_SEIZURES",
            attributes={"cui": "C0036572", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "szrs|szr|seiz|seizure|seizures"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    "mis_congenital_heart_disease": [
        TargetRule(
            literal="congenital heart disease",
            category="MIS_CONGENITAL_HEART_DISEASE",
            attributes={"cui": "C0152021", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "congen|con|congenital"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "heart|hrt"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "dis|dz|disease"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    "mis_sickle_cell_disease": [
        TargetRule(
            literal="sickle cell disease",
            category="MIS_SICKLE_CELL_DISEASE",
            attributes={"cui": "C0019034", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "sickle|skl"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "cl|cell"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "dis|dz|disease"}, "OP": "?"}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    "mis_chronic_lung_disease": [
        TargetRule(
            literal="chronic lung disease",
            category="MIS_CHRONIC_LUNG_DISEASE",
            attributes={"cui": "C0746102", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "chronic|chrn"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "lung|lng"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "dis|dz|disease"}, "OP": "?"}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    "mis_other_congenital_malformation": [
        TargetRule(
            literal="other congenital malformation",
            category="MIS_OTHER_CONGENITAL_MALFORMATION",
            attributes={"cui": "C0000768", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "congen|con|congenital"}}, {"IS_PUNCT": True, "OP": "?"}, {"LOWER": {"REGEX": "malformation|malformations|mal|mals|malf|malfs|malform|malforms"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
    ],
    # TODO needs to include date/onset time as well
    "mis_fever": [
        TargetRule(
            literal="fever",
            category="MIS_FEVER",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[{"LOWER": {"REGEX": "fever|fev|^febrile"}}, {"IS_PUNCT": True, "OP": "?"}],
        ),
        TargetRule(
            literal="temp C",
            category="MIS_FEVER",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "^temp|^temperature"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^3[8-9](\.)?([0-9])*)|(^[4-9][0-9](\.)?([0-9])*)"}},
                {"LOWER": {"REGEX": "^c$|celcius|centigrade"}},
            ],
        ),
        TargetRule(
            literal="tempC",
            category="MIS_FEVER",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "^temp|^temperature"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is", "of"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^3[8-9](\.)?([0-9])*c$)|(^[4-9][0-9](\.)?([0-9])*c$)"}},
            ],
        ),
        TargetRule(
            literal="temp F",
            category="MIS_FEVER",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "^temp|^temperature"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is", "of"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^100\.[4-9]([0-9])*)|(^1[0-9][1-9](\.)?([0-9])*)"}},
                {"LOWER": {"REGEX": "^f$|fahrenheit"}},
            ],
        ),
        TargetRule(
            literal="tempF",
            category="MIS_FEVER",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "^temp|^temperature"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^100.[4-9]([0-9])*f)|(^1[0-9][1-9](\.)?([0-9])*f$)"}},
            ],
        )
    ],
    "mis_max_temp": [
        TargetRule(
            literal="max temp C",
            category="MIS_MAX_TEMP",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "tmax|max|maximum"}},
                {"LOWER": {"REGEX": "temp|temperature"}, "OP": "?"},
                {"LOWER": {"REGEX": "of"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^3[8-9](\.)?([0-9])*)|(^[4-9][0-9](\.)?([0-9])*)"}},
                {"LOWER": {"REGEX": "^c$|celcius|centigrade"}},
            ],
        ),
        TargetRule(
            literal="max tempC",
            category="MIS_MAX_TEMP",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "tmax|max|maximum"}},
                {"LOWER": {"REGEX": "temp|temperature"}, "OP": "?"},
                {"LOWER": {"REGEX": "of"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^3[8-9](\.)?([0-9])*c$)|(^[4-9][0-9](\.)?([0-9])*c$)"}}
            ],
        ),
        TargetRule(
            literal="max temp F",
            category="MIS_MAX_TEMP",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "tmax|max|maximum"}},
                {"LOWER": {"REGEX": "temp|temperature"}, "OP": "?"},
                {"LOWER": {"REGEX": "of"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is", "of"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^100.[4-9]([0-9])*)|(^1[0-9][1-9](\.)?([0-9])*)"}},
                {"LOWER": {"REGEX": "^f$|fahrenheit"}, "OP": "?"}, # assume fahrenheit unless otherwise stated
            ],
        ),
        TargetRule(
            literal="max temp, optionally F",
            category="MIS_MAX_TEMP",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"REGEX": "tmax|max|maximum|spiked"}},
                {"LOWER": {"REGEX": "a"}, "OP": "?"},
                {"LOWER": {"REGEX": "temp|temperature"}, "OP": "?"},
                {"LOWER": {"REGEX": "of"}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "above", "abv", "is"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^100.[4-9]([0-9])*)|(^1[0-9][1-9](\.)?([0-9])*$)|(^100.[4-9]([0-9])*f)|(^1[0-9][1-9](\.)?([0-9])*f$)"}},
            ],
        ),
        TargetRule(
            literal="fever max",
            category="MIS_MAX_TEMP",
            attributes={"cui": "C0015967", "is_imported": False},
            pattern=[
                {"LOWER": {"IN": ["fever", "fevers", "febrile", "fev", "fev."]}},
                {"LOWER": {"IN": ["max", "hit", "of", "to", "up to", "upto"]}, "OP": "?"},
                {"LOWER": {"IN": [">", "=", "gt", "ov", "over", "about", "above", "abv", "is", "up to", "upto"]}, "OP": "?"},
                {"LOWER": {"REGEX": "(^100.[4-9]([0-9])*)|(^1[0-9][1-9](\.)?([0-9])*$)|(^100.[4-9]([0-9])*f)|(^1[0-9][1-9](\.)?([0-9])*f$)"}},
            ],
        )
    ],
}
