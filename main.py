"""Tkinter restaurant order manager using only Python's standard library."""
import csv
import sqlite3
import tkinter as tk
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

HERE = Path(__file__).resolve().parent
DB = HERE / "restaurant.db"
TAX_RATE = Decimal("0.05")
MENU = {
    "Starters": [("Tomato soup", 90), ("Garlic bread", 110), ("Paneer tikka", 220)],
    "Mains": [("Margherita pizza", 280), ("Classic burger", 190), ("Veg biryani", 240), ("Pasta Alfredo", 260)],
    "Desserts": [("Chocolate brownie", 130), ("Vanilla ice cream", 80)],
    "Drinks": [("Fresh lime soda", 70), ("Masala chai", 40), ("Cold coffee", 120)],
    "Specials": [("Tandoori platter", 360), ("Biryani bucket", 290), ("BBQ ribs", 380), ("Cheese fondue", 310), ("Dal makhani + Naan", 220)],
    "Fast Food":[("Pani Puri",40)]
}
BG, WHITE, INK, MUTED, GREEN = "#f3f6f5", "#ffffff", "#172923", "#65736e", "#176b57"


def fmt(value):
    return "₹" + format(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ",.2f")


class App:
    def __init__(self, root):
        self.root = root
        root.title("Table & Thyme | Restaurant Desk")
        root.geometry("1150x740")
        root.minsize(940, 620)
        root.configure(bg=BG)
        self.prices = {n: p for group in MENU.values() for n, p in group}
        self._database()
        self._style()
        self.side = tk.Frame(root, bg="#16312c", width=218)
        self.side.pack(side="left", fill="y")
        self.side.pack_propagate(False)
        tk.Label(self.side, text="TABLE & THYME", bg="#16312c", fg="white", font=("Helvetica", 16, "bold")).pack(anchor="w", padx=20, pady=(28, 3))
        tk.Label(self.side, text="RESTAURANT DESK", bg="#16312c", fg="#a7c7bc", font=("Helvetica", 9, "bold")).pack(anchor="w", padx=21, pady=(0, 28))
        for label, cmd in [("Overview", self.dashboard), ("New order", self.new_order), ("Order history", self.history)]:
            tk.Button(self.side, text="  " + label, command=cmd, bg="#22453d", fg="black", activebackground=GREEN, activeforeground="black", bd=0, anchor="w", padx=12, pady=12, font=("Helvetica", 11), cursor="hand2").pack(fill="x", padx=12, pady=4)
        tk.Label(self.side, text="Tkinter · SQLite\nYour data stays on this Mac", bg="#16312c", fg="#9cb2ac", font=("Helvetica", 9), justify="left").pack(side="bottom", anchor="w", padx=20, pady=20)
        self.main = tk.Frame(root, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        root.bind_all("<Control-n>", lambda _e: self.new_order())
        root.bind_all("<Control-h>", lambda _e: self.history())
        root.bind_all("<Control-1>", lambda _e: self.dashboard())
        root.bind_all("<Escape>", lambda _e: self.clear_menu_filter())
        self.dashboard()

    def db(self):
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _database(self):
        with self.db() as con:
            con.execute("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, number TEXT UNIQUE NOT NULL, customer TEXT NOT NULL, created TEXT NOT NULL, subtotal REAL NOT NULL, tax REAL NOT NULL, total REAL NOT NULL)")
            con.execute("CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE, name TEXT NOT NULL, qty INTEGER NOT NULL, price REAL NOT NULL, amount REAL NOT NULL)")

    def _style(self):
        s = ttk.Style(); s.theme_use("clam")
        s.configure("Treeview", rowheight=32, background=WHITE, fieldbackground=WHITE, foreground=INK, borderwidth=0)
        s.configure("Treeview.Heading", background="#e6eeeb", foreground=INK, font=("Helvetica", 10, "bold"), relief="flat")
        s.map("Treeview", background=[("selected", "#d4ebe1")], foreground=[("selected", INK)])

    def clear(self):
        for w in self.main.winfo_children(): w.destroy()

    def header(self, title, subtitle):
        f = tk.Frame(self.main, bg=BG); f.pack(fill="x", padx=28, pady=(25, 17))
        tk.Label(f, text=title, bg=BG, fg=INK, font=("Helvetica", 24, "bold")).pack(anchor="w")
        tk.Label(f, text=subtitle, bg=BG, fg=MUTED, font=("Helvetica", 10)).pack(anchor="w", pady=(4, 0))

    def table(self, parent, rows, compact=False):
        tree = ttk.Treeview(parent, columns=("number", "customer", "created", "total"), show="headings", height=8 if compact else 15)
        for c, title, width in [("number", "ORDER", 190), ("customer", "CUSTOMER", 220), ("created", "DATE & TIME", 220), ("total", "TOTAL", 150)]:
            tree.heading(c, text=title); tree.column(c, width=width, anchor="e" if c == "total" else "w")
        for r in rows: tree.insert("", "end", iid=str(r["id"]), values=(r["number"], r["customer"], r["created"], fmt(r["total"])))
        tree.pack(fill="both", expand=True)
        if not compact:
            self.tree = tree
            tree.bind("<Button-1>", self.on_history_click)
            tree.bind("<Double-1>", self.on_history_double_click)
        return tree

    def dashboard(self):
        self.clear(); self.header("Good day 👋", "A clear view of today's restaurant activity.")
        day = datetime.now().strftime("%Y-%m-%d")
        with self.db() as con:
            count, sales = con.execute("SELECT COUNT(*),COALESCE(SUM(total),0) FROM orders WHERE substr(created,1,10)=?", (day,)).fetchone()
            all_count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            rows = con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 7").fetchall()
        cards = tk.Frame(self.main, bg=BG); cards.pack(fill="x", padx=28)
        for title, val, note in [("Today's orders", count, "Created today"), ("Today's sales", fmt(sales), "Including GST"), ("All-time orders", all_count, "Saved on this Mac")]:
            card = tk.Frame(cards, bg=WHITE, padx=18, pady=17, highlightbackground="#e4ebe8", highlightthickness=1); card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            tk.Label(card, text=title.upper(), bg=WHITE, fg=MUTED, font=("Helvetica", 9, "bold")).pack(anchor="w")
            tk.Label(card, text=val, bg=WHITE, fg=INK, font=("Helvetica", 22, "bold")).pack(anchor="w", pady=(7, 2))
            tk.Label(card, text=note, bg=WHITE, fg=MUTED, font=("Helvetica", 9)).pack(anchor="w")
        section = tk.Frame(self.main, bg=BG); section.pack(fill="both", expand=True, padx=28, pady=24)
        tk.Label(section, text="Recent orders", bg=BG, fg=INK, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 10))
        self.table(section, rows, True)
        ttk.Button(section, text="View all orders", command=self.history).pack(anchor="e", pady=10)

    def new_order(self):
        self.clear(); self.header("Create an order", "Select quantities to see the bill update instantly.")
        wrap = tk.Frame(self.main, bg=BG); wrap.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        left = tk.Frame(wrap, bg=WHITE, padx=18, pady=16, highlightbackground="#e4ebe8", highlightthickness=1); left.pack(side="left", fill="both", expand=True, padx=(0, 14))
        right = tk.Frame(wrap, bg=WHITE, width=280, padx=18, pady=18, highlightbackground="#e4ebe8", highlightthickness=1); right.pack(side="right", fill="y"); right.pack_propagate(False)
        tk.Label(left, text="Customer", bg=WHITE, fg=INK, font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.customer = tk.StringVar(value="Walk-in"); ttk.Entry(left, textvariable=self.customer).pack(fill="x", pady=(5, 12))
        canvas = tk.Canvas(left, bg=WHITE, highlightthickness=0); scroll = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=WHITE); body.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        self.menu_window = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(self.menu_window, width=event.width))
        self.vars = {name: tk.IntVar(value=0) for name in self.prices}
        for var in self.vars.values():
            var.trace_add("write", lambda *_: self.update_total())
        toolbar = tk.Frame(left, bg=WHITE); toolbar.pack(fill="x", pady=(0, 10))
        tk.Label(toolbar, text="Find an item", bg=WHITE, fg=INK, font=("Helvetica", 9, "bold")).pack(side="left", padx=(0, 8))
        self.menu_search = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.menu_search)
        search_entry.pack(side="left", fill="x", expand=True)
        self.category_var = tk.StringVar(value="All categories")
        categories = ttk.Combobox(toolbar, textvariable=self.category_var, state="readonly", width=17,
                                  values=("All categories", *MENU.keys()))
        categories.pack(side="right", padx=(8, 0))
        canvas.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        self.menu_canvas, self.menu_body = canvas, body
        self.menu_search.trace_add("write", lambda *_: self.render_menu())
        self.category_var.trace_add("write", lambda *_: self.render_menu())
        self.render_menu()
        tk.Label(right, text="Bill summary", bg=WHITE, fg=INK, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 16))
        self.sub_v, self.tax_v, self.total_v = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.summary(right, "Subtotal", self.sub_v); self.summary(right, "GST · 5%", self.tax_v)
        ttk.Separator(right).pack(fill="x", pady=11); self.summary(right, "Total", self.total_v, True)
        tk.Label(right, text="Change TAX_RATE in main.py to adjust GST.", bg=WHITE, fg=MUTED, font=("Helvetica", 8)).pack(anchor="w", pady=(8, 16))
        ttk.Button(right, text="Save order", command=self.save_order).pack(fill="x", ipady=7)
        ttk.Button(right, text="Clear quantities", command=lambda: [v.set(0) for v in self.vars.values()]).pack(fill="x", pady=8, ipady=5)
        self.update_total()

    def render_menu(self):
        """Draw menu rows in a shared grid so prices and quantity controls align."""
        if not hasattr(self, "menu_body") or not self.menu_body.winfo_exists():
            return
        for child in self.menu_body.winfo_children():
            child.destroy()
        self.menu_body.grid_columnconfigure(0, weight=1, minsize=180)
        self.menu_body.grid_columnconfigure(1, weight=0, minsize=122)
        self.menu_body.grid_columnconfigure(2, weight=0, minsize=104)
        query = self.menu_search.get().strip().casefold()
        category = self.category_var.get()
        row_index = 0
        matches = 0
        for group, entries in MENU.items():
            if category != "All categories" and group != category:
                continue
            visible = [(name, price) for name, price in entries if query in name.casefold()]
            if not visible:
                continue
            matches += len(visible)
            tk.Label(self.menu_body, text=group, bg=WHITE, fg=GREEN,
                     font=("Helvetica", 11, "bold")).grid(row=row_index, column=0,
                     columnspan=3, sticky="w", padx=8, pady=(12, 5))
            row_index += 1
            for name, price in visible:
                tk.Label(self.menu_body, text=name, bg=WHITE, fg=INK,
                         font=("Helvetica", 10)).grid(row=row_index, column=0,
                         sticky="w", padx=8, pady=7)
                qty_controls = tk.Frame(self.menu_body, bg=WHITE)
                qty_controls.grid(row=row_index, column=1, sticky="e", padx=4, pady=4)
                ttk.Button(qty_controls, text="−", width=3,
                           command=lambda item=name: self.change_quantity(item, -1)).pack(side="left")
                tk.Label(qty_controls, textvariable=self.vars[name], bg="#edf3f0", fg=INK,
                         width=3, font=("Helvetica", 10, "bold")).pack(side="left", ipady=4, padx=3)
                ttk.Button(qty_controls, text="+", width=3,
                           command=lambda item=name: self.change_quantity(item, 1)).pack(side="left")
                tk.Label(self.menu_body, text=fmt(price), bg=WHITE, fg=MUTED,
                         font=("Helvetica", 10)).grid(row=row_index, column=2,
                         sticky="e", padx=10, pady=7)
                row_index += 1
        if not matches:
            tk.Label(self.menu_body, text="No menu items match. Try another search.",
                     bg=WHITE, fg=MUTED, font=("Helvetica", 10)).grid(
                         row=0, column=0, columnspan=3, sticky="w", padx=8, pady=16)

    def change_quantity(self, item, amount):
        """Adjust an order quantity, keeping it between zero and 99."""
        variable = self.vars[item]
        variable.set(min(99, max(0, int(variable.get() or 0) + amount)))
        self.update_total()

    def clear_menu_filter(self):
        """Escape clears an active menu search and restores every category."""
        if hasattr(self, "menu_search") and self.menu_search.winfo_exists():
            self.menu_search.set("")
            self.category_var.set("All categories")
            return "break"

    def summary(self, parent, label, var, bold=False):
        row = tk.Frame(parent, bg=WHITE); row.pack(fill="x", pady=5); font = ("Helvetica", 10, "bold" if bold else "normal")
        tk.Label(row, text=label, bg=WHITE, fg=INK, font=font).pack(side="left"); tk.Label(row, textvariable=var, bg=WHITE, fg=INK, font=font).pack(side="right")

    def totals(self):
        sub = sum(Decimal(str(self.prices[n])) * max(0, int(v.get() or 0)) for n, v in self.vars.items())
        tax = (sub * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return sub, tax, sub + tax

    def update_total(self):
        if hasattr(self, "vars") and hasattr(self, "sub_v"):
            a, b, c = self.totals(); self.sub_v.set(fmt(a)); self.tax_v.set(fmt(b)); self.total_v.set(fmt(c))

    def save_order(self):
        selected = [(n, int(v.get() or 0), self.prices[n]) for n, v in self.vars.items() if int(v.get() or 0) > 0]
        if not selected: return messagebox.showwarning("No items", "Choose at least one menu item.")
        sub, tax, total = self.totals(); now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
        number = datetime.now().strftime("ORD-%y%m%d-%H%M%S"); customer = self.customer.get().strip() or "Walk-in"
        try:
            with self.db() as con:
                cur = con.execute("INSERT INTO orders(number,customer,created,subtotal,tax,total) VALUES(?,?,?,?,?,?)", (number, customer, now, float(sub), float(tax), float(total)))
                con.executemany("INSERT INTO items(order_id,name,qty,price,amount) VALUES(?,?,?,?,?)", [(cur.lastrowid, n, q, p, p*q) for n,q,p in selected])
        except sqlite3.Error as e: return messagebox.showerror("Save failed", str(e))
        self.dashboard(); messagebox.showinfo("Order saved", f"{number} saved for {fmt(total)}.")

    def history(self):
        self.clear(); self.header("Order history", "Click a customer name to see everything they ordered. Double-click an order for its receipt.")
        bar = tk.Frame(self.main, bg=BG); bar.pack(fill="x", padx=28, pady=(0, 12))
        self.search = tk.StringVar(); ttk.Entry(bar, textvariable=self.search, width=38).pack(side="left")
        ttk.Button(bar, text="Export CSV", command=self.export_csv).pack(side="right", padx=(8, 0))
        ttk.Button(bar, text="Delete selected", command=self.delete_selected_order).pack(side="right")
        box = tk.Frame(self.main, bg=BG); box.pack(fill="both", expand=True, padx=28, pady=(0, 25)); self.table(box, [])
        self.search.trace_add("write", lambda *_: self.load_history()); self.load_history()

    def load_history(self):
        if not hasattr(self, "tree") or not self.tree.winfo_exists(): return
        term = "%" + self.search.get().strip() + "%"
        with self.db() as con: rows = con.execute("SELECT * FROM orders WHERE number LIKE ? OR customer LIKE ? ORDER BY id DESC", (term, term)).fetchall()
        self.tree.delete(*self.tree.get_children())
        for r in rows: self.tree.insert("", "end", iid=str(r["id"]), values=(r["number"], r["customer"], r["created"], fmt(r["total"])))

    def on_history_click(self, event):
        """A single click on the customer column opens that customer's history."""
        tree = event.widget
        row_id = tree.identify_row(event.y)
        if not row_id or tree.identify_column(event.x) != "#2":
            return
        if getattr(self, "_pending_customer_open", None):
            self.root.after_cancel(self._pending_customer_open)
        tree.selection_set(row_id)
        customer = tree.item(row_id, "values")[1]
        self._pending_customer_open = self.root.after(
            280, lambda name=customer: self.customer_history(name)
        )

    def on_history_double_click(self, event):
        """A double click opens the selected order receipt."""
        if getattr(self, "_pending_customer_open", None):
            self.root.after_cancel(self._pending_customer_open)
            self._pending_customer_open = None
        row_id = event.widget.identify_row(event.y)
        if row_id:
            self.receipt(row_id)

    def customer_history(self, customer):
        """Show every saved item for this customer, with order and lifetime totals."""
        with self.db() as con:
            orders = con.execute(
                "SELECT id, number, created, total FROM orders "
                "WHERE customer = ? COLLATE NOCASE ORDER BY id DESC", (customer,)
            ).fetchall()
            items = con.execute(
                "SELECT o.id AS order_id, o.number, o.created, o.total AS order_total, "
                "i.name, i.qty, i.price, i.amount FROM orders o "
                "JOIN items i ON i.order_id = o.id "
                "WHERE o.customer = ? COLLATE NOCASE ORDER BY o.id DESC, i.id", (customer,)
            ).fetchall()
        lifetime_total = sum((Decimal(str(order["total"])) for order in orders), Decimal("0"))
        units = sum(item["qty"] for item in items)
        self.clear()
        self.header(f"Orders for {customer}", "Every item saved under this customer name. Double-click an item row to open its order receipt.")

        cards = tk.Frame(self.main, bg=BG); cards.pack(fill="x", padx=28, pady=(0, 18))
        for title, value in [("Orders", len(orders)), ("Items ordered", units), ("Total spent", fmt(lifetime_total))]:
            card = tk.Frame(cards, bg=WHITE, padx=18, pady=14,
                            highlightbackground="#e4ebe8", highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            tk.Label(card, text=title.upper(), bg=WHITE, fg=MUTED,
                     font=("Helvetica", 9, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg=WHITE, fg=INK,
                     font=("Helvetica", 20, "bold")).pack(anchor="w", pady=(5, 0))

        box = tk.Frame(self.main, bg=BG)
        box.pack(fill="both", expand=True, padx=28, pady=(0, 18))
        columns = ("created", "number", "item", "qty", "price", "amount", "order_total")
        tree = ttk.Treeview(box, columns=columns, show="headings", height=15)
        specs = [("created", "DATE & TIME", 155), ("number", "ORDER", 175),
                 ("item", "ITEM ORDERED", 220), ("qty", "QTY", 65),
                 ("price", "UNIT PRICE", 115), ("amount", "ITEM TOTAL", 120),
                 ("order_total", "ORDER TOTAL", 125)]
        for column, title, width in specs:
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor="w" if column in ("created", "number", "item") else "e")
        box.grid_columnconfigure(0, weight=1); box.grid_rowconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(box, orient="vertical", command=tree.yview)
        scroll.grid(row=0, column=1, sticky="ns"); tree.configure(yscrollcommand=scroll.set)
        seen_orders = set()
        self.customer_item_orders = {}
        for index, item in enumerate(items):
            order_id = item["order_id"]
            order_total = fmt(item["order_total"]) if order_id not in seen_orders else ""
            seen_orders.add(order_id)
            row_id = f"{order_id}-{index}"
            tree.insert("", "end", iid=row_id, values=(item["created"], item["number"],
                        item["name"], item["qty"], fmt(item["price"]), fmt(item["amount"]), order_total))
            self.customer_item_orders[row_id] = order_id
        tree.bind("<Double-1>", lambda event: self.receipt(
            self.customer_item_orders.get(event.widget.identify_row(event.y))
        ))
        ttk.Button(self.main, text="Back to order history", command=self.history).pack(anchor="w", padx=28, pady=(0, 20))

    def receipt(self, order_id):
        if not order_id: return
        with self.db() as con:
            order = con.execute("SELECT * FROM orders WHERE id=?", (int(order_id),)).fetchone()
            items = con.execute("SELECT * FROM items WHERE order_id=?", (int(order_id),)).fetchall()
        if not order: return
        self.clear(); self.header("Order receipt", f"{order['number']}  ·  {order['created']}")
        card = tk.Frame(self.main, bg=WHITE, padx=25, pady=20, highlightbackground="#e4ebe8", highlightthickness=1); card.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        tk.Label(card, text=order["customer"], bg=WHITE, fg=INK, font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 12))
        tree = ttk.Treeview(card, columns=("item", "qty", "price", "amount"), show="headings", height=10)
        for c,t,w in [("item","ITEM",350),("qty","QTY",80),("price","UNIT PRICE",140),("amount","AMOUNT",150)]: tree.heading(c,text=t); tree.column(c,width=w,anchor="e" if c!="item" else "w")
        for it in items: tree.insert("","end",values=(it["name"],it["qty"],fmt(it["price"]),fmt(it["amount"])))
        tree.pack(fill="x", pady=(0, 15))
        for label,key in [("Subtotal","subtotal"),("GST","tax"),("Total","total")]: tk.Label(card,text=f"{label}:  {fmt(order[key])}",bg=WHITE,fg=INK,font=("Helvetica",11,"bold" if key=="total" else "normal")).pack(anchor="e",pady=2)
        actions=tk.Frame(card,bg=WHITE); actions.pack(fill="x",pady=(22,0))
        ttk.Button(actions,text="Back to history",command=self.history).pack(side="left")
        ttk.Button(actions,text="Save receipt as text",command=lambda:self.export_receipt(order,items)).pack(side="left",padx=8)
        ttk.Button(actions,text="Delete order",command=lambda:self.delete_order(order["id"])).pack(side="right")

    def export_receipt(self, order, items):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=order["number"]+".txt", filetypes=[("Text file","*.txt")])
        if not path: return
        lines=["TABLE & THYME",order["number"],f"Customer: {order['customer']}",f"Date: {order['created']}",""]
        lines += [f"{it['name']}  x{it['qty']}  {fmt(it['amount'])}" for it in items]
        lines += ["",f"Subtotal: {fmt(order['subtotal'])}",f"GST: {fmt(order['tax'])}",f"TOTAL: {fmt(order['total'])}","","Thank you for dining with us!"]
        Path(path).write_text("\n".join(lines), encoding="utf-8"); messagebox.showinfo("Receipt exported", "Receipt saved.")

    def delete_selected_order(self):
        """Delete the selected history row and its item lines after confirmation."""
        selection = self.tree.selection() if hasattr(self, "tree") and self.tree.winfo_exists() else ()
        if not selection:
            messagebox.showinfo("Select an order", "Choose an order in the list first.")
            return
        order_id = int(selection[0])
        number = self.tree.item(selection[0], "values")[0]
        if messagebox.askyesno("Delete order", f"Permanently delete {number} and its items?"):
            with self.db() as con:
                con.execute("DELETE FROM orders WHERE id=?", (order_id,))
            self.load_history()

    def delete_order(self, order_id):
        if messagebox.askyesno("Delete order", "Permanently delete this order and its items?"):
            with self.db() as con: con.execute("DELETE FROM orders WHERE id=?", (order_id,))
            self.history()

    def export_csv(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",initialfile="restaurant-orders.csv",filetypes=[("CSV file","*.csv")])
        if not path:return
        with self.db() as con: rows=con.execute("SELECT number,customer,created,subtotal,tax,total FROM orders ORDER BY id DESC").fetchall()
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            writer=csv.writer(f);writer.writerow(["Order number","Customer","Date and time","Subtotal","GST","Total"]);writer.writerows([tuple(row) for row in rows])
        messagebox.showinfo("Export complete",f"Exported {len(rows)} orders.")


if __name__ == "__main__":
    root=tk.Tk(); App(root); root.mainloop()
