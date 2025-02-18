import streamlit as st
import fitz  # PyMuPDF

def extract_hyperlinked_toc(doc):
    """
    Extracts a Table of Contents (ToC) from a PDF by detecting hyperlinks and their associated text.
    Uses bounding box detection and falls back on get_toc() if necessary.
    """
    plst = []  # Final structured output
    unique_entries = set()  # To prevent duplicates
    section_counter = ord('A')  # Counter for unknown sections
    id_counter = 1

    # Check pages 1 → 2 → 3 for more than 3 hyperlinks
    selected_page = None
    for page_num in range(3):
        page = doc[page_num]
        links = page.get_links()
        if len(links) > 3:
            selected_page = page_num
            break

    if selected_page is None:
        st.warning("No page with more than 3 hyperlinks found. No ToC generated.")
        return []

    st.success(f"Using Page {selected_page + 1} for ToC extraction.")

    # Extract text blocks from the selected page
    selected_page_obj = doc[selected_page]
    links = selected_page_obj.get_links()
    text_blocks = selected_page_obj.get_text("blocks")

    # Extract inbuilt ToC as a fallback
    toc_dict = {entry[2]: entry[1] for entry in doc.get_toc(simple=True) if entry[2] > 0}

    for link in links:
        if "page" in link and isinstance(link["page"], int):
            destination_page = link["page"] + 1  # Convert to 1-indexed
        else:
            continue  # Skip invalid links

        link_rect = fitz.Rect(link["from"])  # Hyperlink bounding box
        expanded_rect = link_rect + (-5, -2, 5, 2)  # Expand for better text capture

        matched_text = None
        min_distance = float("inf")

        # Find the closest text block overlapping the link
        for block in text_blocks:
            text_rect = fitz.Rect(block[:4])
            if expanded_rect.intersects(text_rect):
                distance = abs(link_rect.y0 - text_rect.y0)
                if distance < min_distance:
                    matched_text = block[4].strip()
                    min_distance = distance

        # Use inbuilt ToC as a fallback if no matched text found
        if not matched_text:
            matched_text = toc_dict.get(destination_page, f"Unknown Section {chr(section_counter)}")
            section_counter += 1 if "Unknown Section" in matched_text else 0

        # Avoid duplicates
        entry_key = (matched_text, destination_page)
        if entry_key in unique_entries:
            continue
        unique_entries.add(entry_key)

        # Append to plst
        plst.append({
            "id": id_counter,
            "lvl": 1,
            "title": matched_text,
            "pno_from": destination_page,
            "pno_to": destination_page  # Will adjust later
        })
        id_counter += 1

    # Ensure `pno_to` follows hyperlink order
    plst = sorted(plst, key=lambda x: x["pno_from"])  # Sort in order of pno_from

    for i in range(len(plst) - 1):
        plst[i]["pno_to"] = plst[i + 1]["pno_from"] - 1  # Assign next section's start - 1

    # Ensure the last section spans till the last page
    if plst:
        plst[-1]["pno_to"] = doc.page_count

    return plst

# Streamlit UI
st.title("PDF Table of Contents Extractor (Hyperlink-based & Editable)")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        toc = extract_hyperlinked_toc(doc)

        if toc:
            st.subheader("Extracted Table of Contents")

            # Store editable ToC in session state
            if "edited_toc" not in st.session_state:
                st.session_state.edited_toc = {entry["id"]: entry["title"] for entry in toc}

            # Dropdown to select a section
            section_titles = [f"{entry['title']} (Page {entry['pno_from']}-{entry['pno_to']})" for entry in toc]
            selected_section = st.selectbox("Select a section to edit:", section_titles)

            # Find the corresponding section
            for entry in toc:
                if selected_section.startswith(entry["title"]):
                    section_id = entry["id"]
                    break

            # Editable text input
            new_title = st.text_input("Edit Section Name:", st.session_state.edited_toc[section_id])

            # Update session state when edited
            if st.button("Save Changes"):
                st.session_state.edited_toc[section_id] = new_title
                st.success("Section name updated successfully!")

            # Display the updated ToC
            st.subheader("Updated Table of Contents")
            for entry in toc:
                edited_title = st.session_state.edited_toc[entry["id"]]
                st.write(f"**{edited_title}** (Page {entry['pno_from']}-{entry['pno_to']})")

# import streamlit as st
# import fitz  # PyMuPDF
#
# def extract_hyperlinked_toc(doc):
#     """
#     Extracts a Table of Contents (ToC) from a PDF by detecting hyperlinks and their associated text.
#     Uses bounding box detection and falls back on get_toc() if necessary.
#     """
#     plst = []  # Final structured output
#     unique_entries = set()  # To prevent duplicates
#     section_counter = ord('A')  # Counter for unknown sections
#     id_counter = 1
#
#     # Check pages 1 → 2 → 3 for more than 3 hyperlinks
#     selected_page = None
#     for page_num in range(3):
#         page = doc[page_num]
#         links = page.get_links()
#         if len(links) > 3:
#             selected_page = page_num
#             break
#
#     if selected_page is None:
#         st.warning("No page with more than 3 hyperlinks found. No ToC generated.")
#         return []
#
#     st.success(f"Using Page {selected_page + 1} for ToC extraction.")
#
#     # Extract text blocks from the selected page
#     selected_page_obj = doc[selected_page]
#     links = selected_page_obj.get_links()
#     text_blocks = selected_page_obj.get_text("blocks")
#
#     # Extract inbuilt ToC as a fallback
#     toc_dict = {entry[2]: entry[1] for entry in doc.get_toc(simple=True) if entry[2] > 0}
#
#     for link in links:
#         if "page" in link and isinstance(link["page"], int):
#             destination_page = link["page"] + 1  # Convert to 1-indexed
#         else:
#             continue  # Skip invalid links
#
#         link_rect = fitz.Rect(link["from"])  # Hyperlink bounding box
#         expanded_rect = link_rect + (-5, -2, 5, 2)  # Expand for better text capture
#
#         matched_text = None
#         min_distance = float("inf")
#
#         # Find the closest text block overlapping the link
#         for block in text_blocks:
#             text_rect = fitz.Rect(block[:4])
#             if expanded_rect.intersects(text_rect):
#                 distance = abs(link_rect.y0 - text_rect.y0)
#                 if distance < min_distance:
#                     matched_text = block[4].strip()
#                     min_distance = distance
#
#         # Use inbuilt ToC as a fallback if no matched text found
#         if not matched_text:
#             matched_text = toc_dict.get(destination_page, f"Unknown Section {chr(section_counter)}")
#             section_counter += 1 if "Unknown Section" in matched_text else 0
#
#         # Avoid duplicates
#         entry_key = (matched_text, destination_page)
#         if entry_key in unique_entries:
#             continue
#         unique_entries.add(entry_key)
#
#         # Append to plst
#         plst.append({
#             "id": id_counter,
#             "lvl": 1,
#             "title": matched_text,
#             "pno_from": destination_page,
#             "pno_to": destination_page  # Will adjust later
#         })
#         id_counter += 1
#
#     # Ensure `pno_to` follows hyperlink order
#     plst = sorted(plst, key=lambda x: x["pno_from"])  # Sort in order of pno_from
#
#     for i in range(len(plst) - 1):
#         plst[i]["pno_to"] = plst[i + 1]["pno_from"] - 1  # Assign next section's start - 1
#
#     # Ensure the last section spans till the last page
#     if plst:
#         plst[-1]["pno_to"] = doc.page_count
#
#     return plst
#
# # Streamlit UI
# st.title("PDF Table of Contents Extractor (Hyperlink-based)")
#
# uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
#
# if uploaded_file is not None:
#     with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
#         toc = extract_hyperlinked_toc(doc)
#
#         if toc:
#             st.subheader("Extracted Table of Contents")
#
#             for entry in toc:
#                 with st.expander(f"{entry['title']} (Page {entry['pno_from']}-{entry['pno_to']})"):
#                     st.write(f"**Section ID:** {entry['id']}")
#                     st.write(f"**Title:** {entry['title']}")
#                     st.write(f"**Page Range:** {entry['pno_from']} - {entry['pno_to']}")
