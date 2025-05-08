import requests
from typing import Dict, Any

class CodaConnector:
    BASE_URL = "https://coda.io/apis/v1"

    def __init__(self, api_token: str, doc_id: str):
        self.api_token = api_token
        self.doc_id = doc_id
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_table_columns(self, table_id: str) -> Dict[str, str]:
        """Get column names and their IDs for a table"""
        response = self._make_request("GET", f"docs/{self.doc_id}/tables/{table_id}/columns")
        return {col["name"]: col["id"] for col in response["items"]}

    def get_table_rows(self, table_id: str) -> Dict:
        """Get all rows from a table"""
        # First get the column mappings
        columns = self.get_table_columns(table_id)
        print("Debug - Column mappings:", columns)  # Debug column mappings
        
        # Get the rows
        response = self._make_request("GET", f"docs/{self.doc_id}/tables/{table_id}/rows")
        print("Debug - Raw Coda API response:", response)  # Debug raw response
        
        # Format the response to match our model's expected structure
        formatted_response = {
            "items": [
                {
                    "id": row["id"],
                    "values": {
                        columns.get(col_id, col_id): value  # Map column ID to name
                        for col_id, value in row.get("values", {}).items()
                    }
                }
                for row in response.get("items", [])
            ]
        }
        print("Debug - Formatted response:", formatted_response)  # Debug formatted response
        return formatted_response

    def insert_row(self, table_id: str, payload: Dict) -> Dict:
        """Insert a new row into a table"""
        return self._make_request("POST", f"docs/{self.doc_id}/tables/{table_id}/rows", payload)

    def update_row(self, table_id: str, row_id: str, payload: Dict) -> Dict:
        """Update an existing row in a table"""
        return self._make_request("PUT", f"docs/{self.doc_id}/tables/{table_id}/rows/{row_id}", payload)

    def delete_row(self, table_id: str, row_id: str) -> Dict:
        """Delete a row from a table"""
        return self._make_request("DELETE", f"docs/{self.doc_id}/tables/{table_id}/rows/{row_id}") 