def buscar_fila(page, tabla_id, texto):
    """Filtra la DataTable por `texto` usando su buscador nativo y devuelve
    el locator de la fila resultante. Evita depender de en que pagina de la
    paginacion quedaria la fila si se buscara sin filtrar."""
    buscador = page.locator(f"#{tabla_id}_filter input[type='search']")
    buscador.fill(texto)
    return page.locator(f"#{tabla_id} tbody tr", has_text=texto).first


def abrir_menu_administrar(fila):
    fila.locator("a.dropdown-toggle").click()
