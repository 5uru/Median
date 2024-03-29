from datetime import datetime, timedelta

import ebisu

from median.utils import median_logger


def convert_to_datetime(date_str, date_format="%Y-%m-%d %H:%M:%S.%f"):
    """Converts a date string to a datetime object.

    :param date_str: The date string to convert.
    :type date_str: str
    :param date_format: The format of the date string (default is "%Y-%m-%d %H:%M:%S.%f").
    :type date_format: str
    :returns: The datetime object representing the converted date.
    :rtype: datetime

    """

    return datetime.strptime(date_str, date_format)


def hours_since(date_last_test):
    """Calculates the number of hours since a given date.

    :param date_last_test: The date to calculate the hours since.
    :type date_last_test: datetime
    :returns: The number of hours elapsed since the given date.
    :rtype: float

    """

    one_hour = timedelta(hours=1)
    return (datetime.now() - date_last_test) / one_hour


def recall_prediction(database):
    """Predicts recall for each factID based on the database information.

    :param database: The database containing information for each factID.
    :returns: A list of dictionaries with 'factID' and 'recall' values, sorted by 'recall' in ascending order.
    :rtype: list

    """

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
    """Updates a model based on the result, total, and last test information.

    :param model: The current model to update.
    :param result: The result of the update.
    :param total: The total number of updates.
    :param last_test: The date of the last test.
    :returns: The updated model after the modifications.
    :rtype: str

    """

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
