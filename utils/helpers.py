from datetime import timedelta

def calcular_vencimiento(fecha_realizacion, frecuencia):
    if frecuencia == 'anual':
        return fecha_realizacion + timedelta(days=365)
    elif frecuencia == 'bienal':
        return fecha_realizacion + timedelta(days=730)
    elif frecuencia == 'trienal':
        return fecha_realizacion + timedelta(days=1095)
    elif frecuencia == 'unico':
        return None
    return None
