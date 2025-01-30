from flask import Flask, render_template, request

app = Flask(__name__)

products = []
min_product = None
max_product = None

def convert_to_unit_price(price, quantity, unit):
    if unit == "gram":
        return price / (quantity / 1000)
    elif unit == "ml":
        return price / (quantity / 1000)
    else:
        return None

def update_min_max(products, current_product):
    if not products:
      return {"min": current_product, "max": current_product}
    min_product = products[0]
    max_product = products[0]
    for product in products:
        if product["unit_price"] < min_product["unit_price"]:
            min_product = product
        if product["unit_price"] > max_product["unit_price"]:
            max_product = product
    if current_product["unit_price"] < min_product["unit_price"]:
        min_product = current_product
    if current_product["unit_price"] > max_product["unit_price"]:
         max_product = current_product
    return {"min": min_product, "max": max_product}


@app.route("/", methods=["GET", "POST"])
def index():
    global products, min_product, max_product
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]

        unit_price = convert_to_unit_price(price, quantity, unit)
        current_product = {"name": name, "unit_price": unit_price, "price": price, "quantity": quantity, "unit": unit}
        products.append(current_product)

        min_max = update_min_max(products, current_product)
        min_product = min_max["min"]
        max_product = min_max["max"]

    return render_template("index.html", products=products, min_product=min_product, max_product=max_product)

if __name__ == "__main__":
    app.run(debug=True)
