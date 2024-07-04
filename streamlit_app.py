import streamlit as st
import os
import time

from backend.apps.database.main import identify_invalid_batches, initialize_database, update_database, read_database, get_labels

from backend.apps.nex.main import insert_or_replace_charstatelabels
from backend.apps.doc.main import convert_document
from backend.apps.prompt.main import build_rag_prompt, build_evaluation_prompt
from backend.apps.langchain.main import get_response, get_eval
from backend.apps.utils.main import get_sanitized_filename
from backend.apps.xml.main import parse_xml, validate_xml, build_character_state_labels

# Layout and file upload
st.title("MorphoBank PBDB PDF to NEXUS File Generator")

st.subheader("Start by Uploading the Document.")
st.write("Please upload the file containing the character list. Ideally I want you to keep the file open side by side to help me with more information that will help me process you request more effeciently")

uploaded_character_list = st.file_uploader("Upload Character List file", type="pdf")

parsing_method_description = st.empty()

st.subheader("Define your Characters")
st.write("""
    Please identify the pages in the document where the character state labels are located? Also, please specify the number of characters and their corresponding states that you'd like me to extract
""")

opt_col1, opt_col2 = st.columns(2)

with opt_col1:
    target_pages = st.text_input("Pages in Range (Inclusive)", placeholder="3-4")

with opt_col2:
    num_characters = st.number_input("Number of Characters", step=int(1))

st.subheader("Upload the Empty NEXUS File")
st.write("Please upload the Nexus file with the missing character state labels that need to be processed.")
uploaded_nexus_file = st.file_uploader("Upload NEXUS File", type="nex")

character_state_view = st.empty()

# Processing

with st.sidebar:
    if st.button("Process NEXUS file"):

        start_time = time.time()

        attempt = 0
        max_attempts = 5

        filename, file_extension = os.path.splitext(uploaded_character_list.name)

        process_name = get_sanitized_filename(filename)

        with st.status("Processing...", expanded=True) as status:

            st.write("Parsing Character List...")
            raw_characters = convert_document(uploaded_character_list, target_pages)

            #elif file_extension == ".docx" or ".doc":
                #st.write("Parsing Docs...")
                #raw_characterstatelabels = parse_docx(uploaded_character_list)

            initialize_database(process_name, raw_characters, num_characters)

            while attempt < max_attempts:

                batches = identify_invalid_batches(process_name)
                if not batches:  # If batches is empty, break the loop
                    break

                try: 
                    if attempt == 0: st.write("Preparing Data Batches...")
                    elif attempt == 1 : st.write("Reattempting Failed Batches")

                    context = read_database(process_name, batches, column_name="context")
                    prompt = read_database(process_name, batches, column_name="prompt")

                    if attempt == 0: 
                        st.write("Querying Language Model...")
                    rag_prompt = build_rag_prompt(context, prompt)
                    response = get_response(rag_prompt) 
                    
                    if attempt == 0: 
                        st.write("Validating and Evaluating Response...")
                    xml_characters = parse_xml(response)
                    update_database(process_name, batches, xml_characters, column_name="xml_characters")
                    
                    validation_status = validate_xml(batches, xml_characters)
                    update_database(process_name, batches, validation_status, column_name="validation_status")

                    evaluation_prompt = build_evaluation_prompt(prompt, xml_characters, context)
                    evaluation_status = get_eval(evaluation_prompt)
                    update_database(process_name, batches, evaluation_status, column_name="evaluation_status")
                
                except Exception as e:
                    st.write(f"Reattempting as it raised an internal error.")
                    continue

                attempt += 1

            if attempt == max_attempts:
                # Check if there are still invalid batches
                remaining_batches = identify_invalid_batches(process_name)
                if remaining_batches:
                    st.write("Incomplete Characters Extracted...")
                else:  
                    st.write("Character Extraction Complete!")

            characterstatelabels_xml = get_labels(process_name)

            characterstatelabels = build_character_state_labels(characterstatelabels_xml)

            st.write("Adding Characters to Nexus File...")
            updated_nexus_file = insert_or_replace_charstatelabels(uploaded_nexus_file, characterstatelabels)

            end_time = time.time()
            total_time = str(round((end_time-start_time),1))

            if attempt == max_attempts:
                # Check if there are still invalid batches
                remaining_batches = identify_invalid_batches(process_name)
                if remaining_batches:
                    status.update(label="Processing incomplete.", state="complete", expanded=True)
                    character_state_view.warning(f"Please review the following characters. {remaining_batches}")
            else:  
                status.update(label="Processing complete! Your NEXUS file is ready.", state="complete", expanded=False)

        # Create a download button

        st.info(f"Finished in {total_time} seconds")

        download_button = st.download_button(
            label="Download the updated NEXUS File",
            data=updated_nexus_file,
            file_name=process_name + ".nex",
        )