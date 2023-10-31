from datetime import date


class Delivery:
    def __init__(self, start_date: date, end_date: date, *args, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_str = start_date.strftime('%d-%m-%Y')
        self.end_date_str = end_date.strftime('%d-%m-%Y')
