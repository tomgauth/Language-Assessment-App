from typing import Dict, Any, Union
from codaio import Row

class CodaModel:
    TABLE_ID: str                  # override in subclass
    COLS: Dict[str,str]            # field_name -> column_name

    @classmethod
    def from_row(cls, row: Union[Dict[str,Any], Row]):
        """
        Handle both codaio Row objects and our original dict format
        row: Either a codaio Row object or a dict from Coda API
        """
        kwargs = {}
        
        # Handle codaio Row object
        if hasattr(row, 'to_dict'):
            values = row.to_dict()
            row_id = row.id
        # Handle our original dict format
        else:
            values = row.get("values", {})
            row_id = row.get("id")
        
        # Map column names to field names
        for field, col_name in cls.COLS.items():
            kwargs[field] = values.get(col_name, "")
        
        # Store the row ID for updates
        kwargs["_row_id"] = row_id
        return cls(**kwargs)

    def to_coda_payload(self) -> Dict[str,Any]:
        """
        Returns {"values": {column_name: value, ...}}
        for create/update calls.
        """
        values = {}
        for field, col_name in self.COLS.items():
            value = getattr(self, field, None)
            if value is not None:
                values[col_name] = value
        return {"values": values} 