import unicodedata
import json

# Cargar el archivo original
with open('core/quimicos_cas.json', encoding='utf-8') as f:
    cas_dict = json.load(f)

# Generar variantes sin tildes
nuevos = {}
def sin_tildes(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

for k, v in cas_dict.items():
    nuevos[k] = v
    k_sin = sin_tildes(k)
    if k_sin != k and k_sin not in nuevos:
        nuevos[k_sin] = v

# Guardar el archivo actualizado
with open('core/quimicos_cas.json', 'w', encoding='utf-8') as f:
    json.dump(nuevos, f, ensure_ascii=False, indent=2)

print('¡Listo! Variantes sin tildes agregadas.')
