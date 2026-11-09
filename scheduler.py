import schedule
import time
from main import coletar_noticias


def coletar_seguro():
    # Um erro numa coleta não pode derrubar o agendador
    try:
        coletar_noticias()
    except Exception as erro:
        print(f"Erro na coleta: {erro}")


coletar_seguro()
schedule.every(30).minutes.do(coletar_seguro)
print("Coletor iniciado...")

while True:
    schedule.run_pending()
    time.sleep(60)