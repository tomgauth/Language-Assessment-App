from typing import List, Optional, Dict, Any
from codaio import Coda, Document, Table, Row, Cell

class CodaService:
    def __init__(self, api_key: str, doc_id: str):
        """Initialize the Coda service with API key and document ID"""
        self.coda = Coda(api_key)
        self.doc = Document(doc_id, coda=self.coda)
        self._tables: Dict[str, Table] = {}

    def get_table(self, table_id: str) -> Table:
        """Get a table by ID, caching it for future use"""
        if table_id not in self._tables:
            self._tables[table_id] = self.doc.get_table(table_id)
        return self._tables[table_id]

    def get_rows(self, table_id: str, limit: Optional[int] = None, offset: Optional[str] = None) -> List[Row]:
        """Get all rows from a table"""
        table = self.get_table(table_id)
        return table.rows(limit=limit, offset=offset)

    def find_rows_by_value(self, table_id: str, column_name: str, value: Any) -> List[Row]:
        """Find rows where a column matches a value"""
        table = self.get_table(table_id)
        return table.find_row_by_column_name_and_value(column_name, value)

    def get_row_by_id(self, table_id: str, row_id: str) -> Optional[Row]:
        """Get a specific row by ID"""
        table = self.get_table(table_id)
        try:
            return table[row_id]
        except KeyError:
            return None

    def create_row(self, table_id: str, cells: List[Cell]) -> Row:
        """Create a new row in a table"""
        table = self.get_table(table_id)
        return table.upsert_row(cells)

    def update_row(self, table_id: str, row_id: str, cells: List[Cell]) -> Row:
        """Update an existing row"""
        table = self.get_table(table_id)
        return table.update_row(row_id, cells)

    def delete_row(self, table_id: str, row_id: str) -> None:
        """Delete a row by ID"""
        table = self.get_table(table_id)
        table.delete_row_by_id(row_id)

    def get_columns(self, table_id: str) -> List[Dict[str, Any]]:
        """Get all columns from a table"""
        table = self.get_table(table_id)
        return [
            {
                'id': col.id,
                'name': col.name,
                'type': col.type,
                'calculated': col.calculated
            }
            for col in table.columns()
        ]

    def create_cell(self, column_name: str, value: Any) -> Cell:
        """Create a Cell object for a column"""
        return Cell(column=column_name, value_storage=value)

    def create_cells(self, data: Dict[str, Any]) -> List[Cell]:
        """Create Cell objects from a dictionary of column names and values"""
        return [self.create_cell(name, value) for name, value in data.items()]

    def get_table_schema(self, table_id: str) -> Dict[str, Any]:
        """Get the schema of a table including columns and their types"""
        table = self.get_table(table_id)
        return {
            'id': table.id,
            'name': table.name,
            'columns': self.get_columns(table_id)
        } 