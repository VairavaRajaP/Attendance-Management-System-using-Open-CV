from json_excel_converter import Converter
# from json_excel_converter.csv import Writer
from json_excel_converter.xlsx import Writer
from json_excel_converter.xlsx.formats import LastUnderlined, Bold, \
    Centered, Format
import json


def jsontoxl():
    conv = Converter()
    try:
        writer = Writer(file='Attendance_format2.xlsx',
                        header_formats=(
                            Centered, Bold, LastUnderlined,
                            Format({
                                'font_color': 'red'
                            })),
                        data_formats=(
                            Format({
                                'font_color': 'green'
                            }),)
                        )
        data = []
        with open('attendance.json', 'r') as file:
            data.append(json.load(file))
        conv.convert(data, writer)
    except Exception:
        print('Excel file is already open. Please close the file and try again')
