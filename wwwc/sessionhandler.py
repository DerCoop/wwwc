"""session handler for wilmaa tv

    Python module to handle the wilmaa session

    """

import cookielib


def create_cookie(name, value):
    """create netscape formatted cookie

        format specification
        Domain	not_complete_url	/	only_https	expire_time	name	value

        :param name: the name of the cookie
        :param value: value of the cookie
        :return: the cookie

        """

    return cookielib.Cookie(
        domain="www.wilmaa.com",
        domain_specified=False,
        domain_initial_dot=False,
        path="/",
        secure=False,
        expires=None,
        name=name,
        value=value,
        version=0,
        port=None,
        port_specified=False,
        path_specified=True,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None
    )
