// Estado del carrito en el navegador
const cart = {};
let selectedMesa = 1;

function formatBs(num){
    const n = Number(num || 0);
    return n.toFixed(2);
}

function addToCart(productoId, precio, nombre){
    const id = Number(productoId);
    if(!cart[id]){
        cart[id] = { cantidad: 0, precio: Number(precio), nombre: nombre };
    }
    cart[id].cantidad += 1;
    renderCart();
}

function changeQty(productoId, delta){
    const id = Number(productoId);
    if(!cart[id]) return;
    cart[id].cantidad += delta;
    if(cart[id].cantidad <= 0) delete cart[id];
    renderCart();
}

function recalcTotal(){
    let total = 0;
    Object.values(cart).forEach(item => {
        total += item.precio * item.cantidad;
    });
    const cartTotal = document.getElementById('cartTotal');
    if(cartTotal) cartTotal.textContent = 'Bs ' + formatBs(total);
}

function renderCart(){
    const list = document.getElementById('cartList');
    if(!list) return;

    list.innerHTML = '';
    const entries = Object.entries(cart);

    if(entries.length === 0){
        const empty = document.createElement('div');
        empty.className = 'cart-empty';
        empty.textContent = 'Tu carrito está vacío. Agrega productos desde el menú.';
        list.appendChild(empty);
        recalcTotal();
        return;
    }

    for(const [productoId, item] of entries){
        const row = document.createElement('div');
        row.className = 'cart-row';

        const left = document.createElement('div');
        left.innerHTML = `
            <div class="name">${item.nombre}</div>
            <div class="meta">
                Precio: Bs ${formatBs(item.precio)} | Subtotal: Bs ${formatBs(item.precio * item.cantidad)}
            </div>
        `;

        const right = document.createElement('div');
        right.className = 'cart-qty';
        right.innerHTML = `
            <button type="button" class="qty-btn" data-pid="${productoId}" data-delta="-1">-</button>
            <div class="qty">${item.cantidad}</div>
            <button type="button" class="qty-btn" data-pid="${productoId}" data-delta="+1">+</button>
        `;

        row.appendChild(left);
        row.appendChild(right);
        list.appendChild(row);
    }

    recalcTotal();
}

function renderMesaButtons(){
    const grid = document.getElementById('mesaGrid');
    if(!grid) return;

    const total = Number(document.getElementById('mesasTotal')?.value || 0);
    grid.innerHTML = '';

    for(let i=1; i<=total; i++){
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'mesa-btn' + (i === selectedMesa ? ' active' : '');
        btn.textContent = i;
        btn.addEventListener('click', () => selectMesa(i));
        grid.appendChild(btn);
    }
}

function selectMesa(n){
    selectedMesa = n;
    const mesaSelected = document.getElementById('mesaSelected');
    if(mesaSelected) mesaSelected.textContent = n;

    const mesaInput = document.getElementById('mesaInput');
    if(mesaInput) mesaInput.value = String(n);

    document.querySelectorAll('.mesa-btn').forEach(b => b.classList.remove('active'));
    const btn = Array.from(document.querySelectorAll('.mesa-btn')).find(b => Number(b.textContent) === n);
    if(btn) btn.classList.add('active');
}

function tabsInit(){
    const tabs = [
        { tabId: 'tabPlatos', panelId: 'productosPlatos' },
        { tabId: 'tabSodas', panelId: 'productosSodas' },
        { tabId: 'tabJugos', panelId: 'productosJugos' },
        { tabId: 'tabOtras', panelId: 'productosOtras' },
    ];

    const tabEls = tabs.map(t => document.getElementById(t.tabId));
    const panelEls = tabs.map(t => document.getElementById(t.panelId));

    if(tabEls.some(x => !x) || panelEls.some(x => !x)) return;

    function activate(idx){
        tabs.forEach((t, i) => {
            const tab = document.getElementById(t.tabId);
            const panel = document.getElementById(t.panelId);
            if(!tab || !panel) return;
            if(i === idx){
                tab.classList.add('active');
                panel.classList.remove('is-hidden');
            }else{
                tab.classList.remove('active');
                panel.classList.add('is-hidden');
            }
        });
    }

    tabs.forEach((t, idx) => {
        const tab = document.getElementById(t.tabId);
        tab.addEventListener('click', () => activate(idx));
    });
}

function syncCartToForm(){
    const cartInput = document.getElementById('cartInput');
    if(!cartInput) return;
    const payload = Object.entries(cart).map(([producto_id, item]) => ({
        producto_id: Number(producto_id),
        cantidad: item.cantidad
    }));
    cartInput.value = JSON.stringify(payload);
}

function bindAddButtons(){
    document.querySelectorAll('.add-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            addToCart(btn.dataset.pid, btn.dataset.precio, btn.dataset.nombre);
        });
    });
}

function bindCartQtyButtons(){
    const cartList = document.getElementById('cartList');
    if(!cartList) return;

    // Delegación: funciona aunque el carrito se re-renderice
    cartList.addEventListener('click', (e) => {
        const target = e.target.closest('.qty-btn');
        if(!target) return;
        const pid = target.dataset.pid;
        const delta = Number(target.dataset.delta || 0);
        if(pid) changeQty(pid, delta);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // Revisa: algunos elementos pueden no existir según el caso
    const orderForm = document.getElementById('orderForm');
    if(orderForm){
        orderForm.addEventListener('submit', () => {
            syncCartToForm();
        });
    }

    renderMesaButtons();
    tabsInit();
    renderCart();
    bindAddButtons();
    bindCartQtyButtons();
    selectMesa(1);

    const printMesaBtn = document.getElementById('printMesaBtn');
    if(printMesaBtn){
        printMesaBtn.addEventListener('click', () => {
            // Abre el ticket del último pedido guardado de esta mesa
            const url = `/pedido-mesa/${selectedMesa}/ultimo/`;
            window.open(url, '_blank');
        });
    }
});

