import sys
import os
import json
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ---------------------------
# InventoryManager: Data management class
# ---------------------------
class InventoryManager:
    def __init__(self):
        self.products = []  # Each product: {name, quantity, price, cost, restock_threshold}
        self.sales = []  # Each sale: {product, quantity, revenue, profit, day}
        self.total_revenue = 0.0
        self.total_profit = 0.0
        self.data_file = "products.json"
        self.sales_file = "sales.json"
        self.time_file = "time.json"
        self.current_day = 1
        self.load_time()
        self.load_products()
        self.load_sales()
        self.calculate_totals()

    def load_time(self):
        if os.path.exists(self.time_file):
            try:
                with open(self.time_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_day = data.get("current_day", 1)
            except Exception as e:
                print("Failed to load time:", e)
        else:
            self.current_day = 1

    def save_time(self):
        try:
            with open(self.time_file, "w", encoding="utf-8") as f:
                json.dump({"current_day": self.current_day}, f, ensure_ascii=False, indent=4)
            print("Time saved!")
        except Exception as e:
            print("Failed to save time:", e)

    def advance_day(self):
        self.current_day += 1
        self.save_time()

    def load_products(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.products = json.load(f)
                print("Product data loaded!")
            except Exception as e:
                print("Failed to load product data:", e)

    def save_products(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.products, f, ensure_ascii=False, indent=4)
            print("Product data saved!")
        except Exception as e:
            print("Failed to save product data:", e)

    def load_sales(self):
        if os.path.exists(self.sales_file):
            try:
                with open(self.sales_file, "r", encoding="utf-8") as f:
                    self.sales = json.load(f)
                print("Sales records loaded!")
            except Exception as e:
                print("Failed to load sales records:", e)

    def save_sales(self):
        try:
            with open(self.sales_file, "w", encoding="utf-8") as f:
                json.dump(self.sales, f, ensure_ascii=False, indent=4)
            print("Sales records saved!")
        except Exception as e:
            print("Failed to save sales records:", e)

    def calculate_totals(self):
        # Recalculate total revenue and profit based on loaded sales
        self.total_revenue = sum(sale.get("revenue", 0) for sale in self.sales)
        self.total_profit = sum(sale.get("profit", 0) for sale in self.sales)

    def add_product(self, product):
        self.products.append(product)
        self.save_products()

    def edit_product(self, index, new_product):
        if 0 <= index < len(self.products):
            self.products[index] = new_product
            self.save_products()

    def record_sale(self, product_index, quantity):
        if 0 <= product_index < len(self.products):
            product = self.products[product_index]
            if quantity > product["quantity"]:
                return False, "Insufficient stock!"
            product["quantity"] -= quantity
            revenue = quantity * product["price"]
            profit = quantity * (product["price"] - product.get("cost", 0))
            self.total_revenue += revenue
            self.total_profit += profit
            sale_record = {
                "product": product["name"],
                "quantity": quantity,
                "revenue": revenue,
                "profit": profit,
                "day": self.current_day
            }
            self.sales.append(sale_record)
            self.save_products()  # Update inventory
            self.save_sales()  # Persist sales record
            return True, "Sale recorded successfully!"
        else:
            return False, "Invalid product index!"

    def get_sales_summary(self):
        # Returns a dictionary: product name -> total quantity sold (0 if no sale)
        summary = {}
        for product in self.products:
            summary[product["name"]] = 0
        for sale in self.sales:
            name = sale["product"]
            summary[name] = summary.get(name, 0) + sale["quantity"]
        return summary

    def get_best_selling(self):
        summary = self.get_sales_summary()
        if summary:
            best_product = max(summary, key=summary.get)
            return best_product, summary[best_product]
        return None, 0

    def get_worst_selling(self):
        summary = self.get_sales_summary()
        if summary:
            worst_product = min(summary, key=summary.get)
            return worst_product, summary[worst_product]
        return None, 0

    def check_restock(self):
        # Returns a list of product names that are below threshold
        alerts = []
        for product in self.products:
            threshold = product.get("restock_threshold", 10)
            if product["quantity"] < threshold:
                alerts.append(product["name"])
        return alerts


# ---------------------------
# ProductDialog: Dialog for adding/editing products
# ---------------------------
class ProductDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Product Information")
        self.resize(300, 200)
        self.initUI(product)

    def initUI(self, product):
        layout = QtWidgets.QFormLayout(self)

        self.edit_name = QtWidgets.QLineEdit()
        self.spin_quantity = QtWidgets.QSpinBox()
        self.spin_quantity.setRange(0, 10000)
        self.spin_price = QtWidgets.QDoubleSpinBox()
        self.spin_price.setRange(0, 10000)
        self.spin_price.setDecimals(2)
        self.spin_cost = QtWidgets.QDoubleSpinBox()
        self.spin_cost.setRange(0, 10000)
        self.spin_cost.setDecimals(2)
        self.spin_restock = QtWidgets.QSpinBox()
        self.spin_restock.setRange(0, 10000)

        layout.addRow("Name:", self.edit_name)
        layout.addRow("Quantity:", self.spin_quantity)
        layout.addRow("Price:", self.spin_price)
        layout.addRow("Cost:", self.spin_cost)
        layout.addRow("Restock Threshold:", self.spin_restock)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)

        if product:
            self.edit_name.setText(product.get("name", ""))
            self.spin_quantity.setValue(product.get("quantity", 0))
            self.spin_price.setValue(product.get("price", 0.0))
            self.spin_cost.setValue(product.get("cost", 0.0))
            self.spin_restock.setValue(product.get("restock_threshold", 10))

    def get_product_data(self):
        return {
            "name": self.edit_name.text(),
            "quantity": self.spin_quantity.value(),
            "price": self.spin_price.value(),
            "cost": self.spin_cost.value(),
            "restock_threshold": self.spin_restock.value()
        }


# ---------------------------
# MainWindow: Main GUI window with tabs and time control
# ---------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory and Sales Management System")
        self.resize(1800, 1200)  # <-- Modified: make the initial window larger
        self.manager = InventoryManager()
        self.alerted_products = set()  # To record products alerted in the current day
        self.initUI()
        self.check_alerts_initial()
        self.update_status_bar()

    def initUI(self):
        # ------------------------------
        # 1) 创建一个较大的字体
        # ------------------------------
        big_font = QtGui.QFont()
        big_font.setPointSize(14)  # 可根据需求调整字号

        # Create main toolbar on the LEFT side
        self.toolbar = QtWidgets.QToolBar("Time Toolbar")
        self.toolbar.setFont(big_font)  # 给整个toolbar设置大字体
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        self.toolbar.setMovable(False)

        # "Advance Day" button
        self.advance_day_action = QtWidgets.QAction("Advance Day", self)
        self.advance_day_action.setFont(big_font)  # 设置按钮的字体
        self.advance_day_action.triggered.connect(self.advance_day)
        self.toolbar.addAction(self.advance_day_action)

        # A label to show current day in the toolbar
        self.day_label = QtWidgets.QLabel(f"Day: {self.manager.current_day}")
        self.day_label.setFont(big_font)  # 设置标签的字体
        self.toolbar.addWidget(self.day_label)

        # Central tab widget
        self.tabs = QtWidgets.QTabWidget()
        # 设置tab标签字体
        self.tabs.tabBar().setFont(big_font)
        self.setCentralWidget(self.tabs)

        # Tab 1: Product Management
        self.tab_products = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_products, "Product Management")
        self.initProductTab()

        # Tab 2: Sales Records
        self.tab_sales = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_sales, "Sales Records")
        self.initSalesTab()

        # Tab 3: Sales Analysis
        self.tab_analysis = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_analysis, "Sales Analysis")
        self.initAnalysisTab()

    def update_status_bar(self):
        self.statusBar().showMessage(f"Current Day: {self.manager.current_day}")

    # ---------------------------
    # Product Management Tab
    # ---------------------------
    def initProductTab(self):
        layout = QtWidgets.QVBoxLayout()

        self.table_products = QtWidgets.QTableWidget()
        self.table_products.setColumnCount(5)
        self.table_products.setHorizontalHeaderLabels(["Name", "Quantity", "Price", "Cost", "Restock Threshold"])
        self.table_products.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_products)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_add_product = QtWidgets.QPushButton("Add Product")
        self.btn_edit_product = QtWidgets.QPushButton("Edit Selected Product")
        self.btn_refresh_products = QtWidgets.QPushButton("Refresh")
        btn_layout.addWidget(self.btn_add_product)
        btn_layout.addWidget(self.btn_edit_product)
        btn_layout.addWidget(self.btn_refresh_products)
        layout.addLayout(btn_layout)

        self.tab_products.setLayout(layout)

        self.btn_add_product.clicked.connect(self.add_product)
        self.btn_edit_product.clicked.connect(self.edit_product)
        self.btn_refresh_products.clicked.connect(self.load_products_to_table)

        self.load_products_to_table()

    def load_products_to_table(self):
        products = self.manager.products
        self.table_products.setRowCount(len(products))
        for row, product in enumerate(products):
            self.table_products.setItem(row, 0, QtWidgets.QTableWidgetItem(product.get("name", "")))
            self.table_products.setItem(row, 1, QtWidgets.QTableWidgetItem(str(product.get("quantity", 0))))
            self.table_products.setItem(row, 2, QtWidgets.QTableWidgetItem(str(product.get("price", 0.0))))
            self.table_products.setItem(row, 3, QtWidgets.QTableWidgetItem(str(product.get("cost", 0.0))))
            self.table_products.setItem(row, 4, QtWidgets.QTableWidgetItem(str(product.get("restock_threshold", 10))))

    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            product = dialog.get_product_data()
            self.manager.add_product(product)
            self.load_products_to_table()
            self.update_product_combo()

    def edit_product(self):
        selected = self.table_products.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Alert", "Please select a product to edit")
            return
        row = selected[0].row()
        product = self.manager.products[row]
        dialog = ProductDialog(self, product)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_product = dialog.get_product_data()
            self.manager.edit_product(row, new_product)
            self.load_products_to_table()
            self.update_product_combo()

    # ---------------------------
    # Sales Records Tab
    # ---------------------------
    def initSalesTab(self):
        layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()

        # Increase font size and make bold
        bold_font = QtGui.QFont()
        bold_font.setPointSize(12)
        bold_font.setBold(True)

        self.combo_products = QtWidgets.QComboBox()
        self.combo_products.setFont(bold_font)
        self.update_product_combo()

        self.spin_quantity = QtWidgets.QSpinBox()
        self.spin_quantity.setRange(1, 1000)
        self.spin_quantity.setFont(bold_font)

        form_layout.addRow("Select Product:", self.combo_products)
        form_layout.addRow("Sale Quantity:", self.spin_quantity)

        layout.addLayout(form_layout)

        self.btn_record_sale = QtWidgets.QPushButton("Record Sale")
        self.btn_record_sale.setFont(bold_font)
        layout.addWidget(self.btn_record_sale)
        self.btn_record_sale.clicked.connect(self.record_sale)

        self.table_sales = QtWidgets.QTableWidget()
        self.table_sales.setColumnCount(5)
        self.table_sales.setHorizontalHeaderLabels(["Product", "Quantity", "Revenue", "Profit", "Day"])
        self.table_sales.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_sales)

        self.tab_sales.setLayout(layout)
        self.load_sales_to_table()

    def update_product_combo(self):
        self.combo_products.clear()
        for product in self.manager.products:
            self.combo_products.addItem(product.get("name", ""))

    def record_sale(self):
        index = self.combo_products.currentIndex()
        quantity = self.spin_quantity.value()
        success, message = self.manager.record_sale(index, quantity)
        if success:
            QtWidgets.QMessageBox.information(self, "Success", message)
            self.load_products_to_table()
            self.load_sales_to_table()
            self.check_sale_alert(index)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", message)

    def load_sales_to_table(self):
        sales = self.manager.sales
        self.table_sales.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            self.table_sales.setItem(row, 0, QtWidgets.QTableWidgetItem(sale.get("product", "")))
            self.table_sales.setItem(row, 1, QtWidgets.QTableWidgetItem(str(sale.get("quantity", 0))))
            self.table_sales.setItem(row, 2, QtWidgets.QTableWidgetItem(f"{sale.get('revenue', 0):.2f}"))
            self.table_sales.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{sale.get('profit', 0):.2f}"))
            self.table_sales.setItem(row, 4, QtWidgets.QTableWidgetItem(str(sale.get("day", 1))))

    def check_sale_alert(self, product_index):
        product = self.manager.products[product_index]
        if product["quantity"] < product.get("restock_threshold", 10):
            if product["name"] not in self.alerted_products:
                QtWidgets.QMessageBox.information(
                    self,
                    "Restock Alert",
                    f"Product {product['name']} is low on stock ({product['quantity']} units remaining)."
                )
                self.alerted_products.add(product["name"])

    def check_alerts_initial(self):
        # At startup, check all products for low stock and alert once if needed.
        alerts = []
        for product in self.manager.products:
            if product["quantity"] < product.get("restock_threshold", 10):
                alerts.append(
                    f"{product['name']} (Quantity: {product['quantity']} < {product.get('restock_threshold', 10)})")
                self.alerted_products.add(product["name"])
        if alerts:
            msg = "The following products have low stock:\n" + "\n".join(alerts)
            QtWidgets.QMessageBox.information(self, "Restock Alert", msg)

    # ---------------------------
    # Sales Analysis Tab
    # ---------------------------
    def initAnalysisTab(self):
        layout = QtWidgets.QVBoxLayout()

        self.label_summary = QtWidgets.QLabel()
        layout.addWidget(self.label_summary)

        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.btn_refresh_analysis = QtWidgets.QPushButton("Refresh Analysis")
        layout.addWidget(self.btn_refresh_analysis)
        self.btn_refresh_analysis.clicked.connect(self.update_analysis)

        self.tab_analysis.setLayout(layout)
        self.update_analysis()

    def update_analysis(self):
        best, best_qty = self.manager.get_best_selling()
        worst, worst_qty = self.manager.get_worst_selling()
        summary_text = (f"Total Revenue: {self.manager.total_revenue:.2f}    "
                        f"Total Profit: {self.manager.total_profit:.2f}\n")
        summary_text += f"Best-selling Product: {best} (Quantity: {best_qty})\n" if best else "Best-selling Product: N/A\n"
        summary_text += f"Worst-selling Product: {worst} (Quantity: {worst_qty})\n" if worst else "Worst-selling Product: N/A\n"
        summary_text += f"Current Day: {self.manager.current_day}"
        self.label_summary.setText(summary_text)

        # Prepare data for charts based on day timeline
        days = list(range(1, self.manager.current_day + 1))
        revenue_by_day = {day: 0 for day in days}
        profit_by_day = {day: 0 for day in days}

        for sale in self.manager.sales:
            d = sale.get("day", 1)
            if d in revenue_by_day:
                revenue_by_day[d] += sale.get("revenue", 0)
                profit_by_day[d] += sale.get("profit", 0)

        product_sales = {}
        for product in self.manager.products:
            product_sales[product["name"]] = [0] * self.manager.current_day
        for sale in self.manager.sales:
            d = sale.get("day", 1)
            product_name = sale["product"]
            if 1 <= d <= self.manager.current_day:
                product_sales[product_name][d - 1] += sale.get("quantity", 0)

        # Clear figure and create 2x2 subplots
        self.figure.clear()
        ax1 = self.figure.add_subplot(221)  # Top-left: Revenue Trend
        ax2 = self.figure.add_subplot(222)  # Top-right: Profit Trend
        ax3 = self.figure.add_subplot(223)  # Bottom-left: Product Sales Trend
        ax4 = self.figure.add_subplot(224)  # Bottom-right: Inventory Status

        # Plot Revenue Trend
        rev_values = [revenue_by_day[day] for day in days]
        ax1.plot(days, rev_values, marker="o")
        ax1.set_title("Sales Revenue Trend")
        ax1.set_xlabel("Day")
        ax1.set_ylabel("Revenue")

        # Plot Profit Trend
        profit_values = [profit_by_day[day] for day in days]
        ax2.plot(days, profit_values, marker="o", color="green")
        ax2.set_title("Total Profit Trend")
        ax2.set_xlabel("Day")
        ax2.set_ylabel("Profit")

        # Plot Individual Product Sales Trend
        for product_name, sales_list in product_sales.items():
            ax3.plot(days, sales_list, marker="o", label=product_name)
        ax3.set_title("Product Sales Trend")
        ax3.set_xlabel("Day")
        ax3.set_ylabel("Quantity Sold")
        ax3.legend()

        # Plot Inventory Status
        names = [p.get("name", "") for p in self.manager.products]
        quantities = [p.get("quantity", 0) for p in self.manager.products]
        ax4.bar(names, quantities)
        ax4.set_title("Inventory Status")
        ax4.set_xlabel("Product")
        ax4.set_ylabel("Current Stock")

        # Make subplots layout cleaner to avoid overlap
        self.figure.tight_layout()
        self.canvas.draw()

    def advance_day(self):
        self.manager.advance_day()
        self.alerted_products = set()
        self.update_status_bar()
        # Update the toolbar label
        self.day_label.setText(f"Day: {self.manager.current_day}")
        self.update_analysis()


# ---------------------------
# Main entry
# ---------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
