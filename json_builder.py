import json
import re
from pathlib import Path

LIST_KEYS = {"PERSONS", "DATES", "PLACES", "ORGANIZATIONS"}

HEADER_RE = re.compile(
    r'^(ID|REPORTDATE|REFERENCEID|REPORTSOURCE|REPORTDESCRIPTION|PERSONS|DATES|PLACES|ORGANIZATIONS):\s*(.*)$'
)

def parse_reports(text: str):
    reports = []
    current = None
    desc_lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")

        # skip blank lines
        if not line.strip():
            continue

        # only lines that are exactly "REPORT" start a new object
        if line.strip() == "REPORT":
            if current is not None:
                if desc_lines:
                    current["REPORTDESCRIPTION"] = " ".join(desc_lines).strip()
                    desc_lines = []
                reports.append(current)
            current = {}
            continue

        # header lines
        m = HEADER_RE.match(line)
        if m:
            key, value = m.groups()

            # if we were collecting description and hit another header, finalize it
            if key != "REPORTDESCRIPTION" and desc_lines:
                current["REPORTDESCRIPTION"] = " ".join(desc_lines).strip()
                desc_lines = []

            if key == "REPORTDESCRIPTION":
                # description may be long; treat following non-header lines as continuation
                desc_lines = [value] if value else []
            elif key in LIST_KEYS:
                if value.strip():
                    if key == "PLACES":
                        current[key] = [v.strip().split("/") for v in value.split(";") if v.strip()]
                        place_list_temp = []
                        for places in current[key]:
                            place_temp = ""
                            for place in places:
                                if place.strip() != "":
                                    place_temp += (place + ", ")
                            place_list_temp.append(place_temp[:-2])
                        current[key] = place_list_temp
                    else:
                        current[key] = [v.strip() for v in value.split(";") if v.strip()]
                else:
                    current[key] = []
            else:
                current[key] = value.strip()
        else:
            # continuation of description
            if desc_lines:
                desc_lines.append(line.strip())

    # flush last report
    if current is not None:
        if desc_lines:
            current["REPORTDESCRIPTION"] = " ".join(desc_lines).strip()
        reports.append(current)

    return reports

def main(input_path: str, output_path: str | None = None):
    text = Path(input_path).read_text(encoding="utf-8")
    data = parse_reports(text)
    out = json.dumps(data, indent=2)
    if output_path:
        Path(output_path).write_text(out, encoding="utf-8")
    else:
        print(out)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py dataset.txt [output.json]")
        raise SystemExit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) >= 3 else None)
