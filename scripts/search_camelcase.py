import os, re
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
pattern = re.compile(r"firstName|lastName|maidenName|genevaDegree|updateSelector|prefSalutation|phoneType|addressLine1|addressLine2|postalCode|maritalStatus|spouseName|spouseGenevaGrad|spouseGenevaDegree|startDate|nonGEducation|additionalUpdates|volunteerRadio|volunteerChoices|otherVolunteer", re.I)
for dirpath, dirs, files in os.walk(root):
    if '__pycache__' in dirpath.split(os.sep):
        continue
    for f in files:
        path = os.path.join(dirpath, f)
        try:
            txt = open(path, encoding='utf-8').read()
        except Exception:
            continue
        for m in pattern.finditer(txt):
            print(path, '->', m.group(0))
