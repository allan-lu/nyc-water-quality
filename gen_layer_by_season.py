import psycopg2
from psycopg2.extensions import AsIs
import datetime

now = datetime.datetime.now()

try:
    connection = psycopg2.connect(user="postgres",
                                  password='password',
                                  host='localhost',
                                  port='5432',
                                  database='alu')

    cursor = connection.cursor()

    change_schema = "SET search_path = nyc"
    cursor.execute(change_schema)

    # Create Sub-tables Query
    year_list = list(range(2000, now.year + 1))
    season_list = [(AsIs('winter'), 1), (AsIs('spring'), 2), (AsIs('summer'), 3), (AsIs('autumn'), 4)]
    for year in year_list:
        for season, num in season_list:
            params = {'y': year, 's': season, 'n': num}
            select_query = '''
                SELECT *
                FROM   wq_o2perc_season AS c,
                       (SELECT Count(fid) AS samples,
                               Max(year)  AS yr,
                               season AS szn
                        FROM   wq_o2perc_season
                        WHERE  year :: FLOAT = %(y)s :: FLOAT
                               AND season = '%(s)s'
                        GROUP BY season) AS t
                WHERE  samples > 20
                       AND c.year = t.yr
                       AND c.season = t.szn
                       '''
            cursor.execute(select_query, params)
            selection = cursor.fetchone()
            if selection is not None:
                create_table_query = "CREATE TABLE o2perc_%(y)s_%(n)s_%(s)s AS"
                query = create_table_query + select_query
                cursor.execute(query, params)
                print('Table %(s)s, %(y)s created successfully.' % params)
            else:
                print('Table %(s)s, %(y)s was not created.' % params)

    # Drop table
    # for year in year_list:
    #     for season, num in season_list:
    #         params = {'y': year, 's': season, 'n': num}
    #         drop_table_query = '''DROP TABLE IF EXISTS o2perc_%(y)s_%(n)s_%(s)s'''
    #         cursor.execute(drop_table_query, params)

    connection.commit()
    print('Query ran successfully')

except(Exception, psycopg2.Error) as error:
    print('Error while running query.', error)

finally:
    # Closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print('PostgreSQL connection is closed')
