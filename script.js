let cart = [];

function addToCart(id, name, price) {
    // Verificar si el producto ya está en el carrito
    let productIndex = cart.findIndex(item => item.id === id);
    if (productIndex !== -1) {
        cart[productIndex].quantity += 1;
    } else {
        cart.push({ id, name, price, quantity: 1 });
    }

    updateCart();
}

function updateCart() {
    let cartItems = document.getElementById("cart-items");
    cartItems.innerHTML = ""; // Limpiar carrito

    let total = 0;
    cart.forEach(item => {
        total += item.price * item.quantity;

        let li = document.createElement("li");
        li.textContent = `${item.name} - $${item.price} x ${item.quantity}`;
        cartItems.appendChild(li);
    });

    document.getElementById("total").textContent = `Total: $${total.toFixed(2)}`;
}

function checkout() {
    if (cart.length === 0) {
        alert("El carrito está vacío.");
        return;
    }

    let total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    alert(`Pago realizado por $${total.toFixed(2)}. ¡Gracias por su compra!`);

    // Limpiar carrito después del pago
    cart = [];
    updateCart();
}
