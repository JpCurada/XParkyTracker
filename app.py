import streamlit as st
import pandas as pd
import io
from PIL import Image
from googleapiclient.http import MediaIoBaseDownload
from src.client import GoogleAPIClient
from src.processors import XParkyProcessor, CertificateProcessor
from dotenv import load_dotenv

def init_streamlit():
    """Initialize Streamlit page configuration and styling"""
    st.set_page_config(
        page_title="Student Portal",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

        *, *::before, *::after {
            font-family: 'Poppins', sans-serif;
        }

        button[data-baseweb="tab"] {
            font-size: 24px;
            margin: 0;
            width: 100%;
        }

        button[title="View fullscreen"],
        .reportview-container,
        #MainMenu,
        .stDeployButton,
        footer,
        #stDecoration { 
            visibility: hidden; 
        }

        .search-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
                
        .stProgress > div > div > div {
            background-color: #4284f2 !important;
        }

        .certificate-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_google_client():
    """Initialize Google API client with Streamlit secrets"""
    try:
        client = GoogleAPIClient(st.secrets["GOOGLE_CREDENTIALS"])
        return client
    except Exception as e:
        st.error(f"Failed to initialize Google client: {str(e)}")
        st.info("Please check if GOOGLE_CREDENTIALS is properly set in Streamlit secrets")
        st.stop()

def load_config():
    """Load and validate environment variables"""
    load_dotenv()
    
    required_secrets = [
        "CLASSROOM_FOLDER_ID",
        "EVAL_FORMS_FOLDER_ID",
        "CERTIFICATES_FOLDER_ID"
    ]
    
    config = {key: st.secrets.get(key) for key in required_secrets}
    
    if missing_vars := [key for key, value in config.items() if not value]:
        st.error(f"Missing configuration variables: {', '.join(missing_vars)}")
        st.stop()
    
    return config

def fetch_data(client: GoogleAPIClient, config: dict) -> pd.DataFrame:
    """Fetch and process XParky data"""
    try:
        with st.spinner('Loading data...'):
            processor = XParkyProcessor(client)
            final_df, _, _ = processor.process_all_data(
                config['CLASSROOM_FOLDER_ID'],
                config['EVAL_FORMS_FOLDER_ID']
            )
            return final_df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.stop()

def display_xparky_table(df: pd.DataFrame):
    """Display XParky points table with search functionality"""
    with st.container():
        search_query = st.text_input(
            "Search your name",
            placeholder="Enter first or last name...",
            help="Search is case-insensitive"
        )
    
    filtered_df = df
    if search_query:
        mask = (df['First Name'].str.contains(search_query, case=False) | 
                df['Last Name'].str.contains(search_query, case=False))
        filtered_df = df[mask]
        st.caption(f"Found {len(filtered_df)} student(s)")
    
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

    st.download_button(
        label="Download XParky Data",
        data=filtered_df.to_csv(index=False),
        file_name="xparky_points.csv",
        mime="text/csv",
    )

@st.cache_data(ttl=3600)
def get_event_folders(cert_processor: CertificateProcessor, main_folder_id: str):
    """Cache the event folders mapping"""
    return cert_processor.get_event_folders(main_folder_id)

@st.cache_data(ttl=3600)
def get_certificates_for_event(cert_processor: CertificateProcessor, event_folder_id: str):
    """Cache the certificates mapping for an event"""
    return cert_processor.get_certificates_for_event(event_folder_id)

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
        image = Image.open(fh)
        st.image(image, caption=f"Certificate for {name}", use_container_width=True)
        
        fh.seek(0)
        st.download_button(
            label="Download Certificate",
            data=fh,
            file_name=f"{name}_certificate.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"Error displaying certificate: {str(e)}")

def handle_certificates_tab(client: GoogleAPIClient, cert_processor: CertificateProcessor, config: dict):
    """Handle the certificates tab functionality"""
    event_folders = get_event_folders(cert_processor, config['CERTIFICATES_FOLDER_ID'])
    
    if not event_folders:
        st.error("No event folders found.")
        return
    
    event_names = sorted(event_folders.keys())
    selected_event = st.selectbox(
        "Select Event",
        options=event_names,
        index=None,
        placeholder="Choose an event..."
    )
    
    if selected_event:
        certificates = get_certificates_for_event(
            cert_processor, 
            event_folders[selected_event]
        )
        
        if not certificates:
            st.warning("No certificates found for this event.")
            return
        
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

def main():
    try:
        init_streamlit()
        st.image('assets/web-header.svg')
        
        config = load_config()
        client = initialize_google_client()
        
        xparky_processor = XParkyProcessor(client)
        cert_processor = CertificateProcessor(client)
        
        tab1, tab2 = st.tabs(["XParky Points", "Certificates"])
        
        with tab1:
            col1, col2, col3 = st.columns([1,3,1])
            with col2:
                df = fetch_data(client, config)
                display_xparky_table(df)
        
        with tab2:
            col1_, col2_, col3_ = st.columns([1,3,1])
            with col2_:
                handle_certificates_tab(client, cert_processor, config)

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()
