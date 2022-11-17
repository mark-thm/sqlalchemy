# mysql/pymysql.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


r"""

.. dialect:: mysql+pymysql
    :name: PyMySQL
    :dbapi: pymysql
    :connectstring: mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
    :url: https://pymysql.readthedocs.io/

Unicode
-------

Please see :ref:`mysql_unicode` for current recommendations on unicode
handling.

.. _pymysql_ssl:

SSL Connections
------------------

The PyMySQL DBAPI accepts the same SSL arguments as that of MySQLdb,
described at :ref:`mysqldb_ssl`.   See that section for examples.


MySQL-Python Compatibility
--------------------------

The pymysql DBAPI is a pure Python port of the MySQL-python (MySQLdb) driver,
and targets 100% compatibility.   Most behavioral notes for MySQL-python apply
to the pymysql driver as well.

"""  # noqa

from .mysqldb import MySQLDialect_mysqldb
from ...util import langhelpers


class MySQLDialect_pymysql(MySQLDialect_mysqldb):
    driver = "pymysql"
    supports_statement_cache = True

    description_encoding = None

    @langhelpers.memoized_property
    def supports_server_side_cursors(self):
        try:
            cursors = __import__("pymysql.cursors").cursors
            self._sscursor = cursors.SSCursor
            return True
        except (ImportError, AttributeError):
            return False

    @classmethod
    def import_dbapi(cls):
        return __import__("pymysql")

    def create_connect_args(self, url, _translate_args=None):
        if _translate_args is None:
            _translate_args = dict(username="user")
        return super().create_connect_args(
            url, _translate_args=_translate_args
        )

    def is_disconnect(self, e, connection, cursor):
        if super().is_disconnect(e, connection, cursor):
            return True
        elif isinstance(e, self.dbapi.Error):
            str_e = str(e).lower()
            return (
                "already closed" in str_e or "connection was killed" in str_e
            )
        else:
            return False

    def _extract_error_code(self, exception):
        if isinstance(exception.args[0], Exception):
            exception = exception.args[0]
        return exception.args[0]


dialect = MySQLDialect_pymysql
