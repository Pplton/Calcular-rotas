# 📍 Calculadora de Valor por KM com Mapa (Google Maps)

Aplicativo desenvolvido em Python que calcula o valor de entregas baseando-se na distância percorrida entre estabelecimentos e destinos, utilizando rotas reais do Google Maps. Ideal para controle de custos em serviços de motoboy e delivery.

---

## ✨ Funcionalidades

- Seleção do estabelecimento (loja) via planilha Excel.
- Digitação manual do endereço de destino.
- Cálculo automático de:
  - Distância real em km
  - Tempo estimado de trajeto
  - Valor pago ao motoboy
  - Valor cobrado do cliente
  - Lucro obtido
- Exibição de rota real diretamente no mapa do app.
- Zoom automático para enquadrar perfeitamente toda a rota.
- Limpeza da rota anterior ao traçar nova rota.
- Posição inicial do mapa definida para Salvador - BA.

---

## 🛠️ Tecnologias utilizadas

- **Python 3.12+**
- **Tkinter** (Interface gráfica)
- **TkinterMapView** (Mapa integrado)
- **Google Maps Geocoding API** (Conversão de endereços)
- **Google Maps Directions API** (Traçado de rotas)
- **Pandas** (Leitura e manipulação de Excel)
- **Requests** (Requisições HTTP)
- **Polyline** (Decodificação de rotas)

---

## 📦 Instalação

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
