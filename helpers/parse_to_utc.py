from datetime import datetime, timezone

def parse_to_utc(date):
    """
    Given a string with the date to parse, converts
    the date to utc string that can be undertand by js.

    Parameters: 
        date (string):  A string containing the date to parse.

    Returns:
        utc_date (string):  A string containing the date in utc
                            format compatible with js.
    """

    return datetime.strptime(
        date.replace(" ",''),
        "%Y-%m-%dT%H:%M:%S.%f%z"
    ).astimezone(
        tz=timezone.utc
    ).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )[:-3] + 'Z'

