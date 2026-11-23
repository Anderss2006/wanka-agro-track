import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Lote,
  LoteCreate,
  PedidoCreate,
  ProductorCreate,
  Catalogos,
  LoginRequest,
  UsuarioSesion,
  PedidoHistorial
} from '../models/agro.model';

@Injectable({
  providedIn: 'root'
})
export class AgroService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000/api';

  login(credenciales: LoginRequest): Observable<{ mensaje: string; usuario: UsuarioSesion }> {
    return this.http.post<{ mensaje: string; usuario: UsuarioSesion }>(`${this.apiUrl}/auth/login`, credenciales);
  }

  getLotes(): Observable<Lote[]> {
    return this.http.get<Lote[]>(`${this.apiUrl}/lotes`);
  }

  getCatalogos(): Observable<Catalogos> {
    return this.http.get<Catalogos>(`${this.apiUrl}/catalogos`);
  }

  publicarLote(lote: LoteCreate): Observable<{ mensaje: string }> {
    return this.http.post<{ mensaje: string }>(`${this.apiUrl}/lotes`, lote);
  }

  reservarPedido(pedido: PedidoCreate): Observable<{ mensaje: string; id_pedido: number }> {
    return this.http.post<{ mensaje: string; id_pedido: number }>(`${this.apiUrl}/pedidos`, pedido);
  }

  registrarProductor(productor: ProductorCreate): Observable<{ mensaje: string }> {
    return this.http.post<{ mensaje: string }>(`${this.apiUrl}/productores`, productor);
  }

  getPedidosUsuario(idUsuario: number, rol: string): Observable<PedidoHistorial[]> {
    return this.http.get<PedidoHistorial[]>(`${this.apiUrl}/pedidos/usuario/${idUsuario}?rol=${rol}`);
  }
}