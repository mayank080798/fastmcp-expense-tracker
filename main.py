import os
import random
import sqlite3
from fastmcp import FastMCP

# Constants
DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

# Create a FastMCP instance
mcp = FastMCP(name="Expense Tracker MCP")

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

################# Init Database #################
def init_db():
    '''Initialize the SQLite database and create the expenses table if it doesn't exist.'''
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

init_db()

################# Tools for Expense Tracker #################
@mcp.tool()
def add_expense(date: str, amount: float, category: str, subcategory: str = '', note: str = ''):
    '''Add a new expense to the database.'''
    id = 0
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
                   (date, amount, category, subcategory, note))
    id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"status": "success", "ID": id}

@mcp.tool()
def list_expenses(start_date: str, end_date: str):
    '''List expense entries within an inclusive date range.'''

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, date, amount, category, subcategory, note
        FROM expenses
        WHERE date BETWEEN ? AND ?
        order by id ASC
        """,
        (start_date, end_date)
    )

    expenses = cursor.fetchall()
    conn.close()
    return expenses

@mcp.tool()
def summarize_expenses(start_date: str, end_date: str, category: str = None):
    '''Summarize total expenses by category within an inclusive date range.'''
    query = """
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """
    params = [start_date, end_date]

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " GROUP BY category ORDER BY category ASC"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    summary = cursor.fetchall()
    conn.close()
    return summary
    
                   
################# Resources for Expense Tracker #################
@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run(transport="http", host="localhost", port=8000)
