import yadisk
from calendar import monthrange
disk = yadisk.YaDisk(token="y0_AgAAAABALxVvAAhfcwAAAADNm_GdxJ2gzsdISuSJfntSvJ0Kaydd99w")
months_dir = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4, 'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8, 'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
years = ["2023"]
months = ["Март", "Апрель", "Май", "Июнь", "Июль", "Август"]
lessons = ["Английский язык", "Биология", "ОБЖ", "История", "Физика", "Химия", "Физ. лаба", "Обществознание"]
for h in lessons:
    for i in years:
        for ii in months:
            for iii in range(1,monthrange(int(i), months_dir[ii])[1]):
                disk.mkdir('conspectbot/' + h + '/' + i + '/' + ii + '/' + str(iii) + '/' + 'ДЗ')
print("я всё сделяль")