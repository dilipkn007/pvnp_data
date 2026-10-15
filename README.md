# PVND Data Management

Project repository for managing contact directories, trip participant CSV exports, and volunteer registration test automations.

---

## 📁 Directory Structure

```text
PVND_DATA/
├── data/                    # Exported contact and trip participant CSV files
│   ├── chennai_jaipur_jaipur_vrindavan_trip_16_10_2026.csv
│   ├── chennai_jaipur_trip_16_10_2026.csv
│   ├── gscj_gsj_gss.csv
│   ├── jagannath_puri_dham_25_12_2026.csv
│   ├── pune_hkvalley_trip_2026.csv
│   ├── vrindavan_trip_19_10_2026.csv
│   └── vyasa_puja_offering.csv
│
├── nhce_contacts/           # NHCE contacts dataset and utility script
│   ├── __init__.py
│   ├── contacts.py          # NHCE phone normalization and CSV export
│   ├── 08102026.csv
│   ├── NHCE.csv
│   ├── contacts.csv
│   └── core.csv
│
├── reports/                 # Test validation reports (Markdown, CSV, JSON)
│   ├── volunteer_registration_report.csv
│   ├── volunteer_registration_report.json
│   └── volunteer_registration_report.md
│
├── scripts/                 # Core processing and test automation scripts
│   ├── __init__.py
│   ├── mobile_dict.py       # Master contact dictionaries and trip groupings
│   └── test_volunteer_registration.py # Volunteer registration E2E validation suite
│
├── app.py                   # Streamlit Interactive Web Application
└── README.md                # Project documentation
```

---

## 🚀 Usage

### 1. Interactive Streamlit Web UI (Preview & Export)
Launch the web interface for filtering, previewing, and downloading contact lists in CSV and Excel:
```bash
streamlit run app.py
```
*Access the app in your browser at `http://localhost:8501`.*

### 2. Generating Contact Exports
To generate and update trip participant lists or contact CSV files in `data/`:
```bash
python3 scripts/mobile_dict.py
```
*Exports are automatically saved to the `data/` directory.*

### 2. Running Volunteer Registration Validation
To validate volunteer registrations using Playwright or API mode:
```bash
# E2E Browser mode (default dictionary: folk_internal)
python3 scripts/test_volunteer_registration.py --mode browser

# Specify custom dictionary from mobile_dict (e.g. pvnp_contacts, hknf)
python3 scripts/test_volunteer_registration.py --dict pvnp_contacts --mode browser

# Run in headless or headed mode
python3 scripts/test_volunteer_registration.py --headed
```
*Generated reports (Markdown, CSV, JSON) are automatically saved to `reports/`.*

### 3. NHCE Contacts Utility
To process NHCE contacts:
```bash
python3 nhce_contacts/contacts.py
```
*Exports are saved to `nhce_contacts/NHCE.csv`.*
