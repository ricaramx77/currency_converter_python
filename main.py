import requests
import tkinter as tk
from tkinter import ttk, messagebox


# API endpoint for ExchangeRate-API (requiere API key)
def get_api_key():
    try:
        with open('apikey.txt', 'r') as f:
            return f.read().strip()
    except Exception:
        raise RuntimeError('No se pudo leer la API key. Asegúrate de tener el archivo apikey.txt con tu clave.')

def get_api_url(from_currency, to_currency):
    api_key = get_api_key()
    return f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}'

# Unidades físicas para conversión
PHYSICAL_UNITS = {
    'Longitud': {'m': 1, 'cm': 0.01, 'mm': 0.001, 'km': 1000, 'in': 0.0254, 'ft': 0.3048},
    'Peso': {'kg': 1, 'g': 0.001, 'lb': 0.453592, 'oz': 0.0283495},
    'Volumen': {'l': 1, 'ml': 0.001, 'gal': 3.78541, 'm3': 1000}
}

# --- Lógica de conversión ---
def get_exchange_rate(from_currency, to_currency):
    try:
        url = get_api_url(from_currency, to_currency)
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('result') != 'success':
            raise RuntimeError(f"API error: {data.get('error-type', 'Desconocido')}")
        return data['conversion_rate']
    except Exception as e:
        return 1.5

def convert_currency(amount, from_currency, to_currency):
    rate = get_exchange_rate(from_currency, to_currency)
    return amount * rate

def convert_physical(amount, from_unit, to_unit, unit_type):
    units = PHYSICAL_UNITS[unit_type]
    if from_unit not in units or to_unit not in units:
        raise ValueError('Unidad no soportada')
    return amount * units[from_unit] / units[to_unit]

# --- Interfaz gráfica ---
class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Conversor Universal')
        self.geometry('400x350')
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        self.mode = tk.StringVar(value='Moneda')
        modes = ['Moneda', 'Longitud', 'Peso', 'Volumen']
        ttk.Label(self, text='Tipo de conversión:').pack(pady=5)
        mode_menu = ttk.OptionMenu(self, self.mode, modes[0], *modes, command=self.update_units)
        mode_menu.pack()

        self.amount_var = tk.DoubleVar()
        ttk.Label(self, text='Cantidad:').pack(pady=5)
        ttk.Entry(self, textvariable=self.amount_var).pack()

        self.from_unit = tk.StringVar()
        self.to_unit = tk.StringVar()
        self.from_menu = ttk.Combobox(self, textvariable=self.from_unit)
        self.to_menu = ttk.Combobox(self, textvariable=self.to_unit)
        self.from_menu.pack(pady=5)
        self.to_menu.pack(pady=5)

        ttk.Button(self, text='Convertir', command=self.convert).pack(pady=10)
        self.result_label = ttk.Label(self, text='')
        self.result_label.pack(pady=10)

        self.update_units('Moneda')

    def update_units(self, mode):
        if mode == 'Moneda':
            # Lista corta de monedas populares
            currencies = ['USD', 'EUR', 'MXN', 'GBP', 'JPY', 'BRL', 'ARS', 'COP']
            self.from_menu['values'] = currencies
            self.to_menu['values'] = currencies
            self.from_unit.set('USD')
            self.to_unit.set('MXN')
        else:
            units = list(PHYSICAL_UNITS[mode].keys())
            self.from_menu['values'] = units
            self.to_menu['values'] = units
            self.from_unit.set(units[0])
            self.to_unit.set(units[1])

    def convert(self):
        try:
            amount = self.amount_var.get()
            from_u = self.from_unit.get()
            to_u = self.to_unit.get()
            mode = self.mode.get()
            if mode == 'Moneda':
                result = convert_currency(amount, from_u, to_u)
                self.result_label['text'] = f"{amount} {from_u} = {result:.2f} {to_u}"
            else:
                result = convert_physical(amount, from_u, to_u, mode)
                self.result_label['text'] = f"{amount} {from_u} = {result:.4f} {to_u}"
        except Exception as e:
            messagebox.showerror('Error', str(e))

if __name__ == '__main__':
    app = ConverterApp()
    app.mainloop()
