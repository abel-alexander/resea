# Ensure session state for edited ToC exists
if "edited_long_toc" not in st.session_state:
    st.session_state.edited_long_toc = {
        entry[2]: entry[1] for entry in st.session_state.pdf_long_section_names
    }

st.subheader("📝 Edit Detailed Summary Sections")

# Create an editable text area inside an expander
with st.expander("Edit section names for detailed summary", expanded=False):
    edited_text = ""
    
    for entry in st.session_state.pdf_long_section_names:
        page_no = entry[2]
        section_title = st.session_state.edited_long_toc.get(page_no, entry[1])
        
        new_title = st.text_input(f"Page {page_no}:", value=section_title, key=f"edit_long_{page_no}")
        st.session_state.edited_long_toc[page_no] = new_title  # Update session state dynamically

    if st.button("✅ Save Changes"):
        st.success("Section names updated!")
        st.rerun()  # Refresh to reflect updates in dropdown

# Dropdown for detailed summary selection (updated dynamically)
selected_long_section = st.selectbox(
    "Generate a detailed summary",
    options=[st.session_state.edited_long_toc[entry[2]] for entry in st.session_state.pdf_long_section_names],
    index=None,
    key="long_section_name"
)
