# Restaurant Desk (Tkinter)

A local restaurant order and billing desktop app inspired by the linked restaurant management system. It uses Python's built-in `tkinter`, `sqlite3`, and standard library; no pip packages are needed.

## Features
- Dashboard with today's order count and sales
- Search menu items instantly and filter by category
- Keyboard shortcuts: Ctrl+1 dashboard, Ctrl+N new order, Ctrl+H order history, Esc reset menu filters
- Menu grouped into starters, mains, desserts, and drinks
- Live bill totals with editable GST rate
- SQLite order history, customer/order search, customer item-by-item history with lifetime spend, detailed receipts, and confirmed order deletion
- Export orders to CSV, export a receipt to text, and delete orders

## Python’s built-in Tkinter modules:
- tkinter (tk) for the window, frames, labels, buttons, and other widgets.
- tkinter.ttk (ttk) for themed widgets such as buttons, entries, scrollbars, and tables.
- tkinter.messagebox for confirmation and information pop-ups.
- tkinter.filedialog for choosing where to save CSV exports and receipt files.

## Run

From this folder:

```bash
python3 main.py
```

If `python3 -m tkinter` does not open the Tk demo, use a macOS Python distribution that includes Tcl/Tk. The app creates `restaurant.db` in this folder on first launch. Prices are in INR. Edit `MENU` and `TAX_RATE` near the top of `main.py` for your restaurant's menu and tax rules.
