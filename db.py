import sqlite3
from datetime import datetime

class DB():
    def __init__(self):
        self.conn = sqlite3.connect("specific_users.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS specific_users (
                username TEXT PRIMARY KEY,
                lastmessage TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                custommessage TEXT
            )
        """)
        self.conn.commit()

    def add_user(self, username):
        try:
            timestring = "1970-01-01T00:00:00"
            self.cursor.execute("INSERT INTO specific_users (username, lastmessage) VALUES (?,?)", (username, timestring,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            #print(f"User '{username}' is already in the database.")
            self.conn.rollback() 
            return False

    def fetch_names(self):
        # Retrieve the list of specific users from the database
        self.cursor.execute("SELECT username FROM specific_users")
        self.specific_users = {row[0].lower() for row in self.cursor.fetchall()}
        return self.specific_users

    def check_user(self, username):
        self.cursor.execute("SELECT username FROM specific_users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result:
            return True  # Return true
        else:
            return False  # Return false
        

    def check_lastmessage(self, username):
        self.cursor.execute("SELECT lastmessage FROM specific_users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result:
            return result[0]  # Return the last message time as a string
        else:
            return None  # Return None if the user is not found
    
    def check_custommessage(self, username):
        self.cursor.execute("SELECT custommessage FROM specific_users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        if result:
            custom_message = result[0]
            if custom_message is not None:
                return custom_message  # Return the custom message if it exists
            else:
                return False  # Return False if custom message is NULL
        else:
            return False  # Return False if the user is not found

    def set_custommessage(self, custommessage, username):
        self.cursor.execute("UPDATE specific_users SET custommessage = ? WHERE username = ?",(custommessage, username,))
        self.conn.commit()
        if self.cursor.rowcount == 0:
            return False
        else:
            return True

    def set_lastmessage(self, username):
        last_message_time = datetime.now().isoformat()  # Convert the datetime to a string
        self.cursor.execute("UPDATE specific_users SET lastmessage = ? WHERE username = ?", (last_message_time, username,))
        self.conn.commit()

    def remove_user(self, username):
        self.cursor.execute("DELETE FROM specific_users WHERE username = ?", (username,))
        self.conn.commit()
        if self.cursor.rowcount == 0:
            return False  # User not found, return False
        else:
            return True  # User successfully removed, return True

if __name__ == "__main__":
    db = DB()

    print(db.check_user('djmater'))
    print(db.remove_user('djmater'))
    db.conn.close()  # Close the database connection when you're done with it
