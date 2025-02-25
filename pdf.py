st.subheader("📄 PDF Table of Contents (Editable)")

# Ensure session state stores the editable ToC
if "edited_toc" not in st.session_state:
    st.session_state.edited_toc = {
        entry[2]: entry[1] for entry in st.session_state.pdf_toc
    }

# Step 1: Display and allow edits
with st.expander("📝 Edit ToC Before Using Dropdown", expanded=True):
    for entry in st.session_state.pdf_toc:
        page_no = entry[2]
        section_title = st.session_state.edited_toc.get(page_no, entry[1])

        # Inline text input for each section
        new_title = st.text_input(f"Page {page_no}:", value=section_title, key=f"edit_toc_{page_no}")

        # Update session state with new titles
        st.session_state.edited_toc[page_no] = new_title  

    # Step 2: Save changes and confirm before passing to dropdown
    if st.button("✅ Save ToC Changes"):
        st.success("ToC updated successfully! Proceeding to dropdown.")
        st.session_state.final_toc = list(st.session_state.edited_toc.values())  # Store final version

# Step 3: Display the dropdown only after editing is done
if "final_toc" in st.session_state:
    st.subheader("📌 Select Section from Updated ToC")
    selected_section = st.selectbox(
        "Choose a section:",
        options=st.session_state.final_toc,
        index=None,
        key="selected_section"
    )
