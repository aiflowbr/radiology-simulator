import time
import os
from cron import CronManager
import dicom
import dataset
import tempfile
import random

df, paths = dataset.init(shuffle=True, seed=42)
num_generator = dicom.NonRepeatingIndexGenerator(len(df))


# Função que será chamada periodicamente
def send():
    print("***************")
    print("Generating data")
    dicom.gen_random_dcm(df, paths, num_generator)


# Criando uma instância de CronManager
# cron_manager = CronManager()
# # cron_manager.schedule_function("*/5 * * * *", send)
# INTERVAL = os.environ["INTERVAL"]
# cron_manager.schedule_function(f"*/{INTERVAL} * * * *", send)


# Mantendo a aplicação em execução
# try:
while True:
    send()
    time.sleep(30)
# except KeyboardInterrupt:
# Se o usuário pressionar Ctrl+C, pare o CronManager
# cron_manager.stop()
