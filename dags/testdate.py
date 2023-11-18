from datetime import datetime

date1 = datetime.strptime('2005-01-01', '%Y-%m-%d').date()
date2 = datetime.strptime('2000-01-01', '%Y-%m-%d').date()

# So sánh ngày
if date1 < date2:
    print("date1 >date2")
elif date1 == date2:
    print("date1 == date2")
else:
    print("date1 < date2")
