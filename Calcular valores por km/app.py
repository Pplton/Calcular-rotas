import pandas as pd
import requests
import polyline
import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView

# CONFIGURAÇÕES
PLANILHA_CAMINHO = 'Tabela_pagamentos_por_Km.xlsx'
GOOGLE_API_KEY = 'AIzaSyBRRHnjvy_Zbgjd3DCPv2il1Blycx9jr4Q'

# Variável para guardar o último caminho desenhado
ultimo_caminho = None

# Lê a planilha
xls = pd.ExcelFile(PLANILHA_CAMINHO)
sheet_names = xls.sheet_names
abas = {nome: pd.read_excel(PLANILHA_CAMINHO, sheet_name=nome) for nome in sheet_names}

# Obtém os endereços dos estabelecimentos
enderecos_lojas = {}
for nome, df in abas.items():
    endereco = df['Endereço'].dropna().iloc[0]
    enderecos_lojas[nome] = endereco

# Função para geocodificar endereço (Google)
def geocodificar(endereco):
    url = f"https://maps.googleapis.com/maps/api/geocode/json"
    params = {'address': endereco, 'key': GOOGLE_API_KEY}
    resposta = requests.get(url, params=params)
    dados = resposta.json()
    if dados['status'] == 'OK':
        latitude = dados['results'][0]['geometry']['location']['lat']
        longitude = dados['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    else:
        return None

# Função para buscar rota e distância (Google, usando Polyline correta)
def buscar_rota(origem_latlon, destino_latlon):
    origem = f"{origem_latlon[0]},{origem_latlon[1]}"
    destino = f"{destino_latlon[0]},{destino_latlon[1]}"
    url = f"https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin': origem,
        'destination': destino,
        'mode': 'driving',
        'key': GOOGLE_API_KEY
    }
    resposta = requests.get(url, params=params)
    dados = resposta.json()
    if dados['status'] == 'OK':
        rota = dados['routes'][0]['legs'][0]
        distancia_km = rota['distance']['value'] / 1000  # metros para km
        duracao_min = rota['duration']['value'] / 60  # segundos para minutos
        
        # Pega a overview_polyline e decodifica
        overview_polyline = dados['routes'][0]['overview_polyline']['points']
        coordenadas_rota = polyline.decode(overview_polyline)
        
        return distancia_km, duracao_min, coordenadas_rota
    else:
        return None, None, None

# Função para traçar rota e calcular valores
def traçar_rota():
    global ultimo_caminho

    estabelecimento = combo_estabelecimento.get()
    destino_endereco = entrada_destino.get()

    if not estabelecimento or not destino_endereco:
        messagebox.showwarning("Aviso", "Por favor, selecione o estabelecimento e digite o endereço de destino.")
        return

    origem_endereco = enderecos_lojas[estabelecimento]

    origem_coords = geocodificar(origem_endereco)
    destino_coords = geocodificar(destino_endereco)

    if not origem_coords or not destino_coords:
        messagebox.showerror("Erro", "Não foi possível localizar um dos endereços.")
        return

    distancia_km, duracao_min, coordenadas_rota = buscar_rota(origem_coords, destino_coords)

    if distancia_km is None:
        messagebox.showerror("Erro", "Não foi possível traçar a rota.")
        return

    # Limpa a rota anterior se existir
    if ultimo_caminho:
        ultimo_caminho.delete()

    # Desenha a nova rota
    ultimo_caminho = mapa.set_path(coordenadas_rota)

    # Ajusta o zoom automático para enquadrar toda a rota
    latitudes = [lat for lat, lon in coordenadas_rota]
    longitudes = [lon for lat, lon in coordenadas_rota]
    mapa.fit_bounding_box((min(latitudes), min(longitudes)), (max(latitudes), max(longitudes)))

    # Buscar valores
    df = abas[estabelecimento]

    valor_pago = None
    valor_cobrado = None

    for _, row in df.iterrows():
        if row['KM Inical'] <= distancia_km <= row['KM Final']:
            valor_pago = row['Valor']
            if 'Valor Cobrado' in row:
                valor_cobrado = row['Valor Cobrado']
            break

    if valor_pago is None:
        valor_pago_texto = "Não encontrado"
    else:
        valor_pago_texto = f"R$ {valor_pago:.2f}"

    if valor_cobrado is None or pd.isna(valor_cobrado):
        valor_cobrado_texto = "Não encontrado"
        lucro_texto = "Não disponível"
    else:
        valor_cobrado_texto = f"R$ {valor_cobrado:.2f}"
        lucro_texto = f"R$ {valor_cobrado - valor_pago:.2f}"

    # Atualizar labels
    label_resultado.config(text=f"""
Distância percorrida: {distancia_km:.2f} km
Tempo estimado: {duracao_min:.0f} minutos
Valor pago ao motoboy: {valor_pago_texto}
Valor cobrado da loja: {valor_cobrado_texto}
Lucro: {lucro_texto}
""")

# Interface
janela = tk.Tk()
janela.title("Calculadora de Valor por KM com Mapa (Google)")
janela.geometry("800x750")

# Widgets
frame_superior = tk.Frame(janela)
frame_superior.pack(pady=10)

label_estabelecimento = tk.Label(frame_superior, text="Escolha o Estabelecimento:")
label_estabelecimento.grid(row=0, column=0, padx=5, pady=5, sticky="e")

combo_estabelecimento = ttk.Combobox(frame_superior, values=list(enderecos_lojas.keys()), state="readonly", width=50)
combo_estabelecimento.grid(row=0, column=1, padx=5, pady=5)

label_destino = tk.Label(frame_superior, text="Digite o Endereço de Destino:")
label_destino.grid(row=1, column=0, padx=5, pady=5, sticky="e")

entrada_destino = tk.Entry(frame_superior, width=53)
entrada_destino.grid(row=1, column=1, padx=5, pady=5)

botao_rota = tk.Button(janela, text="Traçar Rota e Calcular", command=traçar_rota)
botao_rota.pack(pady=10)

# Mapa
mapa = TkinterMapView(janela, width=750, height=400, corner_radius=10)
mapa.set_tile_server("https://tile.openstreetmap.org/{z}/{x}/{y}.png")

# Define Salvador como posição inicial
mapa.set_position(-12.9714, -38.5014)  # Salvador - BA
mapa.set_zoom(12)

mapa.pack(pady=10)

# Resultado
label_resultado = tk.Label(janela, text="", font=("Arial", 12))
label_resultado.pack(pady=10)

botao_sair = tk.Button(janela, text="Sair", command=janela.destroy)
botao_sair.pack(pady=10)

janela.mainloop()
