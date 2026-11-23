const API_URL = "http://127.0.0.1:8000/api";

const ApiService = {
    async obtenerLotes() {
        const res = await fetch(`${API_URL}/lotes`);
        if (!res.ok) throw new Error("No se pudieron cargar los lotes");
        return await res.json();
    },

    async obtenerCatalogos() {
        const res = await fetch(`${API_URL}/catalogos`);
        if (!res.ok) throw new Error("No se pudieron cargar los catálogos");
        return await res.json();
    },

    async crearLote(datosLote) {
        const res = await fetch(`${API_URL}/lotes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datosLote)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Error al publicar el lote");
        return data;
    },

    async crearPedido(datosPedido) {
        const res = await fetch(`${API_URL}/pedidos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datosPedido)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Error al procesar la reserva");
        return data;
    }
};