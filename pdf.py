# Ensure session state stores the edited ToC
if "edited_toc" not in st.session_state:
    st.session_state.edited_toc = {entry[2]: entry[1] for entry in st.session_state.pdf_toc}

st.subheader("✏️ Edit Section Titles")

# Select a section to edit
selected_section = st.selectbox(
    "Select a section to rename:",
    options=[st.session_state.edited_toc[entry[2]] for entry in st.session_state.pdf_toc],
    index=None,
    key="selected_section_editor"
)

# Find the corresponding page number
selected_page_no = next(entry[2] for entry in st.session_state.pdf_toc if st.session_state.edited_toc[entry[2]] == selected_section)

# Editable text input for renaming the selected section
new_title = st.text_input("Edit section name:", value=selected_section, key="edit_section_title")

# Update section name and refresh UI when the button is clicked
if st.button("✅ Update Section Name"):
    st.session_state.edited_toc[selected_page_no] = new_title
    st.rerun()  # Instantly refresh dropdowns with the updated name
