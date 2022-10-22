"""
File provides test structures and test data
"""

def data_for_check_year_parameter():
    """
    Generated test data for check_year_parameter Test
    :return:
    """
    test_data = []
    for day in range(0, 100):
        for month in range(0, 100):
            if day < 10:
                day_part = ''.join(("0", str(day)))
            else:
                day_part = str(day)
            if month < 10:
                month_part = ''.join(("0", str(month)))
            else:
                month_part = str(month)
            day_month = '.'.join((str(day_part), str(month_part)))

            if month > 12 or month < 1:
                control_data_month = 1
            else:
                control_data_month = month

            if day > 31 or day < 1:
                control_data_day = 1
            else:
                control_data_day = day

            data = (day_month, {"day": control_data_day, "month": control_data_month})
            test_data.append(data)
    return test_data
