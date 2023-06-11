import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)


class Database:
    def __init__(self, db_file: str = 'database.db'):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS accounts
                                (username TEXT PRIMARY KEY,
                                image BLOB,
                                sex TEXT,
                                mail TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS statistics
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 username TEXT,
                                 num_games INTEGER,
                                 num_wins INTEGER,
                                 num_losses INTEGER)''')
        self.conn.commit()

    def add_player(self, username):
        self.cursor.execute('INSERT INTO statistics(username, num_games, num_wins, num_losses) VALUES (?, 0, 0, 0)', (username,))
        self.conn.commit()

    def get_player_stats(self, username):
        self.cursor.execute('SELECT * FROM statistics WHERE username=?', (username,))
        row = self.cursor.fetchone()
        if row:
            stats = {
                'username': row[0],
                'num_games': row[1],
                'num_wins': row[2],
                'num_losses': row[3]
            }
            return stats
        else:
            return {'error': 'Player not found'}

    def get_player_account(self, username):
        self.cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
        row = self.cursor.fetchone()
        if row:
            account = {
                'username': row[0],
                'image': row[1],
                'sex': row[2],
                'mail': row[3]
            }
            return account
        else:
            return {'error': 'Account not found'}


    def update_player_stats(self, username, result):
        if result == 'win':
            self.cursor.execute('UPDATE statistics SET num_games=num_games+1, num_wins=num_wins+1 WHERE username=?', (username,))
        elif result == 'loss':
            self.cursor.execute('UPDATE statistics SET num_games=num_games+1, num_losses=num_losses+1 WHERE username=?', (username,))
        else:
            return {'error': 'Invalid result'}
        self.conn.commit()

    def delete_player(self, username):
        self.cursor.execute('DELETE FROM statistics WHERE username=?', (username,))
        self.conn.commit()

    def select_all_accounts(self, page: int):
        self.cursor.execute('SELECT * FROM accounts')
        accounts = []
        rows = self.cursor.fetchall()
        if len(rows) < 20 * page:
            return jsonify({'error': 'invalid page number'})
        for row in rows[page * 20:page * 20 + 20]:
            account = {
                'username': row[0],
                'image': row[1],
                'sex': row[2],
                'mail': row[3]
            }
            accounts.append(account)
        return 

    def select_account(self):
        self.cursor.execute('SELECT * FROM accounts')
        return self.cursor.fetchall()

    def insert_account(self, account_info):
        username = account_info.get('username')
        if username is None:
            return {'error': 'provider username'}
        self.cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
        row = self.cursor.fetchone()
        if not row:
            new_account = {
                'username': account_info['username'],
                'image': account_info.get('image', row[1]),
                'sex': account_info.get('sex', row[2]),
                'mail': account_info.get('mail', row[3])
            }
            self.cursor.execute('INSERT INTO accounts VALUES (?, ?, ?, ?)',
                    (new_account['username'], new_account['image'], new_account['sex'], new_account['mail']))
            self.conn.commit()
            return new_account
        return {'error': 'account with such username already exists'}
 
    def update_account(self, username, account_info):
        self.cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
        row = self.cursor.fetchone()
        if row:
            updated_account = {
                'username': username,
                'image': account_info.get('image', row[1]),
                'sex': account_info.get('sex', row[2]),
                'mail': account_info.get('mail', row[3])
            }
            self.cursor.execute('UPDATE accounts SET image=?, sex=?, mail=? WHERE username=?',
                    (updated_account['image'], updated_account['sex'], updated_account['mail'], username))
            self.conn.commit()
            return updated_account
        else:
            return {'error': 'Account not found'}

    
    def delete_account(self, username):
        self.cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
        row = self.cursor.fetchone()
        if row:
            self.cursor.execute('DELETE FROM accounts WHERE username=?', (username,))
            self.conn.commit()
            return {'message': 'Account deleted'}
        else:
            return {'error': 'Account not found'}


db = Database()

# GET all accounts
@app.route('/accounts', methods=['GET'])
def get_accounts():
    return jsonify(db.select_all_accounts(0))


# GET all accounts with page
@app.route('/accounts/<int:page>', methods=['GET'])
def get_accounts(page):
    return jsonify(db.select_all_accounts(page))


# GET one account by username
@app.route('/accounts/<string:username>', methods=['GET'])
def get_account(username):
    return jsonify(db.get_player_account(username))


# POST a new account
@app.route('/accounts', methods=['POST'])
def create_account():
    return jsonify(db.insert_account(request.json))


# PUT an existing account by username
@app.route('/accounts/<string:username>', methods=['PUT'])
def update_account(username):
    return jsonify(db.update_account(username, request.json))


# DELETE an account by username
@app.route('/accounts/<string:username>', methods=['DELETE'])
def delete_account(username):
    return jsonify(db.delete_account(username))


if __name__ == '__main__':
    app.run(debug=True)
