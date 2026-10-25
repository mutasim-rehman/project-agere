"""Verdict-only financial review; no invented field/step localization."""
BINARY_INSTRUCTION=('Independently judge operand relevance (correct row/year), operations, and units for the question. '
 'Arithmetic execution alone does not prove relevance. Return verdict PASS only if all three are correct; '
 'FAIL if any is incorrect; UNKNOWN if evidence is insufficient.')
BINARY_SCHEMA={'type':'object','properties':{'verdict':{'enum':['PASS','FAIL','UNKNOWN']}},'required':['verdict'],'additionalProperties':False}


def binary_review(raw):
    if not isinstance(raw,dict) or set(raw)!={'verdict'} or raw['verdict'] not in ('PASS','FAIL','UNKNOWN'):
        return None
    accepted=raw['verdict']=='PASS'
    return {'verdict':'PASS' if accepted else 'FAIL','binary_verdict':raw['verdict'],
            'unsupported_fields':[] if accepted else ['program_review'],
            'review_scope':'whole_program','repair_localization_available':False,
            'steps_to_repair':[],'repair_kind':'NONE' if accepted else 'REPLAN'}
