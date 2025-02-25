# Ensure pdf_toc is stored in session state
if "pdf_toc" not in st.session_state:
    st.session_state.pdf_toc = pdf_toc  # Assuming pdf_toc is already extracted

# Ensure edited titles storage
if "edited_titles" not in st.session_state:
    st.session_state.edited_titles = {}  # Dictionary to store edits

# Collapsible section for editing TOC
with st.expander("Edit Table of Contents"):
    selected_section = st.selectbox(
        "Select a section to edit:",
        options=[(idx, entry[1], entry[2]) for idx, entry in enumerate(st.session_state.pdf_toc)],  
        format_func=lambda x: f"{x[1]} (Page {x[2]})"
    )

    # Extract index and current title
    selected_idx, current_title, page_number = selected_section

    # Editable text input for section title
    new_title = st.text_input("Edit Section Name:", value=current_title)

    # Update the edited title in session state
    if new_title and new_title != current_title:
        st.session_state.edited_titles[selected_idx] = new_title

# Ensure get_name_for_selectbox picks up the edited names
def get_name_for_selectbox():
    return st.session_state.edited_titles.get(selected_idx, st.session_state.pdf_toc[selected_idx][1])  
