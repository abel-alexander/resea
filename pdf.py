# Ensure session state stores edited section names
if "edited_long_toc" not in st.session_state:
    st.session_state.edited_long_toc = {
        entry[2]: entry[1] for entry in st.session_state.pdf_long_section_names
    }

# Collapsible editor for modifying section titles
with st.expander("📝 Edit Section Titles", expanded=False):
    for entry in st.session_state.pdf_long_section_names:
        page_no = entry[2]
        section_title = st.session_state.edited_long_toc.get(page_no, entry[1])

        # Inline editable text input for each section
        new_title = st.text_input(f"Page {page_no}:", value=section_title, key=f"edit_long_{page_no}")

        # Update session state on edit
        st.session_state.edited_long_toc[page_no] = new_title  

    # Save changes and refresh dropdown dynamically
    if st.button("✅ Save Changes"):
        st.success("Section names updated!")
        st.rerun()  # Refresh UI to reflect updated names in dropdown

# 🔹 Existing dropdown remains unchanged, but now uses updated names
st.selectbox(
    "Generate a detailed summary",
    options=[st.session_state.edited_long_toc[entry[2]] for entry in st.session_state.pdf_long_section_names],
    index=None,
    key="long_section_name",
    placeholder="...",
    on_change=select_long_section_name  # Existing function remains intact
)
