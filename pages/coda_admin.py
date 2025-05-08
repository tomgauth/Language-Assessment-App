import streamlit as st
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from models.coda_service import CodaService
from codaio import Cell
import pandas as pd

# Load environment variables
load_dotenv()
api_key = os.getenv('CODA_API_KEY')
doc_id = os.getenv('CODA_DOC_ID')

# Initialize CodaService
coda_service = CodaService(api_key, doc_id)

# Page config
st.set_page_config(page_title="Coda Admin", layout="wide")
st.title("Coda Database Admin")

# Sidebar for table selection
st.sidebar.title("Tables")
table_ids = {
    "Users": "grid-qqR8f6GhaA",
    "Challenges": "grid-frCt4QLI3B",
    "Conversations": "grid-nCqNTa30ig",
    "Skills": "grid-VZpWaIP27c",
    "Topics": "grid-iG8u3niYDD",
    "Prompts": "grid-vBrJKADk0W"
}

selected_table = st.sidebar.selectbox(
    "Select Table",
    list(table_ids.keys())
)

# Get table data
table_id = table_ids[selected_table]
schema = coda_service.get_table_schema(table_id)
rows = coda_service.get_rows(table_id)

# Display table schema
st.subheader("Table Schema")
schema_df = pd.DataFrame(schema['columns'])
st.dataframe(schema_df[['name', 'type', 'calculated']])

# Display table data
st.subheader("Table Data")
if rows:
    # Convert rows to DataFrame
    data = []
    for row in rows:
        # Convert row values to dictionary
        row_data = dict(row.values)
        row_data['id'] = row.id  # Add row ID
        data.append(row_data)
    
    df = pd.DataFrame(data)
    
    # Add search functionality
    search_term = st.text_input("Search in all columns")
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        df = df[mask]
    
    # Display the data
    st.dataframe(df, use_container_width=True)
    
    # Add row operations
    st.subheader("Row Operations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Create New Row")
        new_data = {}
        for col in schema['columns']:
            if not col['calculated']:  # Don't allow editing calculated columns
                new_data[col['name']] = st.text_input(f"New {col['name']}", key=f"new_{col['name']}")
        
        if st.button("Create Row"):
            try:
                cells = coda_service.create_cells(new_data)
                new_row = coda_service.create_row(table_id, cells)
                st.success("Row created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating row: {str(e)}")
    
    with col2:
        st.write("Update Row")
        row_id = st.selectbox("Select Row to Update", df['id'].tolist())
        if row_id:
            row_data = df[df['id'] == row_id].iloc[0]
            update_data = {}
            for col in schema['columns']:
                if not col['calculated']:
                    current_value = row_data.get(col['name'], '')
                    update_data[col['name']] = st.text_input(
                        f"Update {col['name']}", 
                        value=str(current_value),
                        key=f"update_{col['name']}"
                    )
            
            if st.button("Update Row"):
                try:
                    cells = coda_service.create_cells(update_data)
                    updated_row = coda_service.update_row(table_id, row_id, cells)
                    st.success("Row updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating row: {str(e)}")
            
            if st.button("Delete Row"):
                try:
                    coda_service.delete_row(table_id, row_id)
                    st.success("Row deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting row: {str(e)}")
else:
    st.info("No data found in this table") 