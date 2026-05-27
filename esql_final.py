import psycopg
import sys

class QueryResult:
    def __init__(self, rows, col_names):
        self.rows = rows
        self.col_names = col_names
    
    def empty(self):
        return len(self.rows) == 0

    def __len__(self):
        return len(self.rows)
    
    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, idx):
        return self.rows[idx]

    def __str__(self):
        return str(self.rows)

class EmbeddedSQL:
    """
    A simple embedded SQL utility class designed to work with PostgreSQL
    via the psycopg2 driver.
    """

    def __init__(self, dbname, dbport, user, passwd, verbose = False):
        """
        Creates a new instance of EmbeddedSQL and establishes a physical
        connection to the database.

        :param dbname:  the name of the database
        :param dbport:  the port the PostgreSQL server is running on
        :param user:    the user name used to login to the database
        :param passwd:  the user login password
        """
        if verbose:
            print("Connecting to database...")
        try:
            self._connection = psycopg.connect(
                dbname=dbname,
                user=user,
                password=passwd,
                host="localhost",
                port=dbport
            )
            if verbose:
                print(f"Connection URL: postgresql://localhost:{dbport}/{dbname}\n")
                print("Done")
        except Exception as e:
            print(f"Error - Unable to Connect to Database: {e}", file=sys.stderr)
            print("Make sure you started postgres on this machine")
            sys.exit(-1)

    def execute_update(self, sql):
        """
        Executes an update SQL statement (CREATE, INSERT, UPDATE, DELETE, DROP).

        :param sql: the input SQL string
        """
        cursor = self._connection.cursor()
        cursor.execute(sql)
        self._connection.commit()
        cursor.close()

    def execute_query(self, query, params=None, verbose=False):
        """
        Executes a SELECT query and prints the results to standard output.

        :param query:  the input query string
        :param params: optional tuple of parameters for parameterized queries
        :return:       the number of rows returned
        """
        cursor = self._connection.cursor()
        cursor.execute(query, params)

        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        if verbose:
            # Print header
            print("\t".join(col_names))

            # Print each row
            for row in rows:
                print("\t".join(str(val) for val in row))
        cursor.close()


        return QueryResult(rows, col_names)

    def cleanup(self):
        """
        Closes the physical connection if it is open.
        """
        try:
            if self._connection is not None:
                self._connection.close()
        except Exception:
            pass  # ignored

if __name__ == "__main__":
    dbname = "cs166_final" #sys.argv[1]
    dbport = 5432#sys.argv[2]
    user = "ryan" #sys.argv[3]
    password = "ryan123"

    test_query = """
    SELECT * 
    FROM users
    WHERE role = 'Admin';
    """

    esql = EmbeddedSQL(dbname, dbport, user, password)
    res = esql.execute_query(test_query)
    print(res)
    