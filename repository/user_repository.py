from models.user import User

def get_all_users(coda_service):
    rows = coda_service.get_rows(User.TABLE_ID)
    return [User.from_row(row) for row in rows] 