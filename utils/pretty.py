# coding:utf-8
from prettytable import PrettyTable, main, from_csv, from_db_cursor, from_html


def table(rows, headers=None, reverse=False):
    """ 美观输出的库
    +-----------+-------+------------+-----------------+
    | City name |  Area | Population | Annual Rainfall |
    +-----------+-------+------------+-----------------+
    | Sydney    | 2058d |  4336374   |     1214.8f     |
    | Melbourne | 1566d |  3806092   |      646.9f     |
    | Brisbane  | 5905d |  1857594   |     1146.4f     |
    | Perth     | 5386d |  1554769   |      869.4f     |
    | Adelaide  | 1295d |  1158259   |      600.5f     |
    | Hobart    | 1357d |   205556   |      619.5f     |
    | Darwin    | 0112d |   120900   |     1714.7f     |
    +-----------+-------+------------+-----------------+
    """
    _table = PrettyTable(headers)
    for row in rows:
        _table.add_row(row)
    _table.reversesort = reverse
    return _table


if __name__ == '__main__':
    main()
    print table([range(5), range(10, 15), range(20, 25)])
