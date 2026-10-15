"""NHCE Contacts Dictionary and CSV Parser.

This module provides the unique contacts dictionary (normalized 10-digit phone number -> name)
and utilities to load/parse contact CSV exports.
"""

import csv
import re
from pathlib import Path
from typing import Dict


def normalize_phone_number(phone: str) -> str:
    """Normalize phone number to 10 digits by removing country code (+91 / 91) and non-digits."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91") and len(digits) == 12:
        return digits[2:]
    return digits


# Dictionary of unique contacts (10-Digit Mobile Number -> Name)
CONTACTS: Dict[str, str] = {
    "7019707178": "NHCB1 DYUTHI SN F-BCA PG | Dance Sports and God's",
    "7842270305": "NHCB1 G Reddy Vinay M-BCA PG | Creative thinking",
    "7892710064": "NHCE1 Aman D M-ENG Parents | Chess",
    "7349046046": "NHCE1 Ayush HR M-ENG Government hostel | Vollyball",
    "6362032348": "NHCE1 Keerthana G Reddy F-ENG College Hostel | Listen to music, hearing to spiritual talks",
    "7676229711": "NHCE1 Manvitha M L F-ENG College Hostel | Singing",
    "9108262619": "NHCE1 Nanda Uday Mudhole F-ENG College Hostel | Listening to music",
    "8123100542": "NHCE1 Navamohan R M-ENG Community Hostel | Farming",
    "9502892220": "NHCE1 Palle Mamatha F-ENG College Hostel | Listening to music",
    "9866286182": "NHCE1 V. Srisivani F-ENG College Hostel | Listening to music",
    "8317465934": "NHCE1 Vaishnavi Kolekar F-ENG College Hostel | Bharatanatyam dancer, drawing, listening music",
    "9380658684": "NHCE1 Vikas M-ENG College Hostel | Listening to Keerthana and abhangas",
    "9611248407": "NHCE1 Yuvraj M-ENG Parents | Drawing, badminton",
    "9480344899": "NHCE2 A Amrutha F-ENG College Hostel | Communication skills I love to travel",
    "7259719888": "NHCE2 A Rajeshwari F-ENG College Hostel | dancing, travelling",
    "8095887469": "NHCE2 Adithya Vardhan. Y M-ENG Parents | Reading books",
    "8310925606": "NHCE2 Shankar H Harti M-ENG BCM hostel | Playing games listening songs",
    "9380624563": "NHCE4 S P Vinayaka M-ENG Relatives / Guardian | Talking",
    "8050403417": "Shree Pragna NHCE",
    "7981972023": "Bhavya",
    "9113813710": "Manasa",
    "9686994819": "Shreelakshmi",
    "9381598981": "+919381598981",
    "8897991420": "+918897991420",
    "8050865204": "+918050865204",
    "7019742849": "+917019742849",
    "6364035182": "+916364035182",
    "7483074345": "+917483074345",
    "9113071432": "+919113071432",
    "7483665762": "+917483665762",
    "7259949678": "+917259949678",
    "9742433725": "+919742433725",
    "6381332668": "+916381332668",
    "9345869399": "+919345869399",
    "7899943352": "+917899943352",
    "8500943396": "+918500943396",
    "9902554828": "+919902554828",
    "9113959715": "+919113959715",
    "8310023723": "+918310023723",
}


def clean_cell_value(val: str) -> str:
    """Removes Excel formula formatting like `="val"` and surrounding quotes."""
    val = val.strip()
    if val.startswith("="):
        val = val[1:].strip()
    if val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    return val.strip()


def parse_contacts_csv(csv_path: str | Path) -> Dict[str, str]:
    """Parse contact CSV files and return a dict of {10_digit_phone_number: name}."""
    contacts: Dict[str, str] = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        line_pattern = re.compile(
            r'^(.*?),(=\+?\d+|="?\+?\d+"?|"?\+?\d+"?),\s*"?(true|false)"?,\s*"?(true|false)"?$',
            re.IGNORECASE,
        )
        for line in f:
            line = line.strip()
            if not line or "Phone" in line:
                continue

            match = line_pattern.match(line)
            if match:
                raw_name, raw_phone = match.group(1), match.group(2)
                name = clean_cell_value(raw_name)
                phone = normalize_phone_number(clean_cell_value(raw_phone))
                contacts[phone] = name
            else:
                for row in csv.reader([line]):
                    if len(row) >= 2:
                        name = clean_cell_value(row[0])
                        phone = normalize_phone_number(clean_cell_value(row[1]))
                        contacts[phone] = name

    return contacts

def export_dict_to_csv(contacts_dict, filename="NHCE.csv"):
    """
    Exports a contacts dictionary ({phone: name}) to a CSV file with 2 columns: Name, Phone.

    :param contacts_dict: Dictionary containing {phone: name}
    :param filename: Destination CSV file name or path
    """
    out_path = Path(filename)
    if not out_path.is_absolute() and len(out_path.parts) == 1:
        out_path = Path(__file__).resolve().parent / out_path
    with open(out_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Phone"])
        for phone, name in contacts_dict.items():
            writer.writerow([name, phone])
    print("Successfully exported {} contacts to '{}'".format(len(contacts_dict), out_path))


if __name__ == "__main__":
    print(f"Total unique contacts: {len(CONTACTS)}")
    print("\nSample 10-digit normalized contacts (first 5):")
    for i, (phone, name) in enumerate(CONTACTS.items()):
        if i >= 5:
            break
        print(f"  {phone} : {name}")
    print("\nExporting contacts to CSV...")
    export_dict_to_csv(CONTACTS, "NHCE.csv")
