import datetime

class Util:
    @staticmethod
    def strToDate(date) -> datetime.date:
        if (type(date) is str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        return date