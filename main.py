# Inventory and Sales Tracker with Menu System
# Group Assignment - Python Programming in Business

def main():
    # Initialize data storage
    products = []
    sales = []
    total_revenue = 0
    try:
        # 验证是否有本地缓存文件，切不为空，如果找到则提示已经录入请进行修改或其他操作，如果未找到就正常开始输入环节
        with open('products.txt', 'r') as f:
            lines = f.readlines()
            if lines:
                print("已经检测到本地缓存并自动加载！")
                # 读取文件到products
                for line in lines:
                    name, qty, price = line.split()
                    products.append({
                        'name': name,
                        'quantity': int(qty),
                        'price': float(price)
                    })
                pass
    except FileNotFoundError:
        pass

    while True:
        print("\n=== 库存与销售管理系统 ===")
        print("1. 输入产品信息")
        print("2. 记录销售")
        print("3. 查看库存与收入")
        print("4. 修改产品信息")
        print("5. 退出")
        choice = input("请选择操作 (1-5): ")

        if choice == '1':
            if products!=[]:
                print("已经录入产品信息，如需修改请选择修改选项！")
                continue
            else:
                products = input_products()
                # 将产品信息保存到本地文件
                with open('products.txt', 'w') as f:
                    for product in products:
                        f.write(f"{product['name']} {product['quantity']} {product['price']}\n")
        elif choice == '2':
            if not products:
                print("请先输入产品信息！")
                continue
            sales, total_revenue = record_sales(products, sales, total_revenue)
        elif choice == '3':
            if not products:
                print("请先输入产品信息！")
                continue
            display_status(products, total_revenue)
        elif choice == '4':
            edit_products(products)
        elif choice == '5':
            print("感谢使用！")
            break
        else:
            print("无效输入，请重新选择！")


def input_products():
    """输入3个产品的基本信息"""
    products = []
    print("\n=== 输入产品信息 ===")
    for i in range(3):
        name = input(f"产品{i + 1}名称: ")
        qty = int(input(f"{name}库存量: "))
        price = float(input(f"{name}单价: "))
        print('\n')
        products.append({
            'name': name,
            'quantity': qty,
            'price': price
        })
    return products


def record_sales(products, sales, total_revenue):
    """记录销售并更新库存"""
    print("\n=== 记录销售 ===")
    for idx, product in enumerate(products, 1):
        print(f"{idx}. {product['name']} (库存: {product['quantity']})")

    try:
        product_num = int(input("选择产品编号: ")) - 1
        sold = int(input("销售数量: "))

        if 0 <= product_num < len(products):
            if sold <= products[product_num]['quantity']:
                products[product_num]['quantity'] -= sold
                revenue = sold * products[product_num]['price']
                total_revenue += revenue
                sales.append({
                    'product': products[product_num]['name'],
                    'quantity': sold,
                    'revenue': revenue
                })
                print(f"成功记录：{sold}件{products[product_num]['name']}")
            else:
                print("库存不足！")
        else:
            print("无效产品编号！")
    except ValueError:
        print("请输入有效数字！")

    return sales, total_revenue


def display_status(products, total_revenue):
    """显示库存和总收入"""
    print("\n=== 当前状态 ===")
    print("{:<15} {:<10} {:<10}".format("产品名称", "剩余库存", "单价"))
    for product in products:
        print("{:<15} {:<10} {:<10.2f}".format(
            product['name'],
            product['quantity'],
            product['price']
        ))
    print("\n总营收: RM{:.2f}".format(total_revenue))

def edit_products(products):
    """修改产品信息"""
    #先检测是否存在产品信息
    if not products:
        print("请先输入产品信息！")
        return
    else:
        print("\n=== 修改产品信息 ===")
        #显示产品信息
        for idx, product in enumerate(products, 1):
            print(f"{idx}. {product['name']} (库存: {product['quantity']}, 单价: {product['price']})")
        try:
            product_num = int(input("选择产品编号: ")) - 1
            if 0 <= product_num < len(products):
                name = input("新产品名称(无需修改请直接回车): ")
                qty = int(input("新库存量: "))
                price = float(input("新单价: "))
                if name != '':
                    products[product_num]['name'] = name
                products[product_num]['quantity'] = qty
                products[product_num]['price'] = price
                print("成功修改产品信息！")
            else:
                print("无效产品编号！")
        except ValueError:
            print("请输入有效数字！")


if __name__ == "__main__":
    main()