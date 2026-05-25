import psycopg

#!/usr/bin/env python3
# ----------------------------------------------------------
# Template Python User Interface
# ================================
#
# Database Management Systems
# Department of Computer Science & Engineering
# University of California - Riverside
#
# Target DBMS: 'Postgres'
#
# ----------------------------------------------------------

"""
Run with:
python3 EmbeddedSQL.py ryan032_lab6_DB 37353 ryan032

"""
import sys
import psycopg2


class EmbeddedSQL:
    """
    A simple embedded SQL utility class designed to work with PostgreSQL
    via the psycopg2 driver.
    """

    def __init__(self, dbname, dbport, user, passwd=""):
        """
        Creates a new instance of EmbeddedSQL and establishes a physical
        connection to the database.

        :param dbname:  the name of the database
        :param dbport:  the port the PostgreSQL server is running on
        :param user:    the user name used to login to the database
        :param passwd:  the user login password
        """
        print("Connecting to database...")
        try:
            self._connection = psycopg2.connect(
                database=dbname,
                user=user,
                password=passwd,
                host="localhost",
                port=dbport
            )
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

    def execute_query(self, query, params=None):
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
        row_count = 0

        # Print header
        print("\t".join(col_names))

        # Print each row
        for row in rows:
            print("\t".join(str(val) for val in row))
            row_count += 1

        cursor.close()
        return row_count

    def cleanup(self):
        """
        Closes the physical connection if it is open.
        """
        try:
            if self._connection is not None:
                self._connection.close()
        except Exception:
            pass  # ignored


# ----------------------------------------------------------
# Helper functions
# ----------------------------------------------------------

def greeting():
    print("\n\n*******************************************************")
    print("              User Interface                           ")
    print("*******************************************************\n")


def read_choice():
    """
    Reads the user's menu choice from the keyboard.
    Keeps prompting until a valid integer is entered.
    """
    while True:
        try:
            return int(input("Please make your choice: "))
        except ValueError:
            print("Your input is invalid!")


# ----------------------------------------------------------
# Query functions
# ----------------------------------------------------------

def query_example(esql):
    """Example query: find parts with cost lower than a user-supplied value."""
    try:
        cost = input("\tEnter cost: $")
        row_count = esql.execute_query(
            "SELECT * FROM Catalog WHERE cost < %s;",
            (cost,)
        )
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


def query1(esql):
    try:
        query = """
        SELECT s.sname, COUNT(*) AS parts_supplied
        FROM Suppliers s
        INNER JOIN Catalog c ON c.sid = s.sid
        INNER JOIN Parts p ON p.pid = c.pid
        GROUP BY s.sid;
        """
        row_count = esql.execute_query(query)
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


def query2(esql):
    try:
        query = """
        SELECT s.sname, COUNT(*) AS parts_supplied
        FROM Suppliers s
        INNER JOIN Catalog c ON c.sid = s.sid
        INNER JOIN Parts p ON p.pid = c.pid
        GROUP BY s.sid
        HAVING COUNT(*) >= 3;
        """
        row_count = esql.execute_query(query)
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


def query3(esql):
    try:
        query = """
        SELECT s.sname, COUNT(*) AS parts_supplied
        FROM Suppliers s
        INNER JOIN Catalog c ON c.sid = s.sid
        INNER JOIN Parts p ON p.pid = c.pid
        WHERE NOT EXISTS (
            SELECT *
            FROM Catalog c2
            INNER JOIN Parts p2 on p2.pid = c2.pid
            WHERE s.sid = c2.sid AND p2.color <> 'Green'
        )
        GROUP BY s.sid;
        """
        row_count = esql.execute_query(query)
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


def query4(esql):
    try:
        query = """
        SELECT s.sname, MAX(c.cost) AS expensive_cost
        FROM Suppliers s
        INNER JOIN Catalog c ON c.sid = s.sid
        INNER JOIN Parts p ON p.pid = c.pid
        WHERE EXISTS (
            SELECT *
            FROM Catalog c2
            INNER JOIN Parts p2 on p2.pid = c2.pid
            WHERE s.sid = c2.sid AND p2.color = 'Green'
        ) 
        AND EXISTS (
            SELECT *
            FROM Catalog c2
            INNER JOIN Parts p2 on p2.pid = c2.pid
            WHERE s.sid = c2.sid AND p2.color = 'Red'
        )
        GROUP BY s.sid;
        """
        row_count = esql.execute_query(query)
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


def query5(esql):
    def get_float(msg: str) -> float:
        while True:
            try:
                print(msg)
                x = float(input())
                print("")
                return x
            except ValueError:
                print("Please enter a valid float.")
                
    try:
        cost = get_float("Enter cost: ")
        query = """
        SELECT DISTINCT p.pname
        FROM Parts p
        INNER JOIN Catalog c ON c.pid = p.pid
        WHERE c.cost < %s;
        """
        row_count = esql.execute_query(
            query,
            (cost,)
        )
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


def query6(esql):                
    try:
        product_name = input("Enter product name: ")
        query = """
        SELECT DISTINCT s.address
        FROM Suppliers s
        INNER JOIN Catalog c ON c.sid = s.sid
        INNER JOIN Parts p ON p.pid = c.pid
        WHERE p.pname = %s;
        """
        row_count = esql.execute_query(
            query,
            (product_name,)
        )
        print(f"total row(s): {row_count}")
    except Exception as e:
        print(e, file=sys.stderr)


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():
    if len(sys.argv) != 4:
        print(
            f"Usage: python {sys.argv[0]} <dbname> <port> <user>",
            file=sys.stderr
        )
        return

    greeting()

    dbname = sys.argv[1]
    dbport = sys.argv[2]
    user   = sys.argv[3]

    esql = None
    try:
        esql = EmbeddedSQL(dbname, dbport, user, "")

        keepon = True
        while keepon:
            print("MAIN MENU")
            print("---------")
            print("0. Find the pid of parts with cost lower than $_____ (example)")
            print("1. Find the total number of parts supplied by each supplier")
            print("2. Find the total number of parts supplied by each supplier who supplies at least 3 parts")
            print("3. For every supplier that supplies only green parts, print the name of the supplier and the total number of parts that they supply")
            print("4. For every supplier that supplies green part and red part, print the name and the price of the most expensive part that they supply")
            print("5. Find the name of parts with cost lower than $_____")
            print("6. Find the address of the suppliers who supply _____________ (pname)")
            print("9. < EXIT")

            choice = read_choice()

            if   choice == 0: query_example(esql)
            elif choice == 1: query1(esql)
            elif choice == 2: query2(esql)
            elif choice == 3: query3(esql)
            elif choice == 4: query4(esql)
            elif choice == 5: query5(esql)
            elif choice == 6: query6(esql)
            elif choice == 9: keepon = False
            else: print("Unrecognized choice!")

    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        if esql is not None:
            print("Disconnecting from database...", end="")
            esql.cleanup()
            print("Done\n\nBye!")


if __name__ == "__main__":
    main()
