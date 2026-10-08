import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import csv

reslutado = []

url = input("Digite o URL que quer rastrear: ")#"https://www.python.org/"

resposta = requests.get(url)

if resposta.status_code == 200:
    dados = BeautifulSoup(resposta.text, "html.parser")

    titulo_pagina = dados.title.string if dados.title else "Nem um titulo encontrado"
    print(f" Titulo da Pagina: \n{titulo_pagina}\n")

    h1 = dados.find("h1")
    titulo_principal = h1.text.strip() if h1 else "Nem um h1 encontrado"
    print(f" Titulo Principal: \n{titulo_principal}\n")

    links = dados.find_all("a")
    #print(dados.prettify())

    quantidade_link = len(links)
    testados = 0
    ignorados = 0
    funcionando = 0
    redirecionamentos = 0
    erros_4xx = 0
    erros_5xx = 0
    erros_conexao = 0
    print(f"Quantidade de Links \n{quantidade_link}\n")

    print("Datalhe dos prints \n")

    for i, link in enumerate(links, 1):
        texto = link.text.strip() if link.text else "[Link sem texto]"
        href = link.get('href')

        if not href:
            ignorados +=1

            print(f"{i}. [sem endereço/href] - ignorando")
            print("-"*30)
            continue

        if href.startswith("#"):
            ignorados +=1
            print(f"{i}. {href} - ancora interna - ignorando")
            print("-"*30)
            continue

        scheme = urlparse(href).scheme
        
        if scheme in ("javascript", "mailto", "tel"):
            ignorados +=1
            print(f"{i}. {href} - esquema {scheme} - ignorando")
            print("-"*30)
            continue


        url_completo = urljoin(url, href)
        testados +=1
        
        print(f"{i}. Texto: {texto}")
        print(f"Texto completo: {url_completo}")

        try:
            resposta_link = requests.head(url_completo, timeout=5, allow_redirects=True)
            status = resposta_link.status_code
            reslutado.append({
            "numero": i,
            "texto": texto,
            "url": url_completo,
            "status": status
        })
        except requests.exceptions.RequestException:
          erros_conexao +=1

        if status in (301, 302, 307, 308):
            redirecionamentos +=1
        elif status == 200:
            funcionando +=1
        elif 400 <= status < 500:
            erros_4xx +=1
        elif 500 <= status < 600:
            erros_5xx +=1

        

    print("\nResumo:")
    print(f"Links encontrados: {quantidade_link}")
    print(f"Links testados: {testados}")
    print(f"Links ignorados: {ignorados}")
    print(f"Funcionando: {funcionando}")
    print(f"Redirecionamentos: {redirecionamentos}")
    print(f"Erros 4xx: {erros_4xx}")
    print(f"Erros 5xx: {erros_5xx}")
    print(f"Erros de conexão: {erros_conexao}")
    print("\n Resumo: ")


    with open("relatorio_links.csv", "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["numero", "texto", "url", "status"])
        escritor.writeheader()
        escritor.writerows(reslutado)
else:
     print(f"Erro: {resposta.status_code}")
