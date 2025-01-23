# Display the user query
if st.session_state.query:
    with st.chat_message("user"):
        st.markdown(st.session_state.query)

# Display the assistant response
if st.session_state.response:
    with st.chat_message("assistant"):
        st.markdown(st.session_state.response)

        # Add thumbs up/thumbs down feedback
        feedback_col1, feedback_col2 = st.columns(2)
        with feedback_col1:
            thumbs_up = st.button("👍", key="thumbs_up")
        with feedback_col2:
            thumbs_down = st.button("👎", key="thumbs_down")

        if thumbs_up:
            st.session_state.feedback = "Thumbs Up"
            st.success("Thank you for your feedback!")
        elif thumbs_down:
            st.session_state.feedback = "Thumbs Down"
            st.warning("Thank you for your feedback!")
