export interface Lote {
  id_lote: number;
  nombre_producto: string;
  unidad_medida: string;
  nombre_categoria: string;
  productor: string;
  telefono: string;
  origen: string;
  precio_unitario: number;
  stock_disponible: number;
  fecha_cosecha: string;
  punto_entrega: string;
}

export interface LoteCreate {
  id_productor: number;
  id_producto: number;
  precio_unitario: number;
  stock_disponible: number;
  fecha_cosecha: string;
  punto_entrega: string;
}

export interface PedidoCreate {
  id_comprador: number;
  id_lote: number;
  cantidad: number;
}

export interface ProductorCreate {
  nombres: string;
  apellidos: string;
  dni: string;
  telefono: string;
  id_distrito: number;
}

export interface UsuarioSesion {
  id_usuario: number;
  nombres: string;
  apellidos: string;
  nombre_completo: string;
  dni: string;
  telefono: string;
  rol: 'PRODUCTOR' | 'COMPRADOR' | string;
  distrito: string;
}

export interface LoginRequest {
  dni: string;
  clave: string;
}

export interface Catalogos {
  productores: { id: number; nombre: string }[];
  compradores: { id: number; nombre: string }[];
  productos: { id: number; nombre: string }[];
  distritos: { id: number; nombre: string }[];
}

export interface PedidoHistorial {
  id_pedido: number;
  fecha_pedido: string;
  nombre_producto: string;
  unidad_medida: string;
  cantidad: number;
  precio_unitario: number;
  total_pagar: number;
  estado: string;
  punto_entrega: string;
  productor: string;
  telefono_productor: string;
  comprador: string;
  telefono_comprador: string;
}