from medspacy.context import ConTextRule
#from . import callbacks
mis_context_rules = [
# More negation e.g. cover w/out fevers, cough
        ConTextRule("without", "NEGATED_EXISTENCE", direction="TERMINATE", max_scope=10),
        ConTextRule("w/o", "NEGATED_EXISTENCE", direction="TERMINATE", max_scope=10),
        ConTextRule("w/out", "NEGATED_EXISTENCE", direction="TERMINATE", max_scope=10),

#captures temporal context of fever occurences 
#
#DATE CONTEXT
#
        ConTextRule(
                literal="precise date [xxxx-xx-xx and xx-xx]",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"TEXT": {"REGEX": "^(2[0-9])?[0-9]{2}$"},"OP": "?"}, #optional year (digit)
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"TEXT": "-", "OP":"?"},  
                        {"IS_SPACE": True, "OP": "?" },          
                        {"TEXT": {"REGEX": "^(0?[1-9]|1[012])$"}},#month or day (digit)
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"TEXT": "-"},  
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"TEXT": {"REGEX": "^(0?[1-9]|[12]{1}\d{1}|3[01])$"}}, #day (digit)
                ],
                allowed_types={"MIS_FEVER", "COVID-19", "OTHER_CORONAVIRUS", "MIS_MAX_TEMP"} 
        ),

        ConTextRule(
                literal="precise date [xx-xx-xx(xx)]",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"TEXT": {"REGEX": "^(0?[1-9]|1[012])$"}}, #month (digit)
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"TEXT": "-"},  
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"TEXT":{"REGEX": "^(0?[1-9]|[12]{1}\d{1}|3[01])$"}}, #day (digit)
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"TEXT": "-", "OP": "?"},  
                        {"IS_SPACE": True, "OP": "?" },     
                        {"TEXT": {"REGEX": "^(2\d)?\d{2}$"}}, #year (2 or 4 digits)
                ],
                allowed_types={"MIS_FEVER", "COVID-19", "OTHER_CORONAVIRUS", "MIS_MAX_TEMP"}
        ),

        ConTextRule(
                literal="precise date [xx/xx(/xx(xx)) or xx.xx(.xx(xx))]",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"TEXT": {"REGEX": "^(0?[1-9]|1[012])[\/\.](0?[1-9]|[12]\d|3[01])([\/\.](2\d)?\d{2})?$"}} # month [dot or slash] day of month ( [dot or slash] 2 or 4 digit year )
                ],
                allowed_types={"MIS_FEVER", "COVID-19", "OTHER_CORONAVIRUS", "MIS_MAX_TEMP"}
        ),  

        ConTextRule(
                literal="precise date [month x, xx(xx)]",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"LOWER": {"REGEX":"jan(uary|\.)?|feb(ruary|\.)?|mar(ch|\.)?|ap(r(il)?|\.)?|jun(e|\.)?|jn|jul(y|\.)?|aug(ust|\.)|sep(t(ember)?|\.)?|oct|oct\.|october|(nov|dec)(ember|\.)?"} }, #month (literal)
                        {"IS_SPACE": True, "OP": "?" },
                        {"TEXT": {"REGEX": "[0-3]?\d"}}, #day of the month (digit)
                        {"TEXT": ",", "OP": "?"},
                        {"IS_SPACE": True, "OP": "?" },
                        {"TEXT": {"REGEX": "\d{2,4}"}, "OP": "?"} #year (2 or 4 digits)
                ],
                allowed_types={"MIS_FEVER","MIS_MAX_TEMP", "COVID-19", "OTHER_CORONAVIRUS"}
        ),

        ConTextRule(
                literal="days ago",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"TEXT": {"REGEX": "[0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|several|few|couple( of)?"}}, #number of (digit or literal)
                        {"IS_SPACE": False, "OP": "?"},
                        {"LOWER": {"IN": ["hr", "hrs", "hour", "hours", "d", "days", "day", "wk", "wks", "week", "weeks", "month", "months"]}}, #type of time measurement
                        {"IS_SPACE": False, "OP": "?"}, 
                        {"LOWER": {"REGEX": "ago|past|previous(ly)?"}}
                ],
                allowed_types= {"MIS_FEVER", "MIS_MAX_TEMP","COVID-19", "OTHER_CORONAVIRUS"} 
        ),

        ConTextRule(
                literal="on day #",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"LOWER": {"IN": ["on", "in", "by", "around", "about"]}, "OP":"?"},
                        # No 'hr' here so we avoid Heart Rate 133 (HR 133)
                        {"LOWER": {"IN": ["hrs", "hour", "hours", "d", "days", "day", "wk", "wks", "week", "weeks", "month", "months"]}}, #type of time measurement
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"TEXT": {"REGEX": '[0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|several|few|couple( of)?'}} #number of (digit or literal)
                ],
                allowed_types= {"MIS_FEVER", "MIS_MAX_TEMP","COVID-19", "OTHER_CORONAVIRUS"} 
        ),
       
        ConTextRule(
                literal="initiated in past",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"LOWER": {"IN": ["last", "past", "previous", "first", "for", "x", "around", "about"]}, "OP": "?"}, #past temporal component
                        {"TEXT":{"REGEX": "[0-9]+"}, "OP": "?"}, #number of (digit)
                        {"LOWER": {"REGEX": "one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|few|several|couple"}, "OP": "?"},#number of (literal)
                        {"IS_SPACE": True, "OP": "?" },
                        {"LOWER": {"IN": ["hr", "hrs", "hour", "hours", "d", "days", "day", "wk", "wks", "week", "weeks"]}} #type of time measurement
                ],
                allowed_types={"MIS_FEVER", "MIS_MAX_TEMP","COVID-19", "OTHER_CORONAVIRUS"} 
        ),

        ConTextRule(
                literal="[x# time]",
                category="MIS_DATE_CONTEXT",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"TEXT":{"REGEX": "x(\d{1,2})"}}, #number of (digit)
                        {"IS_SPACE": True, "OP": "?" },
                        {"LOWER": {"IN": ["hr", "hrs", "hour", "hours", "d", "days", "day", "wk", "wks", "week", "weeks"]}} #type of time measurement
                ]
        ),

        ConTextRule(
                literal="Fever Initially Detected",
                category="FEVER_INITIALLY_DETECTED",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"LOWER": {"REGEX": "began|since|begin(ning)?|start(ing)?|got|onset|not(ic)?ed|detect(ed)?"}}, #initially detected trigger terms
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"LOWER":{"IN": ["on"]}, "OP": "?"},   
                        {"IS_SPACE": True, "OP": "?" },  
                        {"LOWER": {"REGEX": "^(sun|mon|(t(ues|hurs))|fri)(day|\.)?$|wed(\.|nesday)?$|sat(\.|urday)?$|t((ue?)|(hu?r?))\.?$"}} #day of the week
                        ], 
                allowed_types={"MIS_FEVER", "MIS_MAX_TEMP","COVID-19", "OTHER_CORONAVIRUS"} 
        ), 
        
        ConTextRule(
                literal="Fever Initially Detected",
                category="FEVER_INITIALLY_DETECTED",
                direction="BIDIRECTIONAL",
                pattern=[
                        {"LOWER":{"IN": ["last", "past", "previous"]}}, 
                        {"IS_SPACE": True, "OP": "?" }, 
                        {"LOWER": {"REGEX": "^(sun|mon|(t(ues|hurs))|fri)(day|\.)?$|wed(\.|nesday)?$|sat(\.|urday)?$|t((ue?)|(hu?r?))\.?$"}} #day of the week
                ], 
                allowed_types={"MIS_FEVER", "MIS_MAX_TEMP","COVID-19", "OTHER_CORONAVIRUS"}
        ), 

        ConTextRule(
            literal="Fever Last Detected",
            category="FEVER_LAST_DETECTED",
            direction="FORWARD",
            pattern=[ 
                    {"LOWER": {"IN": ["ended", "ending", "end", "until", "terminated", "terminate", "terminating", "stopped", "stopping", "stop", "last", "lasted", "lasting", "since"]}}, 
                    {"IS_SPACE": True, "OP": "?" }, 
                    {"LOWER": {"REGEX": "[0-9]+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|several"}, "OP": "?"}, #number of (digit or literal)
                    {"IS_SPACE": True, "OP": "?" }, 
                    {"LOWER": {"IN": ["hrs", "hours", "days", "day", "d", "wk", "weeks","yesterday"]}}, 
            ],
            allowed_types={"MIS_FEVER", "MIS_MAX_TEMP", "COVID-19", "OTHER_CORONAVIRUS"} 
)
]   
