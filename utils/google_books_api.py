import requests

def buscar_libros(termino, max_results=5):
    """
    Busca libros en la API de Google Books.
    Retorna una lista de diccionarios con título, autor, descripción, link, isbn, género e imagen.
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q={termino}&langRestrict=es&maxResults={max_results}"
    resp = requests.get(url)
    datos = resp.json()
    resultados = []

    if "items" not in datos:
        return resultados

    for item in datos["items"]:
        info = item.get("volumeInfo", {})
        industry_ids = info.get("industryIdentifiers", [])
        isbn = industry_ids[0]["identifier"] if industry_ids else "N/A"
        imagen = info.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/128x192?text=Sin+Imagen")

        resultados.append({
            "titulo": info.get("title", "Sin título"),
            "autor": ", ".join(info.get("authors", ["Desconocido"])),
            "descripcion": info.get("description", "Sin descripción disponible."),
            "link": info.get("infoLink", "#"),
            "isbn": isbn,
            "genero": ", ".join(info.get("categories", ["No especificado"])),
            "editorial": info.get("publisher", "No especificada"),
            "imagen": imagen
        })

    return resultados
