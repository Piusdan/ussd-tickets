from datetime import datetime, timedelta

def eastafrican_time():
    return datetime.utcnow() + timedelta(hours=3)

def time_str():
    return eastafrican_time().strftime("%Y-%m-%d %H:%M:%S +0300")
