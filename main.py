import re
from datetime import datetime
from collectors.slashdot import RSSCollector
from utils.date_filter import is_recent
from database.database import engine, Base, SessionLocal
from database.models import Noticia


Base.metadata.create_all(engine)

# Para adicionar mais fontes: crie outra classe em collectors/ e inclua aqui.
COLETORES = [RSSCollector]


def normalizar_data(valor):
    """Converte 'on Tuesday July 28, 2026 @07:00PM' para ISO (2026-07-28T19:00:00)."""
    if isinstance(valor, datetime):
        return valor.isoformat()
    m = re.search(r"([A-Za-z]+) (\d{1,2}), (\d{4}) @(\d{1,2}):(\d{2})(AM|PM)", str(valor))
    if m:
        try:
            texto = f"{m[1]} {m[2]} {m[3]} {m[4]}:{m[5]} {m[6]}"
            return datetime.strptime(texto, "%B %d %Y %I:%M %p").isoformat()
        except ValueError:
            pass
    return str(valor)


def coletar_noticias():
    print("\nIniciando coleta...")
    print("Data da coleta:", datetime.now())

    session = SessionLocal()
    total_salvas = 0

    try:
        for Coletor in COLETORES:
            try:
                noticias = Coletor().scrape()
            except Exception as erro:
                print(f"Falha na fonte {Coletor.__name__}: {erro}")
                continue

            for noticia in noticias:
                # Filtro de últimas 24 horas (usa a data original da fonte)
                if not is_recent(noticia["data"]):
                    print(f"Notícia antiga ignorada: {noticia['titulo']}")
                    continue

                # Verifica duplicidade pelo link
                existe = session.query(Noticia).filter_by(link=noticia["link"]).first()
                if existe:
                    print(f"Duplicada ignorada: {noticia['titulo']}")
                    continue

                session.add(Noticia(
                    titulo=noticia["titulo"],
                    autor=noticia["autor"],
                    data=normalizar_data(noticia["data"]),
                    categoria=noticia["categoria"],
                    conteudo=noticia["conteudo"],
                    link=noticia["link"],
                    data_coleta=datetime.now(),
                ))
                total_salvas += 1
                print(f"Salvando: {noticia['titulo']}")

        session.commit()
    except Exception as erro:
        session.rollback()
        print(f"Erro na coleta: {erro}")
    finally:
        session.close()

    print(f"\nFinalizado! {total_salvas} novas notícias salvas.")


# Permite executar manualmente
if __name__ == "__main__":
    coletar_noticias()