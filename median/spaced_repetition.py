from datetime import timedelta, datetime

import ebisu

from median.utils import median_logger


def convert_to_datetime(date_str, date_format="%Y-%m-%d %H:%M:%S.%f"):
    """Convert a date string to a datetime object."""
    return datetime.strptime(date_str, date_format)


def hours_since(date_last_test):
    """Calculate the hours elapsed since the given datetime."""
    one_hour = timedelta(hours=1)
    return (datetime.now() - date_last_test) / one_hour


def recall_prediction(database):
    median_logger.info("Recall prediction for each factID")
    recall_list = [
        {
            "factID": row["factID"],
            "recall": ebisu.predictRecall(
                row["model"],
                hours_since(convert_to_datetime(row["lastTest"])),
                exact=True,
            ),
        }
        for row in database
    ]
    # Sort the recall_list by 'recall' value in ascending order outside the loop
    recall_list.sort(key=lambda x: x["recall"])
    return recall_list


def update_model(model, result, total, last_test):
    median_logger.info("Update model based on the result")
    try:
        new_model = ebisu.updateRecall(
            model, result, total, hours_since(convert_to_datetime(last_test))
        )
    except Exception:
        new_model = ebisu.updateRecall(
            model, 1, total, hours_since(convert_to_datetime(last_test))
        )
    if result == 2:
        new_model = ebisu.rescaleHalflife(new_model, 2.0)
    return str(new_model)
