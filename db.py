# -*- coding: utf-8 -*-
"""
Importing packages needed for the bot to function,
"""
import sqlite3
import os
from datetime import datetime


class DB:
    """
    DB handling

    TODO:
        Make Add user into 1 system rather than 2, EG: Add user and change message.
        Write better documentation.
    """

    def __init__(self):
        self.db_file = "database.db"

        # Check if the new database file exists
        if not os.path.exists(self.db_file) and os.path.exists('specific_users.db'):
            self.migrate_database()  # Run migration if needed

        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS welcome_message (
                username TEXT PRIMARY KEY,
                last_message TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                custom_message TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS "quotes" (
                "Number"	INTEGER NOT NULL UNIQUE,
                "Quote"	TEXT NOT NULL,
                "Category"	TEXT,
                "Added"	TEXT,
                PRIMARY KEY("Number" AUTOINCREMENT)
            )
        """)

        self.conn.commit()

    def migrate_database(self):
        """
        For migrating from 1 DB to another DB
        :return:
        """
        try:
            old_db_conn = sqlite3.connect("specific_users.db")
            old_db_cursor = old_db_conn.cursor()

            new_db_conn = sqlite3.connect(self.db_file)
            new_db_cursor = new_db_conn.cursor()

            # Fetch data from old database and insert into new database
            old_db_cursor.execute("SELECT * FROM specific_users")
            rows = old_db_cursor.fetchall()

            for row in rows:
                print(row)
                new_db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS welcome_message (
                    username TEXT PRIMARY KEY,
                    last_message TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    custom_message TEXT
                )
            """)
                new_db_cursor.execute("INSERT INTO welcome_message VALUES (?, ?, ?)", row)

            new_db_conn.commit()

            old_db_conn.close()
            new_db_conn.close()
        except Exception as e:
            print("Please contact support for help with:", e)

    """
    Welcome
    """

    def add_user(self, username):
        """
        Adding user to database for welcome message
        :param username: name of the user you try to add
        :return:
        """
        try:
            timestring = "1970-01-01T00:00:00"
            self.cursor.execute("INSERT INTO welcome_message (username, last_message) VALUES (?,?)",
                                (username, timestring,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # print(f"User '{username}' is already in the database.")
            self.conn.rollback()
            return False

    def fetch_names(self):
        """
        Fetching if user is in the list
        :return:
        """
        # Retrieve the list of specific users from the database
        self.cursor.execute("SELECT username FROM welcome_message")
        specific_users = {row[0].lower() for row in self.cursor.fetchall()}
        return specific_users

    def check_user(self, username):
        self.cursor.execute("SELECT username FROM welcome_message WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result:
            return True  # Return true
        else:
            return False  # Return false

    def check_last_message(self, username):
        self.cursor.execute("SELECT last_message FROM welcome_message WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result:
            return result[0]  # Return the last message time as a string
        else:
            return None  # Return None if the user is not found

    def check_custom_message(self, username):
        self.cursor.execute("SELECT custom_message FROM welcome_message WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result:
            custom_message = result[0]
            if custom_message is not None:
                return custom_message  # Return the custom message if it exists
            else:
                return False  # Return False if custom message is NULL
        else:
            return False  # Return False if the user is not found

    def set_custom_message(self, custom_message, username):
        self.cursor.execute("UPDATE welcome_message SET custom_message = ? WHERE username = ?",
                            (custom_message, username,))
        self.conn.commit()
        if self.cursor.rowcount == 0:
            return False
        else:
            return True

    def set_last_message(self, username):
        last_message_time = datetime.now().isoformat()  # Convert the datetime to a string
        self.cursor.execute("UPDATE welcome_message SET last_message = ? WHERE username = ?",
                            (last_message_time, username,))
        self.conn.commit()

    def remove_user(self, username):
        self.cursor.execute("DELETE FROM welcome_message WHERE username = ?", (username,))
        self.conn.commit()
        if self.cursor.rowcount == 0:
            return False  # User not found, return False
        else:
            return True  # User successfully removed, return True

    """
    Quotes
    """

    def add_quote(self):
        try:

            # Get today's date
            today = datetime.today()

            # Format the date in the desired format
            formatted_date = today.strftime('%m/%d/%Y')

            print(formatted_date)

            self.cursor.execute("",
                                (formatted_date,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # print(f"User '{username}' is already in the database.")
            self.conn.rollback()
            return False

    """
    Auto shoutout
    """


if __name__ == "__main__":
    db = DB()

    print(db.check_user('djmater'))
    print(db.remove_user('djmater'))
    db.conn.close()  # Close the database connection when you're done with it
