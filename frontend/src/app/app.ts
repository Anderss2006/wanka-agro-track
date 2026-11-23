import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AgroService } from './services/agro.service';
import {
  Lote,
  Catalogos,
  LoteCreate,
  PedidoCreate,
  ProductorCreate,
  LoginRequest,
  UsuarioSesion,
  PedidoHistorial
} from './models/agro.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  private agroService = inject(AgroService);

  usuarioActual = signal<UsuarioSesion | null>(null);
  lotes = signal<Lote[]>([]);
  pedidosHistorial = signal<PedidoHistorial[]>([]);
  catalogos = signal<Catalogos>({ productores: [], compradores: [], productos: [], distritos: [] });
  loteSeleccionado = signal<Lote | null>(null);
  alerta = signal<{ tipo: string; mensaje: string } | null>(null);

  credenciales: LoginRequest = {
    dni: '',
    clave: ''
  };

  nuevoLote: LoteCreate = {
    id_productor: 1,
    id_producto: 1,
    precio_unitario: 0,
    stock_disponible: 0,
    fecha_cosecha: '2026-11-23',
    punto_entrega: ''
  };

  nuevaReserva: PedidoCreate = {
    id_comprador: 3,
    id_lote: 0,
    cantidad: 1
  };

  nuevoProductor: ProductorCreate = {
    nombres: '',
    apellidos: '',
    dni: '',
    telefono: '',
    id_distrito: 1
  };

  ngOnInit(): void {
    const sesionGuardada = localStorage.getItem('wanka_usuario');
    if (sesionGuardada) {
      const user: UsuarioSesion = JSON.parse(sesionGuardada);
      this.usuarioActual.set(user);
      this.sincronizarUsuarioConFormularios(user);
      this.cargarHistorialPedidos();
    }
    this.cargarDatos();
  }

  sincronizarUsuarioConFormularios(user: UsuarioSesion): void {
    if (user.rol === 'PRODUCTOR') {
      this.nuevoLote.id_productor = user.id_usuario;
    } else if (user.rol === 'COMPRADOR') {
      this.nuevaReserva.id_comprador = user.id_usuario;
    }
  }

  iniciarSesion(): void {
    this.agroService.login(this.credenciales).subscribe({
      next: (res) => {
        this.usuarioActual.set(res.usuario);
        localStorage.setItem('wanka_usuario', JSON.stringify(res.usuario));
        this.sincronizarUsuarioConFormularios(res.usuario);
        this.cargarHistorialPedidos();
        this.credenciales = { dni: '', clave: '' };
        this.mostrarAlerta('success', res.mensaje);
      },
      error: (err) => {
        this.mostrarAlerta('danger', err.error?.detail || 'Credenciales inválidas.');
      }
    });
  }

  cerrarSesion(): void {
    this.usuarioActual.set(null);
    this.pedidosHistorial.set([]);
    localStorage.removeItem('wanka_usuario');
    this.mostrarAlerta('info', 'Sesión cerrada correctamente.');
  }

  cargarDatos(): void {
    this.agroService.getLotes().subscribe({
      next: (data) => this.lotes.set(data),
      error: () => this.mostrarAlerta('danger', 'No se pudo conectar con la API de FastAPI.')
    });

    this.agroService.getCatalogos().subscribe({
      next: (data) => {
        this.catalogos.set(data);
        if (!this.usuarioActual() && data.productores.length) {
          this.nuevoLote.id_productor = data.productores[0].id;
        }
        if (data.productos.length) this.nuevoLote.id_producto = data.productos[0].id;
        if (!this.usuarioActual() && data.compradores.length) {
          this.nuevaReserva.id_comprador = data.compradores[0].id;
        }
        if (data.distritos.length) this.nuevoProductor.id_distrito = data.distritos[0].id;
      }
    });
  }

  cargarHistorialPedidos(): void {
    const user = this.usuarioActual();
    if (!user) {
      this.pedidosHistorial.set([]);
      return;
    }

    this.agroService.getPedidosUsuario(user.id_usuario, user.rol).subscribe({
      next: (data) => this.pedidosHistorial.set(data),
      error: () => this.pedidosHistorial.set([])
    });
  }

  abrirModalReserva(lote: Lote): void {
    this.loteSeleccionado.set(lote);
    this.nuevaReserva.id_lote = lote.id_lote;
    this.nuevaReserva.cantidad = 1;
    const user = this.usuarioActual();
    if (user && user.rol === 'COMPRADOR') {
      this.nuevaReserva.id_comprador = user.id_usuario;
    }
  }

  confirmarReserva(): void {
    if (!this.loteSeleccionado() || this.nuevaReserva.cantidad <= 0) return;

    this.agroService.reservarPedido(this.nuevaReserva).subscribe({
      next: (res) => {
        this.mostrarAlerta('success', `${res.mensaje} (Pedido #${res.id_pedido})`);
        this.cargarDatos();
        this.cargarHistorialPedidos();
      },
      error: (err) => {
        this.mostrarAlerta('danger', err.error?.detail || 'Error al procesar la reserva.');
      }
    });
  }

  guardarNuevoLote(): void {
    const user = this.usuarioActual();
    if (user && user.rol === 'PRODUCTOR') {
      this.nuevoLote.id_productor = user.id_usuario;
    }

    this.agroService.publicarLote(this.nuevoLote).subscribe({
      next: (res) => {
        this.mostrarAlerta('success', res.mensaje);
        this.nuevoLote.precio_unitario = 0;
        this.nuevoLote.stock_disponible = 0;
        this.nuevoLote.punto_entrega = '';
        this.cargarDatos();
      },
      error: (err) => {
        this.mostrarAlerta('danger', err.error?.detail || 'Verifica los datos ingresados.');
      }
    });
  }

  guardarNuevoProductor(): void {
    this.agroService.registrarProductor(this.nuevoProductor).subscribe({
      next: (res) => {
        this.mostrarAlerta('success', res.mensaje);
        this.nuevoProductor.nombres = '';
        this.nuevoProductor.apellidos = '';
        this.nuevoProductor.dni = '';
        this.nuevoProductor.telefono = '';
        this.cargarDatos();
      },
      error: (err) => {
        this.mostrarAlerta('danger', err.error?.detail || 'Verifica los datos del productor.');
      }
    });
  }

  mostrarAlerta(tipo: string, mensaje: string): void {
    this.alerta.set({ tipo, mensaje });
    setTimeout(() => this.alerta.set(null), 5000);
  }
}