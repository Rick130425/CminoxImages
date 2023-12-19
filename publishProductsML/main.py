import pandas as pd
import requests


def leer_excel(archivo):
    df = pd.read_excel(archivo)
    return df


def autenticar(client_id, client_secret, code, redirect_uri):
    url = "https://api.mercadolibre.com/oauth/token"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Error en la autenticación: " + response.text)


def refrescarToken(client_id, client_secret, refresh_token):
    url = "https://api.mercadolibre.com/oauth/token"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Error en la autenticación: " + response.text)


def upload_product(access_token, product):
    """
    Uploads a product to Mercado Libre.

    Parameters:
    access_token (str): Authentication token for API access.
    product (dict): Dictionary containing product details.

    Returns:
    str or None: Product ID if upload is successful, None otherwise.
    """

    # API endpoint for uploading products
    url = "https://api.mercadolibre.com/items"

    # Headers with authorization token
    headers = {"Authorization": f"Bearer {access_token}"}

    # Prepare image data
    image_urls = product['URL Imagenes'].split(',')
    images = [{"source": url.strip()} for url in image_urls]

    # Mandatory attributes
    attributes = [
        {"id": "BRAND", "value_name": product["Marca"]},
        {"id": "MODEL", "value_name": product["Modelo"]}
    ]

    # Optional attribute: Compatible Tools
    compatible_tools = product.get("Herramientas compatibles")
    if pd.notna(compatible_tools):
        attributes.append({"id": "COMPATIBLE_TOOLS", "value_name": compatible_tools})
    if product["Modelo"][:4] == "FNRC":
        attributes.append({"id": "MANUFACTURER", "value_name": "Cminox"})
        attributes.append({"id": "MATERIAL", "value_name": "Acero inoxidable"})

    # Data payload for the product
    data = {
        "site_id": "MLM",  # Marketplace site ID, adjust as needed
        "title": product['Título'],
        "category_id": product['Categoría'],  # Ensure this is a valid category
        "price": product['Precio'],
        "currency_id": "MXN",  # Currency, adjust as needed
        "available_quantity": product['Cantidad disponible'],
        "buying_mode": "buy_it_now",
        "condition": "new",
        "listing_type_id": "gold_special",
        "description": {"plain_text": product.get('Descripción', '')},  # Optional description
        "pictures": images,
        "channels": ["marketplace", "mshops"],
        "attributes": attributes,
        "shipping": {
            "mode": "me2",
            "local_pick_up": True,
            "free_shipping": product['Envío'] == "Gratis"
        }
    }

    # Make a POST request to upload the product
    response = requests.post(url, headers=headers, json=data)

    # Check response status and return product ID if successful
    if response.status_code == 201:
        return response.json()['id']
    else:
        print("Error uploading product:", response.text)
        return None


# Usar tus credenciales reales aquí
# access_token = autenticar('2447922089667594', 'Ku613zfb4mRoVKSM1ZS5y5IQG6NmmU1z',
# 'TG-657a1ec174bb6e0001f12ed8-578324692', 'https://cminox.com')

access_token = 'APP_USR-5790996786516740-121517-394aa1733ec9efed10c474b3aa3d708e-578324692'
df_productos = leer_excel('productos.xlsx')

for index, producto in df_productos.iterrows():
    resultado = upload_product(access_token, producto)
    if resultado:
        print("Producto subido con éxito:", resultado)
    else:
        print("Error al subir el producto")