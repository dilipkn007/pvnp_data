import io
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Check optional Excel export support
try:
    import openpyxl  # noqa: F401
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import data source
try:
    import mobile_dict
except Exception as e:
    st.error(f"Error importing mobile_dict: {e}")
    st.stop()

# Optional NHCE contacts import
nhce_contacts_dict = {}
try:
    from nhce_contacts.contacts import CONTACTS as NHCE_CONTACTS
    nhce_contacts_dict = NHCE_CONTACTS
except Exception:
    pass

# Page configuration
st.set_page_config(
    page_title="PVND Contact Management Hub",
    page_icon="📇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.9rem;
        font-weight: 700;
        color: #1f2937;
    }
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .main-header p {
        color: #e0e7ff;
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #ede9fe;
        color: #6d28d9;
        margin-right: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_categories():
    """Build and return all available contact categories with metadata."""
    combined_gscj_gsj_gss = getattr(mobile_dict, "gscj", {}) | getattr(mobile_dict, "gsj", {}) | getattr(mobile_dict, "gss", {})
    categories = {
        "Master Contacts": {
            "dict": getattr(mobile_dict, "master_contacts", {}),
            "group": "Primary Lists",
            "desc": "Complete master repository of contacts",
            "slug": "master_contacts",
        },
        "PVNP Contacts": {
            "dict": getattr(mobile_dict, "pvnp_contacts", {}),
            "group": "Primary Lists",
            "desc": "PVNP active contacts union",
            "slug": "pvnp_contacts",
        },
        "Vyasa Puja Offering": {
            "dict": getattr(mobile_dict, "vyasa_puja_offering", {}),
            "group": "Primary Lists",
            "desc": "Filtered contacts for Vyasa Puja offering (excluding internal groups)",
            "slug": "vyasa_puja_offering",
        },
        "Jagannath Puri Dham (25-12-2026)": {
            "dict": getattr(mobile_dict, "jagannath_puri_dham_25_12_2026", {}),
            "group": "Trips & Yatras",
            "desc": "Jagannath Puri Dham trip list",
            "slug": "jagannath_puri_dham_25_12_2026",
        },
        "Pune HK Valley Trip (2026)": {
            "dict": getattr(mobile_dict, "pune_hkvalley_trip_2026", {}),
            "group": "Trips & Yatras",
            "desc": "Pune Hare Krishna Valley trip list",
            "slug": "pune_hkvalley_trip_2026",
        },
        "Chennai - Jaipur Trip (16-10-2026)": {
            "dict": getattr(mobile_dict, "chennai_jaipur_trip_16_10_2026", {}),
            "group": "Trips & Yatras",
            "desc": "Chennai to Jaipur trip list",
            "slug": "chennai_jaipur_trip_16_10_2026",
        },
        "Vrindavan Trip (19-10-2026)": {
            "dict": getattr(mobile_dict, "vrindavan_trip_19_10_2026", {}),
            "group": "Trips & Yatras",
            "desc": "Vrindavan trip list",
            "slug": "vrindavan_trip_19_10_2026",
        },
        "Chennai + Jaipur + Vrindavan Combined": {
            "dict": getattr(mobile_dict, "chennai_jaipur_jaipur_vrindavan_trip_16_10_2026", {}),
            "group": "Trips & Yatras",
            "desc": "Combined Chennai, Jaipur and Vrindavan trip members",
            "slug": "chennai_jaipur_jaipur_vrindavan_trip_16_10_2026",
        },
        "Folk Internal": {
            "dict": getattr(mobile_dict, "folk_internal", {}),
            "group": "Internal & Sevaks",
            "desc": "Folk Internal core team members",
            "slug": "folk_internal",
        },
        "HKNF Contacts": {
            "dict": getattr(mobile_dict, "hknf", {}),
            "group": "Internal & Sevaks",
            "desc": "Hare Krishna Navodaya Foundation contacts",
            "slug": "hknf",
        },
        "GSCJ, GSJ & GSS Combined": {
            "dict": combined_gscj_gsj_gss,
            "group": "Internal & Sevaks",
            "desc": "Combined GSCJ, GSJ, and GSS team members",
            "slug": "gscj_gsj_gss_combined",
        },
        "GSCJ": {
            "dict": getattr(mobile_dict, "gscj", {}),
            "group": "Internal & Sevaks",
            "desc": "GSCJ team contacts",
            "slug": "gscj",
        },
        "GSJ": {
            "dict": getattr(mobile_dict, "gsj", {}),
            "group": "Internal & Sevaks",
            "desc": "GSJ team contacts",
            "slug": "gsj",
        },
        "GSS": {
            "dict": getattr(mobile_dict, "gss", {}),
            "group": "Internal & Sevaks",
            "desc": "GSS team contacts",
            "slug": "gss",
        },
        "GSCS": {
            "dict": getattr(mobile_dict, "gscs", {}),
            "group": "Internal & Sevaks",
            "desc": "GSCS team contacts",
            "slug": "gscs",
        },
        "GS Core": {
            "dict": getattr(mobile_dict, "gs_core", {}),
            "group": "Internal & Sevaks",
            "desc": "GS Core leadership contact",
            "slug": "gs_core",
        },
        "SKJ 2026 (All)": {
            "dict": getattr(mobile_dict, "SKJ_2026", {}),
            "group": "SKJ 2026",
            "desc": "Total registered contacts for SKJ 2026",
            "slug": "skj_2026_all",
        },
        "SKJ 2026 Attendees": {
            "dict": getattr(mobile_dict, "SKJ_2026_attendies", {}),
            "group": "SKJ 2026",
            "desc": "SKJ 2026 confirmed attendees",
            "slug": "skj_2026_attendees",
        },
        "SKJ 2026 Absentees": {
            "dict": getattr(mobile_dict, "SKJ_2026_absentice", {}),
            "group": "SKJ 2026",
            "desc": "SKJ 2026 absentees list",
            "slug": "skj_2026_absentees",
        },
    }

    if nhce_contacts_dict:
        categories["NHCE Contacts"] = {
            "dict": nhce_contacts_dict,
            "group": "College / External",
            "desc": "New Horizon College of Engineering normalized contacts",
            "slug": "nhce_contacts",
        }

    return categories


def dict_to_dataframe(contacts_dict: dict) -> pd.DataFrame:
    """Convert phone->name dictionary to a clean, sorted DataFrame."""
    if not contacts_dict:
        return pd.DataFrame(columns=["Phone Number", "Name"])

    rows = [{"Phone Number": str(k).strip(), "Name": str(v).strip()} for k, v in contacts_dict.items()]
    df = pd.DataFrame(rows)
    # Sort alphabetically by Name
    df = df.sort_values(by="Name", ascending=True).reset_index(drop=True)
    df.index = df.index + 1  # 1-based indexing for display
    return df


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Export DataFrame to UTF-8 CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame, sheet_name="Contacts") -> bytes:
    """Export single DataFrame to styled Excel bytes using openpyxl."""
    if not HAS_OPENPYXL:
        raise ImportError("openpyxl is required for Excel export. Please install it with: pip install openpyxl")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        # Auto-adjust column widths
        worksheet = writer.sheets[sheet_name[:31]]
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 14)
    return output.getvalue()


def to_multi_sheet_excel(categories: dict) -> bytes:
    """Export all categories into a single multi-sheet Excel file."""
    if not HAS_OPENPYXL:
        raise ImportError("openpyxl is required for Excel export. Please install it with: pip install openpyxl")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for cat_name, data in categories.items():
            df = dict_to_dataframe(data["dict"])
            # Excel sheet names max 31 chars and no invalid chars
            safe_sheet_name = cat_name.replace("/", "-").replace(":", "-")[:31]
            df.to_excel(writer, index=False, sheet_name=safe_sheet_name)
            worksheet = writer.sheets[safe_sheet_name]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 14)
    return output.getvalue()


# Main Application
def main():
    categories = get_categories()

    # Sidebar
    st.sidebar.title("📇 PVND Contacts")
    st.sidebar.caption("Browse, filter, and export contacts")

    # Group filtering in sidebar
    groups = ["All Groups"] + sorted(list({data["group"] for data in categories.values()}))
    selected_group = st.sidebar.selectbox("Filter by Category Group", groups)

    if selected_group == "All Groups":
        filtered_cat_names = list(categories.keys())
    else:
        filtered_cat_names = [k for k, v in categories.items() if v["group"] == selected_group]

    selected_category_name = st.sidebar.selectbox(
        "Select Category to View",
        filtered_cat_names,
        index=0,
    )

    cat_info = categories[selected_category_name]
    raw_dict = cat_info["dict"]
    slug = cat_info["slug"]

    # Sidebar Quick Stats
    st.sidebar.divider()
    st.sidebar.markdown(f"**Current Category:** {selected_category_name}")
    st.sidebar.markdown(f"**Group:** `{cat_info['group']}`")
    st.sidebar.markdown(f"**Total Records:** `{len(raw_dict):,}`")

    # Master size comparison
    master_total = len(categories.get("Master Contacts", {}).get("dict", {}))
    if master_total > 0 and selected_category_name != "Master Contacts":
        ratio = (len(raw_dict) / master_total) * 100
        st.sidebar.markdown(f"**% of Master:** `{ratio:.1f}%`")

    st.sidebar.divider()
    # Bulk Export in Sidebar
    st.sidebar.subheader("📦 Bulk Export")
    if st.sidebar.button("Prepare All-in-One Excel Workbook", width="stretch"):
        if not HAS_OPENPYXL:
            st.sidebar.error("Excel export requires `openpyxl`. Please add it to `requirements.txt`.")
        else:
            with st.spinner("Generating multi-sheet Excel file..."):
                multi_excel_bytes = to_multi_sheet_excel(categories)
                st.sidebar.download_button(
                    label="📥 Download All Categories (.xlsx)",
                    data=multi_excel_bytes,
                    file_name="PVND_All_Categories_Contacts.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                )

    # Main Tabs
    tab_preview, tab_compare, tab_overview = st.tabs(["📋 Preview & Download", "⚖️ Compare Categories", "📊 All Categories Overview"])

    # TAB 1: Preview & Download
    with tab_preview:
        # Header banner
        st.markdown(
            f"""
            <div class="main-header">
                <span class="badge-pill">{cat_info['group']}</span>
                <h1>{selected_category_name}</h1>
                <p>{cat_info['desc']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        df = dict_to_dataframe(raw_dict)

        # Filters Row
        col_search, col_stats = st.columns([2, 1])
        with col_search:
            search_query = st.text_input(
                "🔍 Search by Name or Mobile Number:",
                placeholder="Type name or digits...",
                help="Filters results in real time as you type",
            )

        # Apply search filter
        if search_query:
            query = search_query.strip().lower()
            filtered_df = df[
                df["Name"].str.lower().str.contains(query, na=False)
                | df["Phone Number"].str.contains(query, na=False)
            ].copy()
        else:
            filtered_df = df.copy()

        # Metrics display
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total in Category", f"{len(df):,}")
        with col_m2:
            st.metric("Filtered Matches", f"{len(filtered_df):,}")
        with col_m3:
            st.metric("Unique Numbers", f"{filtered_df['Phone Number'].nunique():,}")
        with col_m4:
            pct_filtered = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0
            st.metric("Showing Percentage", f"{pct_filtered:.1f}%")

        # Download buttons row
        st.markdown("### 💾 Export Options")
        col_dl1, col_dl2, col_dl3 = st.columns(3)

        csv_data = to_csv_bytes(filtered_df)

        with col_dl1:
            st.download_button(
                label=f"📥 Download CSV ({len(filtered_df)} contacts)",
                data=csv_data,
                file_name=f"{slug}.csv",
                mime="text/csv",
                width="stretch",
            )

        with col_dl2:
            if HAS_OPENPYXL:
                excel_data = to_excel_bytes(filtered_df, sheet_name=selected_category_name)
                st.download_button(
                    label=f"📊 Download Excel ({len(filtered_df)} contacts)",
                    data=excel_data,
                    file_name=f"{slug}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                )
            else:
                st.button(
                    label="📊 Excel export unavailable",
                    disabled=True,
                    help="openpyxl is not installed. Add openpyxl to requirements.txt",
                    width="stretch",
                )

        with col_dl3:
            # Full category download (unfiltered) if search is active
            if search_query:
                full_csv = to_csv_bytes(df)
                st.download_button(
                    label=f"⬇️ Download Full CSV ({len(df)} all)",
                    data=full_csv,
                    file_name=f"{slug}_full.csv",
                    mime="text/csv",
                    width="stretch",
                )

        st.divider()

        # Interactive Data Preview
        st.subheader("👁️ Contacts Preview")
        if filtered_df.empty:
            st.info("No contacts match the search query.")
        else:
            st.dataframe(
                filtered_df,
                width="stretch",
                height=520,
                column_config={
                    "Phone Number": st.column_config.TextColumn("Phone Number", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="large"),
                },
            )

    # TAB 2: Compare Categories
    with tab_compare:
        st.subheader("⚖️ Category Set Operations & Overlap")
        st.markdown("Find overlapping contacts, unique attendees, or calculate differences between any two groups.")

        cat_keys = list(categories.keys())
        default_a_idx = cat_keys.index("Jagannath Puri Dham (25-12-2026)") if "Jagannath Puri Dham (25-12-2026)" in cat_keys else 0
        default_b_idx = cat_keys.index("Chennai - Jaipur Trip (16-10-2026)") if "Chennai - Jaipur Trip (16-10-2026)" in cat_keys else 1

        col_cat_a, col_cat_b = st.columns(2)
        with col_cat_a:
            cat_a_name = st.selectbox("Select Category A:", cat_keys, index=default_a_idx, key="cat_a")
        with col_cat_b:
            cat_b_name = st.selectbox("Select Category B:", cat_keys, index=default_b_idx, key="cat_b")

        dict_a = categories[cat_a_name]["dict"]
        dict_b = categories[cat_b_name]["dict"]

        set_a = set(dict_a.keys())
        set_b = set(dict_b.keys())

        intersection_keys = set_a & set_b
        only_in_a_keys = set_a - set_b
        only_in_b_keys = set_b - set_a
        union_keys = set_a | set_b

        # Primary Metrics Row (Total A, Total B, Overlap, Union)
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.metric(label=f"Total in {cat_a_name}", value=f"{len(set_a):,}")
        with col_c2:
            st.metric(label=f"Total in {cat_b_name}", value=f"{len(set_b):,}")
        with col_c3:
            overlap_pct_b = (len(intersection_keys) / len(set_b) * 100) if set_b else 0
            st.metric(label="Common in Both (A ∩ B)", value=f"{len(intersection_keys):,}", delta=f"{overlap_pct_b:.0f}% of {cat_b_name}")
        with col_c4:
            st.metric(label="Total Combined (Union)", value=f"{len(union_keys):,}")

        # Unique / Differences Breakdown Banner
        if len(only_in_b_keys) == 0 and len(set_b) > 0:
            st.info(f"💡 **100% Inclusion:** All **{len(set_b)}** contacts in **{cat_b_name}** are also present in **{cat_a_name}** (Overlap = {len(intersection_keys)}, Unique to {cat_b_name} only = 0).")
        elif len(only_in_a_keys) == 0 and len(set_a) > 0:
            st.info(f"💡 **100% Inclusion:** All **{len(set_a)}** contacts in **{cat_a_name}** are also present in **{cat_b_name}** (Overlap = {len(intersection_keys)}, Unique to {cat_a_name} only = 0).")
        else:
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                st.caption(f"📌 Unique to **{cat_a_name}** only (not in {cat_b_name}): **{len(only_in_a_keys)}**")
            with col_u2:
                st.caption(f"📌 Unique to **{cat_b_name}** only (not in {cat_a_name}): **{len(only_in_b_keys)}**")

        st.markdown("#### 🔍 Select Subset to Preview & Download")
        op_choice = st.radio(
            "Choose view:",
            [
                f"All in '{cat_b_name}' ({len(set_b)} contacts)",
                f"All in '{cat_a_name}' ({len(set_a)} contacts)",
                f"Shared in Both ({len(intersection_keys)} contacts)",
                f"Unique to '{cat_a_name}' only ({len(only_in_a_keys)} contacts)",
                f"Unique to '{cat_b_name}' only ({len(only_in_b_keys)} contacts)",
                f"Combined Union ({len(union_keys)} contacts)",
            ],
            horizontal=False,
        )

        # Build dictionary for selected subset
        if op_choice.startswith(f"All in '{cat_b_name}'"):
            subset_dict = dict_b
            subset_filename = f"{categories[cat_b_name]['slug']}_all"
        elif op_choice.startswith(f"All in '{cat_a_name}'"):
            subset_dict = dict_a
            subset_filename = f"{categories[cat_a_name]['slug']}_all"
        elif "Shared in Both" in op_choice:
            subset_dict = {k: dict_a[k] for k in intersection_keys}
            subset_filename = "shared_overlap"
        elif "Unique to '" + cat_a_name in op_choice:
            subset_dict = {k: dict_a[k] for k in only_in_a_keys}
            subset_filename = f"unique_to_{categories[cat_a_name]['slug']}"
        elif "Unique to '" + cat_b_name in op_choice:
            subset_dict = {k: dict_b[k] for k in only_in_b_keys}
            subset_filename = f"unique_to_{categories[cat_b_name]['slug']}"
        else:
            subset_dict = {**dict_b, **dict_a}
            subset_filename = "combined_union"

        subset_df = dict_to_dataframe(subset_dict)

        col_comp_dl1, col_comp_dl2 = st.columns(2)
        with col_comp_dl1:
            st.download_button(
                label=f"📥 Download Result as CSV ({len(subset_df)} contacts)",
                data=to_csv_bytes(subset_df),
                file_name=f"{subset_filename}.csv",
                mime="text/csv",
                width="stretch",
            )
        with col_comp_dl2:
            if HAS_OPENPYXL:
                st.download_button(
                    label=f"📊 Download Result as Excel ({len(subset_df)} contacts)",
                    data=to_excel_bytes(subset_df, sheet_name="Comparison_Result"),
                    file_name=f"{subset_filename}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                )
            else:
                st.button(
                    label="📊 Excel export unavailable",
                    disabled=True,
                    help="openpyxl is not installed. Add openpyxl to requirements.txt",
                    width="stretch",
                )

        st.dataframe(subset_df, width="stretch", height=400)

    # TAB 3: All Categories Overview
    with tab_overview:
        st.subheader("📊 Summary of All Categories")

        summary_rows = []
        for name, data in categories.items():
            summary_rows.append({
                "Category Name": name,
                "Group": data["group"],
                "Total Contacts": len(data["dict"]),
                "Description": data["desc"],
                "Export Slug": data["slug"],
            })

        summary_df = pd.DataFrame(summary_rows)
        summary_df = summary_df.sort_values(by="Total Contacts", ascending=False).reset_index(drop=True)
        summary_df.index = summary_df.index + 1

        st.dataframe(
            summary_df,
            width="stretch",
            height=500,
            column_config={
                "Total Contacts": st.column_config.NumberColumn("Total Contacts", format="%d"),
            },
        )


if __name__ == "__main__":
    main()
