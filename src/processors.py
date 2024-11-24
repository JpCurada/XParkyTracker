from dataclasses import dataclass
import pandas as pd
from typing import Dict, Optional, Tuple
from .client import GoogleAPIClient

@dataclass
class XParkyPoints:
    """Constants for XParky point values."""
    ONBOARDING_EVAL: int = 70
    REGULAR_EVAL: int = 200
    CERTIFICATE_BADGE: int = 100
    PROJECT: int = 150

class XParkyProcessor:
    """Processor for calculating and managing XParky points."""
    
    def __init__(self, client: GoogleAPIClient):
        self.client = client
        self.points = XParkyPoints()
        self.DATABASE_ID = '1kPb0rcuEGNsuGqrMX8eWDkk-v5erbOHDLqAL3eMERzw'
    
    def get_student_database(self) -> Optional[pd.DataFrame]:
        """Fetch student information from database."""
        try:
            df = self.client.get_sheet_data(self.DATABASE_ID, 'Data')
            if df is None or not all(col in df.columns for col in ['Student Number', 'First Name', 'Last Name']):
                print("Invalid database format or missing required columns")
                return None
                
            # Clean the data
            df = df[df["Position"] == "Data and ML Cadet"] # Ensure that only Data and ML cadets are included
            df['Student Number'] = df['Student Number'].astype(str).str.strip()
            df['First Name'] = df['First Name'].str.strip()
            df['Last Name'] = df['Last Name'].str.strip()
            
            return df[['Student Number', 'First Name', 'Last Name']]
            
        except Exception as e:
            print(f"Error fetching student database: {str(e)}")
            return None

    def merge_with_database(self, points_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge XParky points with student information, including students with 0 points.
        Ensures all students in the database are included in the final DataFrame.
        """
        try:
            # Get student database
            db_df = self.get_student_database()
        
            if db_df is None:
                return points_df
            
            # Clean student numbers in points_df
            points_df['Student Number'] = points_df['Student Number'].astype(str).str.strip()
            
            # Merge points with student information using outer join
            merged_df = pd.merge(
                db_df,  # Start with database to ensure all students are included
                points_df,
                on='Student Number',
                how='left'  # Use left join to keep all students from database
            )
            
            # Fill missing points with 0
            merged_df['XParky Points'] = merged_df['XParky Points'].fillna(0).astype(int)
            
            # Handle missing names (shouldn't occur with left join but kept for safety)
            merged_df['First Name'] = merged_df['First Name'].fillna('Unknown')
            merged_df['Last Name'] = merged_df['Last Name'].fillna('Student')
            
            # Reorder columns
            final_df = merged_df[[
                'Student Number',
                'First Name',
                'Last Name',
                'XParky Points'
            ]]
            
            return final_df.sort_values('XParky Points', ascending=False).reset_index(drop=True)
            
        except Exception as e:
            print(f"Error merging with database: {str(e)}")
            return points_df
    
    def process_evaluation_forms(self, folder_id: str) -> pd.DataFrame:
        """Process evaluation form responses and calculate points."""
        files = self.client.list_files_in_folder(folder_id)
        points_dict = {}
        
        for file_info in files:
            try:
                df = self.client.get_sheet_data(file_info['id'], 'Data')
                if df is None or 'Student Number' not in df.columns:
                    continue
                
                points = (self.points.ONBOARDING_EVAL 
                         if 'onboarding' in file_info['name'].lower() 
                         else self.points.REGULAR_EVAL)
                
                for student in df['Student Number'].unique():
                    points_dict[str(student).strip()] = points_dict.get(str(student).strip(), 0) + points
                    
            except Exception as e:
                print(f"Error processing {file_info['name']}: {str(e)}")
                
        return self._create_points_dataframe(points_dict)
    
    def process_classroom_submission(self, folder_id: str) -> pd.DataFrame:
        """Process classroom submissions and calculate points."""
        folders = self.client.list_files_in_folder(folder_id)

        classroom_submission_folders_id = [folder_dict['id'] for folder_dict in folders if folder_dict['name'].strip() != 'evaluationForms']
        
        files = []
        for folder_id in classroom_submission_folders_id: 
            files.extend(self.client.list_files_in_folder(folder_id))
        
        points_dict = {}

        unique_file_names = list(set([file_info['name'] for file_info in files]))
        
        for file_name in unique_file_names:
            try:
                file_name = file_name.upper()
                if not any(keyword in file_name for keyword in ['CERTIFICATE', 'BADGE', 'PROJECT']):
                    continue
                
                student_number = file_name.split('_')[0].strip()
                points = (self.points.PROJECT if 'PROJECT' in file_name 
                         else self.points.CERTIFICATE_BADGE)
                
                points_dict[student_number] = points_dict.get(student_number, 0) + points
                
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
                    
        return self._create_points_dataframe(points_dict)
    
    def _create_points_dataframe(self, points_dict: Dict) -> pd.DataFrame:
        """Create a DataFrame from points dictionary."""
        if not points_dict:
            return pd.DataFrame(columns=['Student Number', 'XParky Points'])
            
        df = pd.DataFrame(list(points_dict.items()), 
                         columns=['Student Number', 'XParky Points'])
        return df.sort_values('XParky Points', ascending=False).reset_index(drop=True)

    def process_all_data(self, classroom_folder_id: str, eval_forms_folder_id: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Process all data sources and return combined results."""
        try:
            # Get points from different sources
            classroom_points = self.process_classroom_submission(classroom_folder_id)
            eval_points = self.process_evaluation_forms(eval_forms_folder_id)
            
            # Combine all points
            combined_df = pd.concat([classroom_points, eval_points])
            total_points = (combined_df.groupby('Student Number')['XParky Points']
                          .sum()
                          .reset_index()
                          .sort_values('XParky Points', ascending=False))
            
            # Merge with student database
            final_df = self.merge_with_database(total_points)
            
            return final_df, classroom_points, eval_points
            
        except Exception as e:
            print(f"Error processing all data: {str(e)}")
            return (pd.DataFrame(columns=['Student Number', 'First Name', 'Last Name', 'XParky Points']),
                   pd.DataFrame(columns=['Student Number', 'XParky Points']),
                   pd.DataFrame(columns=['Student Number', 'XParky Points']))
