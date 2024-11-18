import pandas as pd
from typing import List

def combine_xparky_points(*dataframes: pd.DataFrame) -> pd.DataFrame:
    """Combine multiple XParky points DataFrames."""
    if not dataframes:
        return pd.DataFrame(columns=['Student Number', 'XParky Points'])
        
    combined_df = pd.concat(dataframes)
    final_df = (combined_df.groupby('Student Number')['XParky Points']
                .sum()
                .reset_index()
                .sort_values('XParky Points', ascending=False))
    
    _print_summary_statistics(final_df)
    return final_df

def _print_summary_statistics(df: pd.DataFrame) -> None:
    """Print summary statistics for XParky points."""
    print("\nFinal XParky Points Summary:")
    print(f"Total students: {len(df):,}")
    print(f"Total points awarded: {df['XParky Points'].sum():,}")
    print(f"Average points per student: {df['XParky Points'].mean():.2f}")
    print(f"Highest points: {df['XParky Points'].max():,}")
    print(f"Lowest points: {df['XParky Points'].min():,}")