from functools import partial
from pyhive.hive import connect as HiveConnection


def conversion_to_dict(cursor, table_name=False):
    desc = cursor.description
    if table_name:
        for desc in cursor.description:
            if "." in desc[0]:
                desc[0] = desc[0].split(".", 1)[1]

    for row in cursor:
        yield {desc[index][0]: item for index, item in enumerate(row)}


if __name__ == '__main__':

    HiveConnection = partial(HiveConnection, auth="LDAP")
    hive_conn = HiveConnection(host='10.15.1.16', port=10000, username='root', password='123456', database='data_xiaonuan_final')
    cursor = hive_conn.cursor()
    cursor.execute('SELECT * FROM clinic_product LIMIT 1000')
    columns_names = [head[0].split(".", 1)[1] for head in cursor.description]
    for row in conversion_to_dict(cursor):
        print row
    cursor.close()
    hive_conn.close()
