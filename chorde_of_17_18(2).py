data_rou_18 = {
    'rou_time': 81,
    'n_car': 6,
    's_time': 336,
    'e_time': 1412
}

data_rou_17 = {
    'rou_time': 62,
    'n_car': 7,
    's_time': 340,
    'e_time': 1406
}



class TabCoRou17: # для 17-го трамвайного маршрута, Кулікове - 11 ст.Фонтана
  DINNER_1 = 585 # 9:45
  MAX_ALLOW = 600 # 10 hours
  DINNER_2 = 1125 # 18:45
  CHANGE = 4
  DINNER_INTERVAL = 12
  
  def __init__(self, rou_time, n_car, s_time, e_time) -> None: 
    # оборотный рейс, количество подвижного состава, время отправления первого вагона и время прибытия последнего в наряде
    self.depo_time = 16 # 16 минут езды из депо на конечную
    self.rou_time = rou_time # время оборотного рейса
    self.n_car = n_car # количество подвижного состава
    self.s_time = s_time # время отправления с конечной первого вагона
    self.e_time = e_time # время прибытия на конечную последнего вагона
    
    self.rou_sched = [] # основная матрица наряда

    self.rou_int = self.get_interval() # функція що вертає список цілочисельних інтервалів для наряду
    # 'rou_capability' функция дает список начальных отправлений вагонов в 1 смене, список времени конца смены (1,2)
    self.rou_start = self.rou_capability(self.s_time, self.e_time, self.rou_time, self.depo_time, self.rou_int)[0]
    self.change_list_1 = self.rou_capability(self.s_time, self.e_time, self.rou_time, self.depo_time, self.rou_int)[1]
    self.change_list_2 = self.rou_capability(self.s_time, self.e_time, self.rou_time, self.depo_time, self.rou_int)[2]
    self.shift_1 = self.rou_capability(self.s_time, self.e_time, self.rou_time, self.depo_time, self.rou_int)[3][0] # кол-во обороток 1 смены
    self.shift_2 = self.rou_capability(self.s_time, self.e_time, self.rou_time, self.depo_time, self.rou_int)[3][1] # кол-во обороток 2 смены
    self.rou_start_2 =  list(map(lambda x: self.CHANGE + x, self.change_list_1))

    # Вызываем методы
    self.turn_1() # матрица 1 смены
    self.turn_2() # матрица 1 смены
    # приходится использовать метод только раз, чтобы не провоцировать дублирующие значения!)
    self.__repr__()

  def get_interval(self):
    rou_int = [] 
    if self.rou_time % self.n_car == 0: # обращаюсь к атрибутам конструктора __init__, если делится нацело...
        div = int (self.rou_time / self.n_car) 
        for i in range(self.n_car):
            rou_int.append (div) # кидаем в список все интервалы по количеству транспорта
    elif self.rou_time % self.n_car != 0: # если не делится на 0
        min_div = self.rou_time // self.n_car # минимальный делитель
        max_div = self.rou_time // self.n_car + 1 # максимальный делитель
        qa_max = self.rou_time % self.n_car # количество максимальных делителей находим путем нахождения остатка при делении
        qa_min = int ((self.rou_time - max_div * qa_max) / min_div) # количество минимальных делителей
        for i in range(qa_max):
            rou_int.append(max_div)
        for i in range(qa_min):
            rou_int.append(min_div)
    return rou_int
  
  
  def rou_capability(self, s_time, e_time, rou_time, depo_time, interval): # функция для расчета основных параметров будущего наряда
    rou_start = []
    rou_qua_shift = [] # основная матрица
 # больше 10 часов запрещено работать
    
    for i in range(len(interval)): # проходим циклом по кол-во интервалов
        if len(rou_start) == 0: # если ничего нет кидаем начальное время
          rou_start.append(s_time)
        else:
          s_time += interval[i] # затем прибавляем интервалы и заносим в список
          rou_start.append(s_time)
          
    rou_qua_shift.append(rou_start)
    
    pause_1 = 12 + 4 + 12 # обед = 12 + пересменка = 4
    pause_list = list(x + pause_1 for x in rou_start) # делаем отдельный список для всех пауз
    rou_list = pause_list.copy()

    while rou_list[-1] <= e_time: # пока последний элемент списка оборотного рейса меньше конечного времени
      rou_qua_shift.append(rou_list)
      rou_list = list(map(lambda x: rou_time + x, rou_list)) # добавляем к элементам оборотное время - накручиваем круги
    
    end_list = [] # верстаем последний список
    for i in rou_list:
      if i < e_time:
        end_list.append(i)
      else:
        end_list.append(0) # выбрал "0" т.к. с пробелом тяжело потом сравнивать и др.операции делать
      
    if end_list.count(0) != len(rou_start): # если с "0" элементы кидаем в основу
      rou_qua_shift.append(end_list)
      
    sched_qa = ((len(rou_qua_shift) - 2) - (len(rou_qua_shift) - 2)//2, (len(rou_qua_shift) - 2)//2)
    # отнимаю 2 списка из-за паузы и начального списка, получаю кортеж из кол-во 2-х смен
    time_1_shift = sched_qa[0] * rou_time + 12 # кол-во рейсов * оборотный рейс и добавляю обед
    time_2_shift = sched_qa[1] * rou_time + 12 # дли-ность рабочей смены в минутах
    if time_1_shift + depo_time > self.MAX_ALLOW: #
      return 'time for 1 shift out of permission'
    if time_2_shift + depo_time > self.MAX_ALLOW:
      return 'time for 2 shift out of permission'
    
    for i in rou_start:
      change_list_1 = list(map(lambda x: x + time_1_shift, rou_start)) # список стартовый с прибавлением дли-ности рабсмены
    change_list_2 = rou_qua_shift[-1] # последний список - конец 2-й смены
    
    return rou_start, change_list_1, change_list_2, sched_qa, time_1_shift, time_2_shift 
  
  
  def turn_1(self):

    cur_list = self.rou_start

    for i in range((self.shift_1 + 1)//2): # +1 cause range count till Number

      self.rou_sched.append(cur_list)
      cur_list = [x + self.rou_time for x in self.rou_sched[-1]]
    
    if cur_list[-1] < self.DINNER_1:
      self.rou_sched.append(cur_list)
      cur_list = [x + self.rou_time for x in self.rou_sched[-1]]
      self.rou_sched.append(cur_list)
      self.rou_sched.append(list(map(lambda x: self.DINNER_INTERVAL + x, cur_list)))
    elif cur_list[-1] >= self.DINNER_1:
      self.rou_sched.append(cur_list) # add cur_list cause he left in memory but    
      # in previous iteration hasn`t been added`
      self.rou_sched.append(list(map(lambda x: self.DINNER_INTERVAL + x, cur_list)))

    cur_list = self.rou_sched[-1]

    while all(x < y for x, y in zip(cur_list, self.change_list_1)):
      cur_list = [x + self.rou_time for x in cur_list]
      self.rou_sched.append(cur_list)
    
    return self.rou_sched
    
    
  def turn_2(self):

    cur_list = self.rou_start_2

    for i in range((self.shift_2 + 1)//2): # +1 cause range count till Number

      self.rou_sched.append(cur_list)
      cur_list = [x + self.rou_time for x in self.rou_sched[-1]]

    if cur_list[-1] < self.DINNER_2:
      self.rou_sched.append(cur_list)
      cur_list = [x + self.rou_time for x in self.rou_sched[-1]]
      self.rou_sched.append(cur_list)
      self.rou_sched.append(list(map(lambda x: self.DINNER_INTERVAL + x, cur_list)))
    elif cur_list[-1] >= self.DINNER_2:
      self.rou_sched.append(cur_list) # add cur_list cause he left in memory but    
      # in previous iteration hasn`t been added`
      self.rou_sched.append(list(map(lambda x: self.DINNER_INTERVAL + x, cur_list)))

    cur_list = self.rou_sched[-1]

    # while all(x < y for x, y in zip(cur_list, self.change_list_2)):
    while cur_list[0] < self.change_list_2[0]:
      cur_list = [x + self.rou_time for x in cur_list]
      self.rou_sched.append(cur_list)
    
    self.rou_sched[-1] = self.change_list_2 # меняю последний список на норм с нулями т.к. траблы с функцией при использовании "0" происходят

    return self.rou_sched
  
  def __repr__(self):
        # Це дозволяє вам краще відображати об'єкти класу при виведенні
        return f"TabCoRou17(rou_time={self.rou_time}, n_car={self.n_car}, s_time={self.s_time}, e_time={self.e_time})"

  def find_optimal_schedule(self, time_range=8):
      counter_of_variants = 0
      s_time_18 = data_rou_18['s_time']
      s_time_17 = data_rou_17['s_time']

      for val_18 in range(-time_range, time_range + 1):  # Проверяем сдвиг от -8 до +8 минут для 9-го маршрута
          for val_17 in range(-time_range, time_range + 1):  # Проверяем сдвиг от -8 до +8 минут для 10-го маршрута
              # Создаем новые расписания с учетом сдвигов
              new_data_rou_18 = {
                  'rou_time': 81,
                  'n_car': 6,
                  's_time': s_time_18 + val_18,
                  'e_time': 1412
              }
              new_data_rou_17 = {
                  'rou_time': 62,
                  'n_car': 7,
                  's_time': s_time_17 + val_17,
                  'e_time': 1406
              }


              sched18 = TabCoRou17(**new_data_rou_18)
              sched17 = TabCoRou17(**new_data_rou_17)
              print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
              print(f"self.sched18 = TabCoRou17({new_data_rou_18['rou_time']}, {new_data_rou_18['n_car']}, {new_data_rou_18['s_time']}, {new_data_rou_18['e_time']})")
              print(f"self.sched17 = TabCoRou17({new_data_rou_17['rou_time']}, {new_data_rou_17['n_car']}, {new_data_rou_17['s_time']}, {new_data_rou_17['e_time']})")
              counter_of_variants += 1
              print(counter_of_variants)

              #(list_17, list_18, mistakes_17_18, errors) = repair_chord(sched17.rou_sched, sched18.rou_sched)
              #row_17_dict = po_comp_17(list_17)
              #row_18_dict = po_comp_18(list_18)
              #tram_17_dict = fix_norma_points_17(row_17_dict)
              #tram_18_dict = fix_norma_points_18(row_18_dict)
              #compare_mistakes(tram_17_dict, tram_18_dict)

              print("--------------------------------------------------------------------------------------------------------------------------------------")
              return  sched18 , sched17




sched17 = TabCoRou17(62, 7, 340, 1406) #5.40, 5.52, 5.33 \ 23.26, 23.37, 23.51
print(sched17.rou_sched) # метод __repr__ автоматично дає таку інфу TabCoRou17(rou_time=62, n_car=7, s_time=340, e_time=1410)

sched18 = TabCoRou17(81, 6, 336, 1412) #5.36, 5.25, 5.47 \ 23.32, 23.26, 23.43
print(sched18.rou_sched)
#print(f'Quantity of lists: {len(sched1.rou_sched)}') # to check if quantity of lists real


print('   ')
# t_17_row_list = sched17_1.rou_sched
# t_18_row_list = sched18_1.rou_sched

#sched18.find_optimal_schedule()

def repair_chord(obj_17, obj_18):

    error_list = [] # список для ошибок ко внутреннему пользаванию и анализа
    for i, sublist1 in enumerate(obj_17): # прохожу циклом по меньшему маршу и более неповоротливому в плане диапазона +-2
        for j, element17 in enumerate(sublist1):
            for m, sublist2 in enumerate(obj_18): # прохожу по циклу в 18-м марше
                for n, element18 in enumerate(sublist2):
                    if abs(element17 - element18) < 4: # ищу ошибки между связкой в интервале 4 мин.
                        # внизу условие, которое отсекает заходы на конечные перед обедом или пересменкой, т.к. вагон выходит из оборота/марша и не мешает другим
                        if (i + 1 < len(obj_17) and abs(obj_17[i + 1][j] - obj_17[i][j]) < 20) and (m > 0 and abs(obj_18[m][n] - obj_18[m - 1][n]) < 20) \
                        or (i > 0 and abs(obj_17[i][j] - obj_17[i - 1][j]) < 20) and (m + 1 < len(obj_18) and abs(obj_18[m + 1][n] - obj_18[m][n]) < 20):
                            continue
                        # закидываю в историю ошибок
#######################################################3#print(f'Разница между точками 17-го марша {element17} и 18-го марша {element18} = {element17 - element18}')
                        error_list.append(("17марш, оборот №  ", i, 'вагон № ', j, 'время ', '{:02}:{:02}'.format(element17 // 60, element17 % 60), \
                         "18марш, оборот № ", m, 'вагон №', n, 'время: ', '{:02}:{:02}'.format(element18 // 60, element18 % 60), "'Разница между точками 17-го и 18-го марша ", (element17 - element18)))
                        # следующее условие назвали "вилкой", это когда пересменка вагона находится на общей диспетчерской и эта пауза в 4 мин.для 1 вагона попадает между
                        # соседними вагонами, нарушая интервал (заходит на пересменку с 1-м, выходит из нее со 2-м a = [834, 838] b = [831, 839])
                        if (m + 1 < len(obj_18) and j + 1 < len(obj_17[i]) and
                                all([obj_17[i][j] < obj_18[m + 1][n] < obj_17[i][j + 1],
                                     obj_17[i][j] < obj_18[m][n] < obj_17[i][j + 1]]) and
                                obj_18[m + 1][n] - obj_18[m][n] < 5):
                            print('fork')
                            obj_17[i][j] -= 1.01

                            obj_17[i][j + 1] += 1.01

                            # ниже учтены разные нюансы при разнице между крайними вагонами др.марша
                            if (m + 1 < len(obj_18) and n + 1 < len(obj_18[m]) and i + 1 < len(obj_17) and
                                    abs(obj_18[m][n + 1] - obj_17[i + 1][j]) == 2 and abs(
                                        obj_17[i][j] - obj_18[m][n]) == 2):

                                obj_18[i + 1][j] -= 1.01
                                #print(f'new_val_9 = {obj_18[m][n]}, new_val_10 = {obj_17[i + 1][j]}')


                            elif (m + 1 < len(obj_18) and n + 1 < len(obj_18[m]) and i + 1 < len(obj_17) and
                                  abs(obj_18[m][n + 1] - obj_17[i + 1][j]) == 3 and abs(
                                        obj_17[i][j] - obj_18[m][n]) == 2):

                                obj_18[i][j] += 1.01
                                #print(f'new_val_9 = {obj_18[m][n]}, new_val_10 = {obj_17[i][j]}')


                            elif (m + 1 < len(obj_18) and n + 1 < len(obj_18[m]) and i + 1 < len(obj_17) and
                                  abs(obj_18[m][n + 1] - obj_17[i + 1][j]) >= 4 and abs(
                                        obj_17[i][j] - obj_18[m][n]) == 2):

                                obj_18[i][j] += 1.01
                                obj_18[i + 1][j] += 1.01
                                #print(f'new_val_9 = {obj_18[m][n + 1]}, new_val_10 = {obj_17[i + 1][j]}')


                            elif (m + 1 < len(obj_18) and n + 1 < len(obj_18[m]) and i + 1 < len(obj_17) and
                                  abs(obj_18[m][n + 1] - obj_17[i + 1][j]) == 2 and abs(
                                        obj_17[i][j] - obj_18[m][n]) >= 4):

                                obj_18[i][j] -= 1.01
                                obj_18[i + 1][j] -= 1.01
                                #print(f'new_val_9 = {obj_18[m][n + 1]}, new_val_10 = {obj_17[i + 1][j]}')

                            elif obj_17[i][j] == obj_18[m][n]:
                                obj_18[m][n] -= 2.02
                                obj_17[i][j] += 1.01
                                obj_17[i][j + 1] += 1.01
                                #print(f'new_val_9 = {obj_18[m][n]}, new_val_10 = {obj_17[i][j]}')
                                if abs(obj_18[m + 1][n] - obj_17[i][j + 1]) > 4:
                                    obj_18[m + 1][n] += 1.01
                                    #print(f'new_val_9 = {obj_18[m + 1][n]}, new_val_10 = {obj_17[i][j + 1]}')
                                elif abs(obj_18[m + 1][n] - obj_17[i][j + 1]) < 4 and abs(
                                        (obj_17[i][j + 1] - obj_18[m][n])) > 3 and abs(
                                    obj_18[m + 1][n] - obj_17[i][j]) > 3:
                                    obj_18[m + 1][n] -= 1.01
                                    #print(f'new_val_9 = {obj_18[m + 1][n]}, new_val_10 = {obj_17[i][j + 1]}')
                                elif abs(obj_18[m + 1][n] - obj_17[i][j + 1]) < 4:
                                    obj_17[i][j + 1] += 1.01
                                    #print(f'new_val_9 = {obj_18[m + 1][n]}, new_val_10 = {obj_17[i][j + 1]}')


                            elif (i + 1 < len(obj_17) and n + 1 < len(obj_18[m]) and j < len(obj_17[i + 1]) and
                                  obj_17[i + 1][j] == obj_18[m][n + 1]):

                                obj_18[m + 1][n] += 2.02
                                obj_17[m][n + 1] -= 1.01
                                obj_17[m][n] -= 1
                                #print(f'new_val_9 = {obj_18[m + 1][n]}, new_val_10 = {obj_17[i][j + 1]}')
                                if abs(obj_18[m][n] - obj_17[i][j]) > 4:
                                    obj_18[m][n] -= 1.01
                                    #print(f'new_val_9 = {obj_18[m][n]}')
                                elif abs(obj_18[m][n] - obj_17[i][j]) < 4 and abs(obj_17[i][j + 1] - obj_18[m][n]) > 3:
                                    obj_18[m][n] += 1.01
                                    #print(f'new_val_9 = {obj_18[m][n]}')
                            # здесь представлен легкий граничный вариант, который в последующей контролке выравнивают +-1 минутой
                            elif abs(obj_18[m + 1][n] - obj_17[i][j + 1]) == 3 and abs(
                                    obj_17[i][j] - obj_18[m][n]) == 3:
                                continue

                            continue # после манипуляций с "вилкой" пропускаю дальнейшие условия и действия, т.к. здесь учтены (наверное)) все варики, х.з.

    # продолжаю функцию по отладке интервалов между разными маршрутами
                        if (element17 - element18) == 0:
                            # т.к. в обоих вагонах изменяем время на 2 мин. ниже отлавливаю условие, когда предыдущий оборот уже был изменен на 1+мин., при чем
                            # приходится давать машине связку соседних элементов, чтобы она понимала, какую разницу держать в уме (4 - смена, 12 - обед трам, 81 - оборот у 18-го)
                            if (m > 0 and\
                                (obj_18[m][n] - obj_18[m -1][n] > 81 and ((n + 1 < len(obj_18[m]) and obj_18[m][n + 1] - obj_18[m -1][n + 1] == 81) or (n > 0 and obj_18[m][n - 1] - obj_18[m -1][n - 1] == 81)))\
                                or (obj_18[m][n] - obj_18[m -1][n] > 12 and ((n + 1 < len(obj_18[m]) and obj_18[m][n + 1] - obj_18[m -1][n + 1] == 12) or (n > 0 and obj_18[m][n - 1] - obj_18[m -1][n - 1] == 12)))\
                                or (obj_18[m][n] - obj_18[m -1][n] > 4 and ((n + 1 < len(obj_18[m]) and obj_18[m][n + 1] - obj_18[m -1][n + 1] == 4) or (n > 0 and obj_18[m][n - 1] - obj_18[m -1][n - 1] == 4)))\
                                or (i > 0 and obj_17[i][j] - obj_17[i - 1][j] < 62)): # add condition if some changes in 17th route
                                #print(f'obj_18[m][n] = {obj_18[m][n]}, obj_18[m -1][n] = {obj_18[m -1][n]}, diff = {obj_18[m][n] - obj_18[m -1][n]}; ')
                                obj_18[m][n] -= 2.02
                                obj_17[i][j] += 2.02
                                #print(f'new_val_18 = {obj_18[m][n]}, new_val_17 = {obj_17[i][j]}')
                            # во всех других случаях увеличиваю оборот у 18-го (хотя еще не уверен, как лучше - все равно увеличение потом приходится нивелировать, чтобы прийти
                            # к идеальному интревалу)
                            else:
                                obj_18[m][n] += 2.02
                                obj_17[i][j] -= 2.02
                                #print(f'new_val_18 = {obj_18[m][n]}, new_val_17 = {obj_17[i][j]}')

                        elif (element17 - element18) == 1:
                            obj_17[i][j] += 1.01
                            obj_18[m][n] -= 2.02
                            #print(f'new_val_18 = {obj_18[m][n]}, new_val_17 = {obj_17[i][j]}')

                        elif (element17 - element18) == 2:
                            obj_17[i][j] += 1.01
                            obj_18[m][n] -= 1.01
                            #print(f'new_val_18 = {obj_18[m][n]}, new_val_17 = {obj_17[i][j]}')

                        elif (element17 - element18) == 3:
                            obj_18[m][n] -= 1
                            #print(f'new_val_18 = {obj_18[m][n]}')

                        elif (element17 - element18) == -1:
                            obj_17[i][j] -= 1.01
                            obj_18[m][n] += 2.02
                            #print(f'new_val_18 = {obj_18[m][n]}, new_val_17 = {obj_17[i][j]}')

                        elif (element17 - element18) == -2:
                            obj_17[i][j] -= 1.01
                            obj_18[m][n] += 1.01
                            #print(f'new_val_18 = {obj_18[m][n]}, new_val_17 = {obj_17[i][j]}')

                        elif (element17 - element18) == -3:
                            obj_18[m][n] += 1.01
                            #print(f'new_val_18 = {obj_18[m][n]}')

                    elif (element18 + 4) > element17:
                        break # прерываю цикл в итерации для экономии времени

    return obj_17, obj_18, len(error_list), error_list

list_17, list_18, mistakes_17_18, errors = repair_chord(sched17.rou_sched, sched18.rou_sched)

tram17_dict = {'Кул.поле': [], # 
               'Среднеф': [], # +9
               '6ст. Б.Ф': [], # +18
               '11ст. Б.Ф': [], # +29
               '11ст. Б.Ф.': [], # +31
               '6ст. Б.Ф.': [], # +42
               'Среднеф.': [], # +50
               'Кул.поле.': [],} # +58 \+4 stand for 17/18 routes- чи він стоїть на Куліковом 4 хв.???  


def po_comp_17(obj_list): # point_compilation
    obj_dict = {}
    # Створюємо список списків - матрицю по кожному оберту в наряді
    for key in tram17_dict: # ітерує ключі
        obj_dict[key] = [[] for i in range(len(obj_list))]

    for i in range(len(obj_list)):
        for j in range(len(obj_list[i])):

            obj_dict['Кул.поле'][i].append(obj_list[i][j])
            # от контрольной точки иду вниз по связке до ее выхода
            if i > 0 and obj_list[i][j] != 0 and abs(obj_list[i][j] - obj_list[i - 1][j]) > 20:
                obj_dict['Кул.поле.'][i].append(obj_list[i][j] - 4)
                obj_dict['Среднеф.'][i].append(obj_list[i][j] - 12)
                obj_dict['6ст. Б.Ф.'][i].append(obj_list[i][j] - 20)
                obj_dict['11ст. Б.Ф.'][i].append(obj_list[i][j] - 31)
            # от контрольной точки иду вверх по связке до ее выхода
            if i < (len(obj_list) - 1) and obj_list[i][j] != 0 and obj_list[i + 1][j] != 0 and abs(obj_list[i + 1][j] - obj_list[i][j]) > 20:
                obj_dict['Среднеф'][i].append(obj_list[i][j] + 9)
                obj_dict['6ст. Б.Ф'][i].append(obj_list[i][j] + 18)
                obj_dict['11ст. Б.Ф'][i].append(obj_list[i][j] + 29)
                
    for key in list(obj_dict.keys()):
        obj_dict[key] = [sublist for sublist in obj_dict[key] if sublist]  # Видаляємо порожні підсписки      

    return obj_dict

tram18_dict = {'Кул.поле': [], # 
               'Среднеф': [], # +9
               '6ст. Б.Ф': [], # +18
               '11ст. Б.Ф': [], # +29
               '16ст. Б.Ф': [], # +39
               '16ст. Б.Ф.': [], # +41 
               '11ст. Б.Ф.': [], # +50
               '6ст. Б.Ф.': [], # +61
               'Среднеф.': [], # +69
               'Кул.поле.': [],} # +79 \+4 stand for 17/18 routes - чи він стоїть на Куліковом 4 хв.??? 

def po_comp_18(obj_list): # point_compilation
    obj_dict = {}
    # Створюємо список списків - матрицю по кожному оберту в наряді
    for key in tram18_dict: # ітерує ключі
        obj_dict[key] = [[] for i in range(len(obj_list))]

    for i in range(len(obj_list)):
        for j in range(len(obj_list[i])):

            obj_dict['Кул.поле'][i].append(obj_list[i][j])
            # от контрольной точки иду вниз по связке до ее выхода и дальше
            if i > 0 and obj_list[i][j] != 0 and abs(obj_list[i][j] - obj_list[i - 1][j]) > 20:
                obj_dict['Кул.поле.'][i].append(obj_list[i][j] - 4)
                obj_dict['Среднеф.'][i].append(obj_list[i][j] - 12)
                obj_dict['6ст. Б.Ф.'][i].append(obj_list[i][j] - 20)
                obj_dict['11ст. Б.Ф.'][i].append(obj_list[i][j] - 31)
                obj_dict['16ст. Б.Ф.'][i].append(obj_list[i][j] - 40)
            # от контрольной точки иду вверх по связке до ее выхода и дальше
            if i < (len(obj_list) - 1) and obj_list[i][j] != 0 and obj_list[i + 1][j] != 0 and abs(obj_list[i + 1][j] - obj_list[i][j]) > 20:
                obj_dict['Среднеф'][i].append(obj_list[i][j] + 9)
                obj_dict['6ст. Б.Ф'][i].append(obj_list[i][j] + 18)
                obj_dict['11ст. Б.Ф'][i].append(obj_list[i][j] + 29)
                obj_dict['16ст. Б.Ф'][i].append(obj_list[i][j] + 39)
                
    for key in list(obj_dict.keys()):
        obj_dict[key] = [sublist for sublist in obj_dict[key] if sublist]  # Видаляємо порожні підсписки      

    return obj_dict


row_17_dict = po_comp_17(list_17)
row_18_dict = po_comp_18(list_18)


def fix_norma_points_17(obj):
    print('analyze_norma_17')
    def cleaner_list_nei_keys(obj):
    # для проверки 0-го ключа с ключом предыдущим -1 из-за разницы в кол-во подсписков ввиду пересменки и обеда
        new_obj = []

        for i in range(1, len(obj)):
            new_list = []
            for j in range(len(obj[i])):
                if abs(obj[i][j] - obj[i - 1][j]) > 20:
                    new_list.append(obj[i][j])

            if new_list != []:
                new_obj.append(new_list)
        
        # для проверки 0-го ключа с ключом следующим +1
        new_obj_1 = []

        for i in range(len(obj) - 1):
            new_list = []
            for j in range(len(obj[i])):
                if abs(obj[i + 1][j] - obj[i][j]) > 20:
                    new_list.append(obj[i][j])

            if new_list != []:
                new_obj_1.append(new_list)
        
        return new_obj, new_obj_1


    add_17 = [4, 9, 9, 11, 2, 11, 8, 8] # время прохождения контролок в минутах
    keys = list(obj.keys())
    # беру с 3-го элемента, чтобы отнимать предыдущий, а 0 и 1 считаю отдельно, т.к. там нужно корректировать список из-за пересменки и обеда
    for index_key in range(2, len(keys)): 
        key = keys[index_key]
        prev_key = keys[index_key - 1]
######################################################3##print('cur_key: ', key, 'prev_key: ', prev_key)
        for i in range(len(obj[key])):
            for j in range(len(obj[key][i])):
                # if i < len(obj[key]) and j < len(obj[key][i]):
                    if (obj[key][i][j] - obj[prev_key][i][j]) >= add_17[index_key] - 1:
                        continue
                    elif (obj[key][i][j] - obj[prev_key][i][j]) == add_17[index_key] - 2:
                        print(f'cur_el: {obj[key][i][j]} = {'{:02}:{:02}'.format(obj[key][i][j] // 60, obj[key][i][j] % 60)}, prev_el: {obj[prev_key][i][j]},\
                               dif = {obj[key][i][j] - obj[prev_key][i][j]}, should be - {add_17[index_key]}')
                        obj[prev_key][i][j] -= 1
                    elif (obj[key][i][j] - obj[prev_key][i][j]) == add_17[index_key] - 3:
                        print(f'cur_el: {obj[key][i][j]} = {'{:02}:{:02}'.format(obj[key][i][j] // 60, obj[key][i][j] % 60)}, prev_el: {obj[prev_key][i][j]},\
                               dif = {obj[key][i][j] - obj[prev_key][i][j]}, should be - {add_17[index_key]}')
                        obj[prev_key][i][j] -= 1
                        obj[key][i][j] += 1

    a0 = cleaner_list_nei_keys(obj['Кул.поле'])[0] # Кул.поле для 'Кул.поле.'
    a1 = cleaner_list_nei_keys(obj['Кул.поле'])[1] # Кул.поле для 'Среднеф'
    
    # снизу условие, которое отсекает подсписки с началом раздвоений: обеда/пересменок 
    
    print('cur_key: Кул.поле', 'prev_key: Кул.поле.')
    for i in range(len(a0)):
        # if i > 0:
            for j in range(len(a0[i])):
                if i < len(obj['Кул.поле.']) and j < len(obj['Кул.поле.'][i]):
                    if (a0[i][j] - obj['Кул.поле.'][i][j])  in [add_17[0], add_17[0] + 1, add_17[0] - 1]:
                        continue
                    else:
                        print(f'cur_el: {a0[i][j]} = {'{:02}:{:02}'.format(a0[i][j] // 60, a0[i][j] % 60)}, prev_el: {obj['Кул.поле.'][i][j]},\
                               dif = {a0[i][j] - obj['Кул.поле.'][i][j]}, should be - {add_17[0]}')

    print('cur_key: Кул.поле', 'prev_key: Среднеф')
    for i in range(len(a1)):
        # if i > 0:
            for j, val in enumerate(a1[i]):
                if i < len(obj['Среднеф']) and j < len(obj['Среднеф'][i]):
                    if (obj['Среднеф'][i][j] - a1[i][j])  in [add_17[1], add_17[1] + 1, add_17[1] - 1]:
                        continue
                    else:
                        print(f'cur_el: {a1[i][j]} = {'{:02}:{:02}'.format(a1[i][j] // 60, a1[i][j] % 60)}, prev_el: {obj['Среднеф'][i][j]} = {'{:02}:{:02}'.format(val // 60, val % 60)},\
                               dif = {obj['Среднеф'][i][j] - a1[i][j]}, should be - {add_17[1]}')
                        
    return obj


tram_17_dict = fix_norma_points_17(row_17_dict)


def fix_norma_points_18(obj):
    print('analyze_norma_18')

    def cleaner_list_nei_keys(obj):
    # для проверки 0-го ключа с ключом предыдущим -1 из-за разницы в кол-во подсписков ввиду пересменки и обеда
        new_obj = []

        for i in range(1, len(obj)):
            new_list = []
            for j in range(len(obj[i])):
                if abs(obj[i][j] - obj[i - 1][j]) > 20:
                    new_list.append(obj[i][j])

            if new_list != []:
                new_obj.append(new_list)
        
        # для проверки 0-го ключа с ключом следующим +1
        new_obj_1 = []

        for i in range(len(obj) - 1):
            new_list = []
            for j in range(len(obj[i])):
                if abs(obj[i + 1][j] - obj[i][j]) > 20:
                    new_list.append(obj[i][j])

            if new_list != []:
                new_obj_1.append(new_list)
        
        return new_obj, new_obj_1


    add_18 = [4, 9, 9, 11, 10, 2, 9, 11, 8, 8] # время прохождения контролок в минутах
    keys = list(obj.keys())
    # беру с 3-го элемента, чтобы отнимать предыдущий, а 0 и 1 считаю отдельно, т.к. там нужно корректировать список из-за пересменки и обеда
    for index_key in range(2, len(keys)):
        key = keys[index_key]
        prev_key = keys[index_key - 1]
        print('cur_key: ', key, 'prev_key: ', prev_key)
        for i in range(len(obj[key])):
            for j in range(len(obj[key][i])):
                # if i < len(obj[key]) and j < len(obj[key][i]):
                    if (obj[key][i][j] - obj[prev_key][i][j]) >= add_18[index_key] - 1:
                        continue
                    elif (obj[key][i][j] - obj[prev_key][i][j]) == add_18[index_key] - 2:
                        print(f'cur_el: {obj[key][i][j]} = {'{:02}:{:02}'.format(obj[key][i][j] // 60, obj[key][i][j] % 60)}, prev_el: {obj[prev_key][i][j]},\
                               dif = {obj[key][i][j] - obj[prev_key][i][j]}, should be - {add_18[index_key]}')
                        obj[prev_key][i][j] -= 1
                    elif (obj[key][i][j] - obj[prev_key][i][j]) == add_18[index_key] - 3:
                        print(f'cur_el: {obj[key][i][j]} = {'{:02}:{:02}'.format(obj[key][i][j] // 60, obj[key][i][j] % 60)}, prev_el: {obj[prev_key][i][j]},\
                               dif = {obj[key][i][j] - obj[prev_key][i][j]}, should be - {add_18[index_key]}')
                        obj[prev_key][i][j] -= 1
                        obj[key][i][j] += 1
                        
    a0 = cleaner_list_nei_keys(obj['Кул.поле'])[0] # Кул.поле для 'Кул.поле.'
    a1 = cleaner_list_nei_keys(obj['Кул.поле'])[1] # Кул.поле для 'Среднеф'
    
    # снизу условие, которое отсекает подсписки с началом раздвоений: обеда/пересменок 
    
    print('cur_key: Кул.поле', 'prev_key: Кул.поле.')
    for i in range(len(a0)):
        # if i > 0:
            for j in range(len(a0[i])):
                if i < len(obj['Кул.поле.']) and j < len(obj['Кул.поле.'][i]):
                    if (a0[i][j] - obj['Кул.поле.'][i][j])  in [add_18[0], add_18[0] + 1, add_18[0] - 1]:
                        continue
                    else:
                        print(f'cur_el: {a0[i][j]}, prev_el: {obj['Кул.поле.'][i][j]},\
                               dif = {a0[i][j] - obj['Кул.поле.'][i][j]}, should be - {add_18[0]}')
                        # obj['Кул.поле.'][i][j] -= 1 заглушка на випадок дефектів, але поки не зустрічав тому і залишив)

    print('cur_key: Кул.поле', 'prev_key: Среднеф')
    for i in range(len(a1)):
        # if i > 0:
            for j in range(len(a1[i])):
                if i < len(obj['Среднеф']) and j < len(obj['Среднеф'][i]):
                    if (obj['Среднеф'][i][j] - a1[i][j])  in [add_18[1], add_18[1] + 1, add_18[1] - 1]:
                        continue
                    else:
                        print(f'cur_el: {a1[i][j]}, prev_el: {obj['Среднеф'][i][j]},\
                               dif = {obj['Среднеф'][i][j] - a1[i][j]}, should be - {add_18[1]}')
                        
    return obj
                        
tram_18_dict = fix_norma_points_18(row_18_dict)



print('Виправлений 17 марш')

for key, value in tram_17_dict.items(): # tuple of dict (key, value)
  print(f'{key}:')
  for sublist in value:
    print(f' {sublist},')
  print('\n') # for space between matrices

print('Виправлений 18 марш')

for key, value in tram_18_dict.items(): # tuple of dict (key, value)
  print(f'{key}:')
  for sublist in value:
    print(f' {sublist},')
  print('\n') # for space between matrices


# эта функция не очень хорошо работает т.к. не отлавливает пересменки и обеды
def compare_mistakes(obj1, obj2):
  
  counter_mistake = 0
  for key in obj1:
      tup_key = tuple(element for sublist in obj2[key] for element in sublist)
      print(f'Сравнение прохождения конт точки на {key}: ')
      counter = 0
      for sublist in obj1[key]:
         for item1 in sublist:
            for item2 in tup_key:
               if abs(item1 - item2) < 4:
                  #print(f'Разница между {item1} и {item2} = {abs(item1 - item2)}')
                  counter += 1
      print(f'Кол-во ошибок для остановки {key} = {counter}')
      counter_mistake += counter

      print(f'Кол-во ошибок при сравнении маршрутов = {counter_mistake}')

      return f'Кол-во ошибок при сравнении маршрутов = {counter_mistake}'


compare_mistakes(tram_17_dict, tram_18_dict)



print('Виправлена звязка!')

def get_hours(obj):
    con_dict = {}
    for key in obj:
        point_matrix = []  # Цей список буде зберігати всі перетворені підсписки для даного ключа
        for sublist in obj[key]:
            new_sublist = []
            for j in sublist:
                if j > 1439:
                    raise ValueError("Wrong time: more than 24 hours in a day!")
                elif j == 0:
                    new_sublist.append('--:--')
                else:
                    new_sublist.append('{:02}:{:02}'.format(j // 60, j % 60))
            point_matrix.append(new_sublist)  # Додаємо перетворений підсписок до списку перетворених часів
        con_dict[key] = point_matrix  # Записуємо у словник новий список підсписків
    return con_dict


route_17 = get_hours(tram_17_dict)
route_18 = get_hours(tram_18_dict)


print('Виправлений 17 марш')
for key, value in route_17.items(): # tuple of dict (key, value)
  print(f'{key}:')
  for sublist in value:
    print(f' {sublist},')
  print('\n') # for space between matrices

print('Виправлений 18 марш')
for key, value in route_18.items(): # tuple of dict (key, value)
  print(f'{key}:')
  for sublist in value:
    print(f' {sublist},')
  print('\n') # for space between matrices


def comparison_of_scheduls():
    def find_optimal_schedule(time_range=8):
        counter_of_variants = 0
        s_time_18 = data_rou_18['s_time']
        s_time_17 = data_rou_17['s_time']

        # Переменные для хранения оптимального результата
        best_sched17 = None
        best_sched18 = None
        min_mistakes = float('inf')  # Начинаем с бесконечности, чтобы любое найденное значение было меньше
        best_variant_number = None  # Для хранения номера лучшего варианта

        for val_18 in range(-time_range, time_range + 1):  # Проверяем сдвиг от -8 до +8 минут для 9-го маршрута
            for val_17 in range(-time_range, time_range + 1):  # Проверяем сдвиг от -8 до +8 минут для 10-го маршрута
                # Создаем новые расписания с учетом сдвигов
                new_data_rou_18 = {
                    'rou_time': 81,
                    'n_car': 6,
                    's_time': s_time_18 + val_18,
                    'e_time': 1412
                }
                new_data_rou_17 = {
                    'rou_time': 62,
                    'n_car': 7,
                    's_time': s_time_17 + val_17,
                    'e_time': 1406
                }

                sched18 = TabCoRou17(**new_data_rou_18)
                sched17 = TabCoRou17(**new_data_rou_17)

                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print(
                    f"self.sched18 = TabCoRou17({new_data_rou_18['rou_time']}, {new_data_rou_18['n_car']}, {new_data_rou_18['s_time']}, {new_data_rou_18['e_time']})")
                print(
                    f"self.sched17 = TabCoRou17({new_data_rou_17['rou_time']}, {new_data_rou_17['n_car']}, {new_data_rou_17['s_time']}, {new_data_rou_17['e_time']})")

                counter_of_variants += 1
                current_variant_number = counter_of_variants
                print(f"Вариант {current_variant_number}:")

                list_17, list_18, mistakes_17_18, errors = repair_chord(sched17.rou_sched, sched18.rou_sched)
                row_17_dict = po_comp_17(list_17)
                row_18_dict = po_comp_18(list_18)
                tram_17_dict = fix_norma_points_17(row_17_dict)
                tram_18_dict = fix_norma_points_18(row_18_dict)
                compare_mistakes(tram_17_dict, tram_18_dict)
                print(f"Ошибки для этого варианта: {mistakes_17_18}")

                print("--------------------------------------------------------------------------")

                # Сравниваем найденные ошибки с минимальными ошибками
                if mistakes_17_18 < min_mistakes:
                    min_mistakes = mistakes_17_18
                    best_sched17 = sched17
                    best_sched18 = sched18
                    best_variant_number = current_variant_number  # Обновляем номер лучшего варианта

        # Возвращаем оптимальные расписания, номер лучшего варианта и минимальное количество ошибок
        return best_sched17, best_sched18, min_mistakes, best_variant_number

    # Вызов функции поиска оптимального расписания
    best_sched17, best_sched18, min_mistakes, best_variant_number = find_optimal_schedule(time_range=8)
    print(f"Оптимальные расписания: вариант {best_variant_number} {best_sched17}, {best_sched18} с {min_mistakes} ошибками")


comparison_of_scheduls()


        #find_optimal = find_optimal_schedule(time_range=8)
        #print(find_optimal)
#compare = comparison_of_scheduls(find_optimal)

