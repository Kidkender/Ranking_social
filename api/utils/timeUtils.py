from datetime import datetime

now = datetime.now()


# dd/mm/yyyy H:M:S
def get_datetime_now() -> str:
    return now.strftime("%d/%m/%Y %H:%M:%S")
