import streamlit as st
import pandas as pd
import os
from src.client import GoogleAPIClient
from src.processors import XParkyProcessor, CertificateProcessor
from googleapiclient.http import MediaIoBaseDownload
import io
from PIL import Image
from dotenv import load_dotenv

def init_streamlit():
    """Initialize Streamlit page configuration and styling"""
    st.set_page_config(
        page_title="Student Portal",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Custom styling
    st.markdown("""
        <style>
        /* Font */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

        *, *::before, *::after {
            font-family: 'Poppins', sans-serif;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            font-size: 24px;
            margin: 0;
            width: 100%;
        }

        /* Hide unnecessary elements */
        button[title="View fullscreen"] { visibility: hidden; }
        .reportview-container { margin-top: -2em; }
        #MainMenu { visibility: hidden; }
        .stDeployButton { display: none; }
        footer { visibility: hidden; }
        #stDecoration { display: none; }

        /* Search container */
        .search-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
                
        /* Progress bar color */
        .stProgress > div > div > div {
            background-color: #4284f2 !important;
        }

        /* Certificate container */
        .certificate-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

def load_config():
    """Load and validate environment variables"""
    load_dotenv()

    config = {
        'credentials_path': st.secrets["GOOGLE_CREDENTIALS"],
        'credentials': st.secrets["GOOGLE_CREDENTIALS"],
        'classroom_folder_id': st.secrets["CLASSROOM_FOLDER_ID"],
        'eval_forms_folder_id': st.secrets["EVAL_FORMS_FOLDER_ID"],
        'certificates_main_folder_id': st.secrets['CERTIFICATES_FOLDER_ID']  # Main Certificates folder ID
    }
    
    if missing_vars := [key for key, value in config.items() if not value]:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}")
        st.stop()
    
    return config
def fetch_data(config):
    """Fetch and process XParky data"""
    try:
        with st.spinner('Loading data...'):
            credentials = service_account.Credentials.from_service_account_info(
                config['credentials'],
                scopes=['https://www.googleapis.com/auth/drive.readonly',
                       'https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            client = GoogleAPIClient(credentials)  
            processor = XParkyProcessor(client)
            
            final_df, _, _ = processor.process_all_data(
                config['classroom_folder_id'],
                config['eval_forms_folder_id']
            )
            
            return final_df
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.stop()

def display_xparky_table(df: pd.DataFrame):
    """Display XParky points table with search functionality"""
    # Search functionality
    with st.container():
        search_query = st.text_input(
            "Search your name",
            placeholder="Enter first or last name...",
            help="Search is case-insensitive"
        )
    
    # Filter data based on search
    if search_query:
        mask = (df['First Name'].str.contains(search_query, case=False) | 
                df['Last Name'].str.contains(search_query, case=False))
        filtered_df = df[mask]
        st.caption(f"Found {len(filtered_df)} student(s)")
    else:
        filtered_df = df
    
    # Display table
    st.data_editor(
        filtered_df.drop(columns=['Student Number']),
        column_config={
            "First Name": st.column_config.TextColumn(
                "First Name",
                width="small"
            ),
            "Last Name": st.column_config.TextColumn(
                "Last Name",
                width="small"
            ),
            "XParky Points": st.column_config.ProgressColumn(
                "XParky Points",
                help="Total XParky points earned",
                format="%d",
                min_value=0,
                max_value=3000,
                width="large",
            ),
        },
        hide_index=True,
        use_container_width=True,
        disabled=True,
        height=2000
    )

    # Download button
    st.download_button(
        label="Download XParky Data",
        data=filtered_df.to_csv(index=False),
        file_name="xparky_points.csv",
        mime="text/csv",
    )

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_event_folders(_cert_processor: CertificateProcessor, main_folder_id: str):
    """Cache the event folders mapping"""
    return _cert_processor.get_event_folders(main_folder_id)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_certificates_for_event(_cert_processor: CertificateProcessor, event_folder_id: str):
    """Cache the certificates mapping for an event"""
    return _cert_processor.get_certificates_for_event(event_folder_id)

def display_certificate(client: GoogleAPIClient, file_id: str, name: str):
    """Display and enable download of certificate"""
    try:
        request = client.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
            
        fh.seek(0)
        
        # Display certificate
        image = Image.open(fh)
        st.image(image, caption=f"Certificate for {name}", use_container_width=True)
        
        # Download button
        fh.seek(0)
        st.download_button(
            label="Download Certificate",
            data=fh,
            file_name=f"{name}_certificate.png",
            mime="image/png"
        )
        
    except Exception as e:
        st.error(f"Error displaying certificate: {str(e)}")

def main():
    # Initialize app
    init_streamlit()
    
    # Display header
    st.image('assets/web-header.svg')
    
    # Get configuration
    config = load_config()
    
    # Initialize clients and processors
    client = GoogleAPIClient(config['credentials'])
    xparky_processor = XParkyProcessor(client)
    cert_processor = CertificateProcessor(client)
    
    # Create tabs
    tab1, tab2 = st.tabs(["XParky Points", "Certificates"])
    
    with tab1:
        # XParky points functionality
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            df = fetch_data(config)
            display_xparky_table(df)
    
    with tab2:
        col1_, col2_, col3_ = st.columns([1,3,1])
        with col2_:
            # Get event folders
            event_folders = get_event_folders(cert_processor, config['certificates_main_folder_id'])
            
            if not event_folders:
                st.error("No event folders found.")
                return
                
            # Event selection
            event_names = sorted(event_folders.keys())
            selected_event = st.selectbox(
                "Select Event",
                options=event_names,
                index=None,
                placeholder="Choose an event..."
            )
            
            if selected_event:
                # Get certificates for selected event
                certificates = get_certificates_for_event(
                    cert_processor, 
                    event_folders[selected_event]
                )
                
                if not certificates:
                    st.warning("No certificates found for this event.")
                    return
                    
                # Name selection
                available_names = sorted(cert_processor.get_available_names(certificates))
                selected_name = st.selectbox(
                    "Enter your Name",
                    options=available_names,
                    index=None,
                    placeholder="Choose your name..."
                )
                
                if selected_name:
                    file_id = certificates.get(selected_name.lower())
                    if file_id:
                        display_certificate(client, file_id, selected_name)
                    else:
                        st.error("Certificate not found. Please contact support.")

if __name__ == "__main__":
    main()
