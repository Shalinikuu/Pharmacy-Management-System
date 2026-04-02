import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PharmacyManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1200x700")
        self.root.config(bg="#f0f0f0")
        
        # Database setup
        self.setup_database()
        
        # Header
        header = tk.Frame(root, bg="#2c3e50", height=80)
        header.pack(fill=tk.X)
        tk.Label(header, text="🏥 Pharmacy Management System", 
                font=("Arial", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=20)
        
        # Main container
        container = tk.Frame(root, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Menu
        menu_frame = tk.Frame(container, bg="white", width=200, relief=tk.RAISED, bd=2)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Label(menu_frame, text="MENU", font=("Arial", 16, "bold"), 
                bg="white", fg="#2c3e50").pack(pady=15)
        
        buttons = [
            ("Medicine Management", self.show_medicine_management),
            ("Stock Management", self.show_stock_management),
            ("Billing", self.show_billing),
            ("Suppliers", self.show_suppliers),
            ("Customers", self.show_customers),
            ("Reports", self.show_reports)
        ]
        
        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, command=command, 
                          width=20, bg="#3498db", fg="white", 
                          font=("Arial", 11), relief=tk.FLAT, cursor="hand2")
            btn.pack(pady=5, padx=10)
        
        # Right panel - Content area
        self.content_frame = tk.Frame(container, bg="white", relief=tk.RAISED, bd=2)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Show default screen
        self.show_medicine_management()
    
    def setup_database(self):
        self.conn = sqlite3.connect('pharmacy.db')
        self.cursor = self.conn.cursor()
        
        # Medicines table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                med_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                stock_qty INTEGER DEFAULT 0,
                expiry_date TEXT,
                supplier_id INTEGER,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            )
        ''')
        
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                email TEXT,
                address TEXT
            )
        ''')
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                cust_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                email TEXT,
                address TEXT
            )
        ''')
        
        # Sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cust_id INTEGER,
                total_amount REAL,
                sale_date TEXT,
                FOREIGN KEY (cust_id) REFERENCES customers(cust_id)
            )
        ''')
        
        # Sale items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                med_id INTEGER,
                quantity INTEGER,
                price REAL,
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
                FOREIGN KEY (med_id) REFERENCES medicines(med_id)
            )
        ''')
        
        # Purchases table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                med_id INTEGER,
                quantity INTEGER,
                cost_price REAL,
                purchase_date TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (med_id) REFERENCES medicines(med_id)
            )
        ''')
        
        self.conn.commit()
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_medicine_management(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Medicine Management", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(pady=10, padx=20, fill=tk.X)
        
        fields = [
            ("Medicine Name:", "name"),
            ("Category:", "category"),
            ("Price:", "price"),
            ("Stock Quantity:", "stock"),
            ("Expiry Date (YYYY-MM-DD):", "expiry"),
            ("Supplier ID:", "supplier")
        ]
        
        self.med_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, bg="white", font=("Arial", 10)).grid(
                row=i//2, column=(i%2)*2, sticky=tk.W, padx=5, pady=5)
            entry = tk.Entry(form_frame, width=20)
            entry.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5)
            self.med_entries[key] = entry
        
        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg="white")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Add Medicine", command=self.add_medicine, 
                 bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update", command=self.update_medicine, 
                 bg="#f39c12", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_medicine, 
                 bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_medicine_form, 
                 bg="#95a5a6", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_frame = tk.Frame(self.content_frame, bg="white")
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Category", "Price", "Stock", "Expiry", "Supplier ID")
        self.med_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.med_tree.heading(col, text=col)
            self.med_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.med_tree.yview)
        self.med_tree.configure(yscrollcommand=scrollbar.set)
        
        self.med_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.med_tree.bind('<ButtonRelease-1>', self.select_medicine)
        self.refresh_medicine_table()
    
    def add_medicine(self):
        try:
            self.cursor.execute('''
                INSERT INTO medicines (name, category, price, stock_qty, expiry_date, supplier_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.med_entries['name'].get(),
                self.med_entries['category'].get(),
                float(self.med_entries['price'].get()),
                int(self.med_entries['stock'].get()),
                self.med_entries['expiry'].get(),
                int(self.med_entries['supplier'].get()) if self.med_entries['supplier'].get() else None
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Medicine added successfully!")
            self.clear_medicine_form()
            self.refresh_medicine_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")
    
    def update_medicine(self):
        selected = self.med_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine to update")
            return
        
        try:
            med_id = self.med_tree.item(selected[0])['values'][0]
            self.cursor.execute('''
                UPDATE medicines 
                SET name=?, category=?, price=?, stock_qty=?, expiry_date=?, supplier_id=?
                WHERE med_id=?
            ''', (
                self.med_entries['name'].get(),
                self.med_entries['category'].get(),
                float(self.med_entries['price'].get()),
                int(self.med_entries['stock'].get()),
                self.med_entries['expiry'].get(),
                int(self.med_entries['supplier'].get()) if self.med_entries['supplier'].get() else None,
                med_id
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Medicine updated successfully!")
            self.clear_medicine_form()
            self.refresh_medicine_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update medicine: {str(e)}")
    
    def delete_medicine(self):
        selected = self.med_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a medicine to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this medicine?"):
            try:
                med_id = self.med_tree.item(selected[0])['values'][0]
                self.cursor.execute('DELETE FROM medicines WHERE med_id=?', (med_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Medicine deleted successfully!")
                self.clear_medicine_form()
                self.refresh_medicine_table()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete medicine: {str(e)}")
    
    def clear_medicine_form(self):
        for entry in self.med_entries.values():
            entry.delete(0, tk.END)
    
    def select_medicine(self, event):
        selected = self.med_tree.selection()
        if selected:
            values = self.med_tree.item(selected[0])['values']
            entries = ['name', 'category', 'price', 'stock', 'expiry', 'supplier']
            for i, key in enumerate(entries):
                self.med_entries[key].delete(0, tk.END)
                self.med_entries[key].insert(0, values[i+1] if values[i+1] else '')
    
    def refresh_medicine_table(self):
        for item in self.med_tree.get_children():
            self.med_tree.delete(item)
        
        self.cursor.execute('SELECT * FROM medicines')
        for row in self.cursor.fetchall():
            self.med_tree.insert('', tk.END, values=row)
    
    def show_stock_management(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Stock Management", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=15)
        
        # Purchase form
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(pady=10, padx=20)
        
        tk.Label(form_frame, text="Medicine ID:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.stock_med_id = tk.Entry(form_frame)
        self.stock_med_id.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Supplier ID:", bg="white").grid(row=0, column=2, padx=5, pady=5)
        self.stock_supp_id = tk.Entry(form_frame)
        self.stock_supp_id.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Quantity:", bg="white").grid(row=1, column=0, padx=5, pady=5)
        self.stock_qty = tk.Entry(form_frame)
        self.stock_qty.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Cost Price:", bg="white").grid(row=1, column=2, padx=5, pady=5)
        self.stock_cost = tk.Entry(form_frame)
        self.stock_cost.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Button(form_frame, text="Add Purchase", command=self.add_purchase, 
                 bg="#27ae60", fg="white").grid(row=2, column=1, columnspan=2, pady=10)
        
        # Stock table
        table_frame = tk.Frame(self.content_frame, bg="white")
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        columns = ("Med ID", "Medicine Name", "Stock", "Last Purchase", "Supplier")
        self.stock_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_stock_table()
    
    def add_purchase(self):
        try:
            med_id = int(self.stock_med_id.get())
            qty = int(self.stock_qty.get())
            
            # Add purchase record
            self.cursor.execute('''
                INSERT INTO purchases (supplier_id, med_id, quantity, cost_price, purchase_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                int(self.stock_supp_id.get()),
                med_id,
                qty,
                float(self.stock_cost.get()),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            # Update medicine stock
            self.cursor.execute('''
                UPDATE medicines SET stock_qty = stock_qty + ? WHERE med_id = ?
            ''', (qty, med_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Purchase added and stock updated!")
            
            self.stock_med_id.delete(0, tk.END)
            self.stock_supp_id.delete(0, tk.END)
            self.stock_qty.delete(0, tk.END)
            self.stock_cost.delete(0, tk.END)
            
            self.refresh_stock_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add purchase: {str(e)}")
    
    def refresh_stock_table(self):
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        self.cursor.execute('''
            SELECT m.med_id, m.name, m.stock_qty, 
                   MAX(p.purchase_date) as last_purchase,
                   s.name as supplier_name
            FROM medicines m
            LEFT JOIN purchases p ON m.med_id = p.med_id
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
            GROUP BY m.med_id
        ''')
        
        for row in self.cursor.fetchall():
            self.stock_tree.insert('', tk.END, values=row)
    
    def show_billing(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Billing System", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=15)
        
        # Customer info
        cust_frame = tk.Frame(self.content_frame, bg="white")
        cust_frame.pack(pady=10, padx=20)
        
        tk.Label(cust_frame, text="Customer ID:", bg="white").grid(row=0, column=0, padx=5)
        self.bill_cust_id = tk.Entry(cust_frame)
        self.bill_cust_id.grid(row=0, column=1, padx=5)
        
        # Add items
        item_frame = tk.Frame(self.content_frame, bg="white")
        item_frame.pack(pady=10, padx=20)
        
        tk.Label(item_frame, text="Medicine ID:", bg="white").grid(row=0, column=0, padx=5)
        self.bill_med_id = tk.Entry(item_frame, width=10)
        self.bill_med_id.grid(row=0, column=1, padx=5)
        
        tk.Label(item_frame, text="Quantity:", bg="white").grid(row=0, column=2, padx=5)
        self.bill_qty = tk.Entry(item_frame, width=10)
        self.bill_qty.grid(row=0, column=3, padx=5)
        
        tk.Button(item_frame, text="Add to Bill", command=self.add_to_bill, 
                 bg="#3498db", fg="white").grid(row=0, column=4, padx=5)
        
        # Bill items table
        bill_table_frame = tk.Frame(self.content_frame, bg="white")
        bill_table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        columns = ("Medicine", "Quantity", "Price", "Total")
        self.bill_tree = ttk.Treeview(bill_table_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.bill_tree.heading(col, text=col)
            self.bill_tree.column(col, width=150)
        
        self.bill_tree.pack(fill=tk.BOTH, expand=True)
        
        # Total and finalize
        total_frame = tk.Frame(self.content_frame, bg="white")
        total_frame.pack(pady=10)
        
        self.bill_total_label = tk.Label(total_frame, text="Total: ₹0.00", 
                                         font=("Arial", 14, "bold"), bg="white")
        self.bill_total_label.pack()
        
        tk.Button(total_frame, text="Generate Bill", command=self.generate_bill, 
                 bg="#27ae60", fg="white", font=("Arial", 12, "bold"), 
                 width=15).pack(pady=10)
        
        self.bill_items = []
        self.bill_total = 0
    
    def add_to_bill(self):
        try:
            med_id = int(self.bill_med_id.get())
            qty = int(self.bill_qty.get())
            
            # Get medicine details
            self.cursor.execute('SELECT name, price, stock_qty FROM medicines WHERE med_id=?', (med_id,))
            result = self.cursor.fetchone()
            
            if not result:
                messagebox.showerror("Error", "Medicine not found!")
                return
            
            name, price, stock = result
            
            if stock < qty:
                messagebox.showerror("Error", f"Insufficient stock! Available: {stock}")
                return
            
            total = price * qty
            self.bill_tree.insert('', tk.END, values=(name, qty, f"₹{price:.2f}", f"₹{total:.2f}"))
            
            self.bill_items.append({'med_id': med_id, 'qty': qty, 'price': price})
            self.bill_total += total
            
            self.bill_total_label.config(text=f"Total: ₹{self.bill_total:.2f}")
            
            self.bill_med_id.delete(0, tk.END)
            self.bill_qty.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")
    
    def generate_bill(self):
        if not self.bill_items:
            messagebox.showwarning("Warning", "No items in bill!")
            return
        
        try:
            cust_id = int(self.bill_cust_id.get()) if self.bill_cust_id.get() else None
            
            # Create sale record
            self.cursor.execute('''
                INSERT INTO sales (cust_id, total_amount, sale_date)
                VALUES (?, ?, ?)
            ''', (cust_id, self.bill_total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            sale_id = self.cursor.lastrowid
            
            # Add sale items and update stock
            for item in self.bill_items:
                self.cursor.execute('''
                    INSERT INTO sale_items (sale_id, med_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, item['med_id'], item['qty'], item['price']))
                
                self.cursor.execute('''
                    UPDATE medicines SET stock_qty = stock_qty - ? WHERE med_id = ?
                ''', (item['qty'], item['med_id']))
            
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Bill generated successfully!\nBill ID: {sale_id}\nTotal: ₹{self.bill_total:.2f}")
            
            # Clear bill
            for item in self.bill_tree.get_children():
                self.bill_tree.delete(item)
            
            self.bill_items = []
            self.bill_total = 0
            self.bill_total_label.config(text="Total: ₹0.00")
            self.bill_cust_id.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
    
    def show_suppliers(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Supplier Management", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=15)
        
        # Form
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(pady=10, padx=20)
        
        fields = [("Name:", "name"), ("Contact:", "contact"), 
                 ("Email:", "email"), ("Address:", "address")]
        
        self.supp_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, bg="white").grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.supp_entries[key] = entry
        
        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg="white")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Add Supplier", command=self.add_supplier, 
                 bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update", command=self.update_supplier, 
                 bg="#f39c12", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_supplier, 
                 bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_frame = tk.Frame(self.content_frame, bg="white")
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Contact", "Email", "Address")
        self.supp_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.supp_tree.heading(col, text=col)
            self.supp_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.supp_tree.yview)
        self.supp_tree.configure(yscrollcommand=scrollbar.set)
        
        self.supp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.supp_tree.bind('<ButtonRelease-1>', self.select_supplier)
        self.refresh_supplier_table()
    
    def add_supplier(self):
        try:
            self.cursor.execute('''
                INSERT INTO suppliers (name, contact, email, address)
                VALUES (?, ?, ?, ?)
            ''', (
                self.supp_entries['name'].get(),
                self.supp_entries['contact'].get(),
                self.supp_entries['email'].get(),
                self.supp_entries['address'].get()
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Supplier added successfully!")
            for entry in self.supp_entries.values():
                entry.delete(0, tk.END)
            self.refresh_supplier_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")
    
    def update_supplier(self):
        selected = self.supp_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier")
            return
        
        try:
            supp_id = self.supp_tree.item(selected[0])['values'][0]
            self.cursor.execute('''
                UPDATE suppliers SET name=?, contact=?, email=?, address=? WHERE supplier_id=?
            ''', (
                self.supp_entries['name'].get(),
                self.supp_entries['contact'].get(),
                self.supp_entries['email'].get(),
                self.supp_entries['address'].get(),
                supp_id
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Supplier updated!")
            self.refresh_supplier_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_supplier(self):
        selected = self.supp_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a supplier")
            return
        
        if messagebox.askyesno("Confirm", "Delete this supplier?"):
            try:
                supp_id = self.supp_tree.item(selected[0])['values'][0]
                self.cursor.execute('DELETE FROM suppliers WHERE supplier_id=?', (supp_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Supplier deleted!")
                self.refresh_supplier_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def select_supplier(self, event):
        selected = self.supp_tree.selection()
        if selected:
            values = self.supp_tree.item(selected[0])['values']
            keys = ['name', 'contact', 'email', 'address']
            for i, key in enumerate(keys):
                self.supp_entries[key].delete(0, tk.END)
                self.supp_entries[key].insert(0, values[i+1])
    
    def refresh_supplier_table(self):
        for item in self.supp_tree.get_children():
            self.supp_tree.delete(item)
        self.cursor.execute('SELECT * FROM suppliers')
        for row in self.cursor.fetchall():
            self.supp_tree.insert('', tk.END, values=row)
    
    def show_customers(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Customer Management", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=15)
        
        # Similar structure as suppliers
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(pady=10, padx=20)
        
        fields = [("Name:", "name"), ("Contact:", "contact"), 
                 ("Email:", "email"), ("Address:", "address")]
        
        self.cust_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, bg="white").grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.cust_entries[key] = entry
        
        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg="white")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Add Customer", command=self.add_customer, 
                 bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update", command=self.update_customer, 
                 bg="#f39c12", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_customer, 
                 bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        
        # Table
        table_frame = tk.Frame(self.content_frame, bg="white")
        table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Contact", "Email", "Address")
        self.cust_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.cust_tree.heading(col, text=col)
            self.cust_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.cust_tree.yview)
        self.cust_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cust_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cust_tree.bind('<ButtonRelease-1>', self.select_customer)
        self.refresh_customer_table()
    
    def add_customer(self):
        try:
            self.cursor.execute('''
                INSERT INTO customers (name, contact, email, address)
                VALUES (?, ?, ?, ?)
            ''', (
                self.cust_entries['name'].get(),
                self.cust_entries['contact'].get(),
                self.cust_entries['email'].get(),
                self.cust_entries['address'].get()
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Customer added successfully!")
            for entry in self.cust_entries.values():
                entry.delete(0, tk.END)
            self.refresh_customer_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
    
    def update_customer(self):
        selected = self.cust_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        try:
            cust_id = self.cust_tree.item(selected[0])['values'][0]
            self.cursor.execute('''
                UPDATE customers SET name=?, contact=?, email=?, address=? WHERE cust_id=?
            ''', (
                self.cust_entries['name'].get(),
                self.cust_entries['contact'].get(),
                self.cust_entries['email'].get(),
                self.cust_entries['address'].get(),
                cust_id
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Customer updated!")
            self.refresh_customer_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_customer(self):
        selected = self.cust_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a customer")
            return
        
        if messagebox.askyesno("Confirm", "Delete this customer?"):
            try:
                cust_id = self.cust_tree.item(selected[0])['values'][0]
                self.cursor.execute('DELETE FROM customers WHERE cust_id=?', (cust_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Customer deleted!")
                self.refresh_customer_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def select_customer(self, event):
        selected = self.cust_tree.selection()
        if selected:
            values = self.cust_tree.item(selected[0])['values']
            keys = ['name', 'contact', 'email', 'address']
            for i, key in enumerate(keys):
                self.cust_entries[key].delete(0, tk.END)
                self.cust_entries[key].insert(0, values[i+1])
    
    def refresh_customer_table(self):
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        self.cursor.execute('SELECT * FROM customers')
        for row in self.cursor.fetchall():
            self.cust_tree.insert('', tk.END, values=row)
    
    def show_reports(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Reports & Analytics", 
                font=("Arial", 18, "bold"), bg="white").pack(pady=15)
        
        # Report buttons
        report_frame = tk.Frame(self.content_frame, bg="white")
        report_frame.pack(pady=20)
        
        tk.Button(report_frame, text="Low Stock Alert", command=self.show_low_stock, 
                 bg="#e74c3c", fg="white", width=20, height=2).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(report_frame, text="Sales Report", command=self.show_sales_report, 
                 bg="#3498db", fg="white", width=20, height=2).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(report_frame, text="Expired Medicines", command=self.show_expired, 
                 bg="#f39c12", fg="white", width=20, height=2).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(report_frame, text="Top Selling Items", command=self.show_top_selling, 
                 bg="#27ae60", fg="white", width=20, height=2).grid(row=1, column=1, padx=10, pady=10)
        
        # Report display area
        self.report_frame = tk.Frame(self.content_frame, bg="white")
        self.report_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
    
    def show_low_stock(self):
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.report_frame, text="Low Stock Alert (Stock < 10)", 
                font=("Arial", 14, "bold"), bg="white", fg="#e74c3c").pack(pady=10)
        
        columns = ("ID", "Name", "Category", "Stock", "Price")
        tree = ttk.Treeview(self.report_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        self.cursor.execute('SELECT med_id, name, category, stock_qty, price FROM medicines WHERE stock_qty < 10')
        for row in self.cursor.fetchall():
            tree.insert('', tk.END, values=row)
    
    def show_sales_report(self):
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.report_frame, text="Sales Report", 
                font=("Arial", 14, "bold"), bg="white", fg="#3498db").pack(pady=10)
        
        columns = ("Sale ID", "Customer ID", "Total Amount", "Date")
        tree = ttk.Treeview(self.report_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        self.cursor.execute('SELECT * FROM sales ORDER BY sale_date DESC LIMIT 50')
        total_sales = 0
        for row in self.cursor.fetchall():
            tree.insert('', tk.END, values=row)
            total_sales += row[2]
        
        tk.Label(self.report_frame, text=f"Total Sales: ₹{total_sales:.2f}", 
                font=("Arial", 12, "bold"), bg="white", fg="#27ae60").pack(pady=10)
    
    def show_expired(self):
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.report_frame, text="Expired/Expiring Soon Medicines", 
                font=("Arial", 14, "bold"), bg="white", fg="#f39c12").pack(pady=10)
        
        columns = ("ID", "Name", "Category", "Stock", "Expiry Date")
        tree = ttk.Treeview(self.report_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        self.cursor.execute('''
            SELECT med_id, name, category, stock_qty, expiry_date 
            FROM medicines 
            WHERE expiry_date < date('now', '+30 days')
            ORDER BY expiry_date
        ''')
        for row in self.cursor.fetchall():
            tree.insert('', tk.END, values=row)
    
    def show_top_selling(self):
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.report_frame, text="Top 10 Selling Medicines", 
                font=("Arial", 14, "bold"), bg="white", fg="#27ae60").pack(pady=10)
        
        columns = ("Medicine Name", "Total Sold", "Revenue")
        tree = ttk.Treeview(self.report_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        self.cursor.execute('''
            SELECT m.name, SUM(si.quantity) as total_qty, SUM(si.quantity * si.price) as revenue
            FROM sale_items si
            JOIN medicines m ON si.med_id = m.med_id
            GROUP BY si.med_id
            ORDER BY total_qty DESC
            LIMIT 10
        ''')
        for row in self.cursor.fetchall():
            tree.insert('', tk.END, values=(row[0], row[1], f"₹{row[2]:.2f}"))
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyManagementSystem(root)
    root.mainloop()