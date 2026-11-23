let precioSeleccionado = 0;

document.addEventListener("DOMContentLoaded", () => {
    cargarDatosIniciales();
    configurarEventos();
});

async function cargarDatosIniciales() {
    try {
        const [lotes, catalogos] = await Promise.all([
            ApiService.obtenerLotes(),
            ApiService.obtenerCatalogos()
        ]);
        renderizarLotes(lotes);
        llenarSelects(catalogos);
    } catch (error) {
        mostrarAlerta(`Error de conexión con FastAPI: ${error.message}`, "danger");
    }
}

function renderizarLotes(lotes) {
    const contenedor = document.getElementById("contenedorLotes");
    if (lotes.length === 0) {
        contenedor.innerHTML = `<div class="col-12"><div class="alert alert-info">No hay lotes disponibles por el momento.</div></div>`;
        return;
    }

    contenedor.innerHTML = lotes.map(lote => `
        <div class="col-12 col-md-6 col-lg-4">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-header bg-white border-bottom-0 pt-3 d-flex justify-content-between align-items-center">
                    <span class="badge bg-success-subtle text-success border border-success-subtle">${lote.nombre_categoria}</span>
                    <small class="text-muted"><i class="bi bi-geo-alt-fill text-danger"></i> ${lote.origen}</small>
                </div>
                <div class="card-body">
                    <h5 class="card-title fw-bold mb-1">${lote.nombre_producto}</h5>
                    <p class="text-muted small mb-3">Productor: <strong>${lote.productor}</strong></p>
                    
                    <div class="bg-light p-2 rounded mb-3">
                        <div class="d-flex justify-content-between">
                            <span class="small text-muted">Precio (${lote.unidad_medida}):</span>
                            <span class="fw-bold text-success">S/ ${Number(lote.precio_unitario).toFixed(2)}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span class="small text-muted">Stock disponible:</span>
                            <span class="fw-semibold">${lote.stock_disponible}</span>
                        </div>
                    </div>

                    <p class="small mb-1"><i class="bi bi-calendar-event me-1 text-primary"></i> Cosecha: ${lote.fecha_cosecha}</p>
                    <p class="small text-truncate mb-0" title="${lote.punto_entrega}">
                        <i class="bi bi-shop me-1 text-warning"></i> ${lote.punto_entrega}
                    </p>
                </div>
                <div class="card-footer bg-white border-top-0 pb-3">
                    <button class="btn btn-outline-primary w-100 fw-semibold" 
                        onclick="abrirModalReserva(${lote.id_lote}, '${lote.nombre_producto}', ${lote.precio_unitario}, ${lote.stock_disponible})">
                        <i class="bi bi-bag-plus me-1"></i> Reservar Directo
                    </button>
                </div>
            </div>
        </div>
    `).join("");
}

function llenarSelects(catalogos) {
    document.getElementById("selectProductor").innerHTML = catalogos.productores
        .map(p => `<option value="${p.id}">${p.nombre}</option>`).join("");
    
    document.getElementById("selectProducto").innerHTML = catalogos.productos
        .map(p => `<option value="${p.id}">${p.nombre}</option>`).join("");
    
    document.getElementById("selectComprador").innerHTML = catalogos.compradores
        .map(c => `<option value="${c.id}">${c.nombre}</option>`).join("");
}

function abrirModalReserva(idLote, nombre, precio, stock) {
    precioSeleccionado = Number(precio);
    document.getElementById("reservaIdLote").value = idLote;
    document.getElementById("reservaNombreProducto").textContent = nombre;
    document.getElementById("reservaPrecioUnit").textContent = precioSeleccionado.toFixed(2);
    document.getElementById("reservaStockMax").textContent = stock;
    
    const inputCant = document.getElementById("inputCantidadReserva");
    inputCant.value = 1;
    inputCant.max = stock;
    document.getElementById("reservaTotalEstimado").textContent = precioSeleccionado.toFixed(2);

    const modal = new bootstrap.Modal(document.getElementById("modalReservar"));
    modal.show();
}

function configurarEventos() {
    // Calcular total dinámico al cambiar cantidad
    document.getElementById("inputCantidadReserva").addEventListener("input", (e) => {
        const cant = Number(e.target.value) || 0;
        document.getElementById("reservaTotalEstimado").textContent = (cant * precioSeleccionado).toFixed(2);
    });

    // Submit: Publicar Lote
    const formLote = document.getElementById("formPublicarLote");
    formLote.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!formLote.checkValidity()) {
            formLote.classList.add("was-validated");
            return;
        }

        const payload = {
            id_productor: Number(document.getElementById("selectProductor").value),
            id_producto: Number(document.getElementById("selectProducto").value),
            precio_unitario: Number(document.getElementById("inputPrecio").value),
            stock_disponible: Number(document.getElementById("inputStock").value),
            fecha_cosecha: document.getElementById("inputFecha").value,
            punto_entrega: document.getElementById("inputPuntoEntrega").value.trim()
        };

        try {
            const resp = await ApiService.crearLote(payload);
            bootstrap.Modal.getInstance(document.getElementById("modalPublicarLote")).hide();
            formLote.reset();
            formLote.classList.remove("was-validated");
            mostrarAlerta(resp.mensaje, "success");
            cargarDatosIniciales();
        } catch (err) {
            mostrarAlerta(err.message, "danger");
        }
    });

    // Submit: Confirmar Reserva
    const formReserva = document.getElementById("formReservar");
    formReserva.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!formReserva.checkValidity()) {
            formReserva.classList.add("was-validated");
            return;
        }

        const payload = {
            id_comprador: Number(document.getElementById("selectComprador").value),
            id_lote: Number(document.getElementById("reservaIdLote").value),
            cantidad: Number(document.getElementById("inputCantidadReserva").value)
        };

        try {
            const resp = await ApiService.crearPedido(payload);
            bootstrap.Modal.getInstance(document.getElementById("modalReservar")).hide();
            formReserva.classList.remove("was-validated");
            mostrarAlerta(`${resp.mensaje} (Pedido #${resp.id_pedido})`, "success");
            cargarDatosIniciales();
        } catch (err) {
            mostrarAlerta(err.message, "danger");
        }
    });
}

function mostrarAlerta(mensaje, tipo) {
    const alerta = document.getElementById("alertaSistema");
    alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
    document.getElementById("alertaMensaje").textContent = mensaje;
}

function ocultarAlerta() {
    document.getElementById("alertaSistema").classList.add("d-none");
}