import pandas as pd
import os
import numpy as np

#event - выгрузка участников мероприятия
#[('ФИО1', 'IKG1'), ('FIO2', 'IKG2')]
def event(inp_data):
    data = {"ФИО":[], "ИКГ":[], "Подпись о участии":[]}
    for i in inp_data:
        data['ФИО'].append(i[0])
        data['ИКГ'].append(i[1])
        data['Подпись о участии'].append("_______________")

    output = pd.DataFrame(data)
    output.index = output.index + 1
    path = os.path.dirname(os.path.realpath(__file__))
    path += r"\Список.xlsx"
    output.to_excel(excel_writer=path, index=True)

    return path

