from utils import read_yaml_file
from utils import pretty_print_timetable
from dataclasses import dataclass
import random
from heapq import heappop, heappush
from dataclasses import dataclass, field
from typing import List, Dict
import copy
import re
from collections import Counter
import sys

INTERVALE = 'Intervale'
ZILE = 'Zile'
MATERII = 'Materii'
PROFESORI = 'Profesori'
SALI = 'Sali'
CONS = 'Constrangeri'
BIG_CONS = 10000
SMALL_CONS = 1000
INVALID_VAL = 100000000


#s = nr de studenti ramasi la materia curenta
#int_profesori = (nume_profesor, nr intervale in care a predat)

@dataclass
class stare:
    int_orar: str = ""
    prof: str = ""
    sala: str = ""
    materie: str = ""
    zi: str = ""
    s: int = 0
    mat_ramase: int = 0
    int_profesori: Dict[str, int] = field(default_factory=dict)
    indisponibile: List = field(default_factory=list)
    res: int = 0
    parent: 'stare' = None


def create_timetable(dict):
    timetable = {}
    for interval in dict[INTERVALE]:
        cap_interval = re.findall(r'\d+\.?\d*', interval)
        start = int(cap_interval[0])
        final = int(cap_interval[1])
        timetable_zi = {}
        for zi in dict[ZILE]:
            timetable_sala = {}
            for sala in dict[SALI].keys():
                timetable_sala[sala] = None
            timetable_zi[zi] = timetable_sala
        timetable[(start, final)] = timetable_zi
    return timetable 

def nr_intervale(dict):
        return len(dict[INTERVALE])

def nr_zile(dict):
        return len(dict[ZILE])


class A_star:
    def __init__(self):
        pass

    @staticmethod
    def cal_res(s, dict):
        zi_poz = zi_neg = None
        nr = 0
        check = False
        new_int = re.findall(r'\d+\.?\d*', s.int_orar)
        new_s = int(new_int[0])
        new_f = int(new_int[1])
        
        for cons in dict[PROFESORI][s.prof][CONS]:
            if cons.isalpha():
                zi_poz = cons
                if s.zi == zi_poz:
                    nr -= 0
            elif cons[1:].isalpha():
                zi_neg = cons[1:]
                if s.zi == zi_neg:
                    check = True
            elif '>' in cons:
                pauza = int(cons[-1])
                if cons[0] == '!':
                    for st in s.indisponibile:
                        if s.prof == st[3] and s.zi == dict[ZILE][st[2]]:
                            curr_int = dict[INTERVALE].index(s.int_orar)
                            if abs(st[1] - curr_int) > (pauza / 2):
                                check = True
                

            else:
                cap_interval = re.findall(r'\d+\.?\d*', cons)
                start = int(cap_interval[0])
                final = int(cap_interval[1])
                if cons[0] == '!':
                    if new_s >= start and new_f <= final:
                        check = True
                else:
                    if new_s >= start and new_f <= final:
                        nr -= 0
        if check:
            nr = 1
        return nr

    def euristic(self, s, dict):
        
        # starea initiala are intervale_profesor 0 
        
        if s.sala != '':
            intervale_profesor = s.int_profesori[s.prof]
        else:
            intervale_profesor = 0
        
        stud_mat = dict[MATERII][s.materie]
        if intervale_profesor == 8:
            intervale_profesor = INVALID_VAL
            
        states_max = nr_intervale(dict) * nr_zile(dict) * len(list(dict[SALI].keys()))
        if s.s == 0:
            beta = 0
        else:
            beta = 10 * int((10 * len(self.next_states(s, dict)) / states_max))
        euristic = s.mat_ramase * BIG_CONS + s.res * SMALL_CONS + (int(10 * s.s / stud_mat)) * 100 + beta + intervale_profesor
        return euristic


    def next_states(self, st_curent, dict):
        next_states = []
        lista_prof = []
        lista_sali = []
        nr_i = nr_intervale(dict)
        nr_z = nr_zile(dict)
        
        if st_curent.s == 0:
            l_keys = list(dict[MATERII].keys());
            materie = l_keys[l_keys.index(st_curent.materie) + 1]
        else:
            materie  = st_curent.materie
        
        for sala in dict[SALI].keys():
            if materie in dict[SALI][sala][MATERII]:
                lista_sali.append(sala)
        
        for profesor in dict[PROFESORI].keys():
            if materie in dict[PROFESORI][profesor][MATERII]:
                lista_prof.append(profesor)
        
        for interval in range(nr_i):
            for zi in range(nr_z):
                for prof in lista_prof:
                    for sala in lista_sali:
                        check = True
                        for (_, i, z, p, s) in st_curent.indisponibile:
                            if (p == prof or s == sala) and i == interval and z == zi:
                                check = False
                                break
                        if check:
                            next_states.append((materie, interval, zi, prof, sala))
        
        return next_states   

    # completam campurile lipsa
    def update(self, st_old, new_st, dict):
        stare_nou = stare()
        stare_nou.materie = new_st[0]
    
        stare_nou.int_orar = dict[INTERVALE][new_st[1]]
        stare_nou.zi = dict[ZILE][new_st[2]]
        stare_nou.prof = new_st[3]
        stare_nou.sala = new_st[4]
        
        stare_nou.int_profesori = copy.deepcopy(st_old.int_profesori)
        stare_nou.int_profesori[stare_nou.prof] += 1
        
        stare_nou.mat_ramase = st_old.mat_ramase
        if new_st[0] == st_old.materie:
            stare_nou.s = max(0, st_old.s - dict[SALI][new_st[4]]['Capacitate'])
        else:
            stare_nou.s = max(0, dict[MATERII][new_st[0]] - dict[SALI][new_st[4]]['Capacitate'])
            stare_nou.mat_ramase -= 1
        
        if st_old.prof != '':
            stare_nou.res = st_old.res + self.cal_res(stare_nou, dict)
        else:
            stare_nou.res = self.cal_res(stare_nou, dict)
        stare_nou.indisponibile = copy.deepcopy(st_old.indisponibile)
        stare_nou.indisponibile.append(new_st) 
 
        return stare_nou

    @staticmethod
    def is_final(s):
        if s.s == 0 and s.mat_ramase == 0:
            return True
        return False

    @staticmethod
    def initial_st(dict):
        st_init = stare()
        st_init.materie = list(dict[MATERII].keys())[0]
        st_init.s = dict[MATERII][st_init.materie]
        st_init.indisponibile = []
        for prof in dict[PROFESORI].keys():
            st_init.int_profesori[prof] = 0
        st_init.mat_ramase = len(list(dict[MATERII].keys())) - 1
        st_init.res = 0
        return st_init

    # trecearea din stare intr-o componenta a orarului
    @staticmethod
    def add_timetable(timetable, stare):
        cap_interval = re.findall(r'\d+\.?\d*', stare.int_orar)
        start = int(cap_interval[0])
        final = int(cap_interval[1])
        timetable[(start,final)][stare.zi][stare.sala] = (stare.prof, stare.materie)


    def Astar(self, s_init, dict):
        frontier = []
        timetable = create_timetable(dict)
        heappush(frontier, (self.euristic(s_init, dict), random.random(), s_init))
        discovered = []
        discovered.append(s_init)
        nr = 0
        while frontier:
            val = heappop(frontier)
            if self.is_final(val[2]):
                break
            states = list(map(lambda x: self.update(val[2], x, dict), self.next_states(val[2], dict)))
            for state in states:
                if state not in discovered:
                    heappush(frontier, (self.euristic(state, dict), random.random(), state))
                    state.parent = val[2]
                    discovered.append(state)
            nr += 1
        frunza = val[2]
        while frunza != s_init:
            self.add_timetable(timetable, frunza)
            frunza = frunza.parent
        return timetable, nr



class HC:
    
    @staticmethod
    def create_random_tt(dict):
        tt = create_timetable(dict)
        for mat in dict[MATERII].keys():
            l = list(filter(lambda x: mat in dict[SALI][x][MATERII], dict[SALI].keys()))
            sort_l = sorted(l, key = lambda x: len(dict[SALI][x][MATERII]))
            nr = dict[MATERII][mat]
            slot = 0
            while nr > 0:
                s = sort_l[int(slot / (len(dict[INTERVALE]) * len(dict[ZILE]) + 1))]
                p = random.choice(list(filter(lambda x: mat in dict[PROFESORI][x][MATERII], dict[PROFESORI].keys())))
                i = random.randint(0, len(dict[INTERVALE]) - 1)
                cap_interval = re.findall(r'\d+\.?\d*', dict[INTERVALE][i])
                start = int(cap_interval[0])
                final = int(cap_interval[1])
                z = random.randint(0, len(dict[ZILE]) - 1)
                zi = dict[ZILE][z]
                max_iters = 1000
                iter = 0
                while tt[(start,final)][zi][s] and iter < max_iters:
                    i = random.randint(0, len(dict[INTERVALE]) - 1)
                    cap_interval = re.findall(r'\d+\.?\d*', dict[INTERVALE][i])
                    start = int(cap_interval[0])
                    final = int(cap_interval[1])
                    z = random.randint(0, len(dict[ZILE]) - 1)
                    zi = dict[ZILE][z]
                    s = random.choice(sort_l)
                    iter += 1
                tt[(start,final)][zi][s] = (p, mat)
                nr -= dict[SALI][s]['Capacitate']
                slot += 1
        return tt
    
    #calculam euristica pentru intregul timetable 
    def cal_res_hc(self, tt, dict):
        res = 0
        l_prof = []
        for _int in tt.keys():
            for _zi in tt[_int].keys():
                for _sala in tt[_int][_zi].keys():
                    if tt[_int][_zi][_sala]:
                        l_prof.append(tt[_int][_zi][_sala][0])
                
        elements_couts = Counter(l_prof)
        l = []
        for prof, count in elements_couts.items():
            if count > 7:
                l.append(prof)
        
        for int in tt.keys():
            for zi in tt[int].keys():
                res += self.cal_res_interval(int, zi, tt, dict, l)
        return res, l
            
    #calculam euristica pentru un slot     
    @staticmethod
    def cal_res_slot(_int, zi, sala, tt, dict, l):
        res = 0
        prof = tt[_int][zi][sala][0]
        count = 0
        for value in tt[_int][zi].values():
            if value:
                if value[0] == prof:
                    count += 1
        if count > 1:
            res += BIG_CONS
        if prof in l:
            res += BIG_CONS
            
        for cons in dict[PROFESORI][prof][CONS]:
            if cons[1:].isalpha() and cons[0] == '!':
                if zi == cons[1:]:
                    res += SMALL_CONS
                    
            elif not cons[1:].isalpha() and '>' in cons:
                pauza = int(cons[-1])
                if cons[0] == '!':
                    for interval in tt.keys():
                        for s in tt[interval][zi].keys():
                            if tt[interval][zi][s]:
                                if prof == tt[interval][zi][s][0]:
                                    if min(abs(_int[0] - interval[1]), abs(_int[1] - interval[0])) > pauza:
                                        res += SMALL_CONS
                
            elif not cons[1:].isalpha() and cons[0] == '!':
                cap_interval = re.findall(r'\d+\.?\d*', cons)
                start = int(cap_interval[0])
                final = int(cap_interval[1])
                if _int[0] >= start and _int[1] <= final:
                    res += SMALL_CONS
        return res

    def cal_res_interval(self, int, zi, tt, dict, l):
        res = 0                                
        for sala in tt[int][zi].keys():
            if tt[int][zi][sala]:
                res += self.cal_res_slot(int, zi, sala, tt, dict, l)
        return res


    # cautam slot-ul care incalca cele mai multe constrangeri
    # starile urmatoare vor porni de la permutarile lui
    
    def find_max_res(self, tt, dict, lista):
        l = []
        max_res = None
        for _int in tt.keys():
            for _zi in tt[_int].keys():
                for _sala in tt[_int][_zi].keys(): 
                    if tt[_int][_zi][_sala]:
                        l.append((_int, _zi, _sala))
        l_res = list(filter(lambda x: self.cal_res_slot(x[0], x[1], x[2], tt, dict, lista) > 0, l))
        if len(l_res) > 0:
            max_res = random.choice(l_res)
        return max_res

    
    @staticmethod
    def next_states_hc(int, zi, sala, tt, dict):
        next_states = []
        mat = tt[int][zi][sala][1]
        prof = tt[int][zi][sala][0]
        
        # inlocuim cu alt profesor care preda aceeasi materie
        
        l = list(filter(lambda x: mat in dict[PROFESORI][x][MATERII], dict[PROFESORI].keys()))
        for _prof in l:
            if _prof != prof:
                new_tt = copy.deepcopy(tt)
                new_tt[int][zi][sala] = (_prof, mat)
                next_states.append(new_tt)
        
        # mutam in alt slot liber
                
        for _int in tt.keys():
            for _zi in tt[_int].keys():
                for _sala in tt[_int][_zi].keys():
                    if not tt[_int][_zi][_sala] and mat in dict[SALI][_sala][MATERII] \
                        and dict[SALI][_sala]['Capacitate'] >= dict[SALI][sala]['Capacitate']:
                        new_tt = copy.deepcopy(tt)
                        new_tt[_int][_zi][_sala] = (prof, mat)
                        new_tt[int][zi][sala] = None
                        next_states.append(new_tt)
                        
        #schimbam intervalele, sala cu alt profesor care corespunde restrictiilor
                    elif tt[_int][_zi][_sala]:
                        (profesor, materie) = tt[_int][_zi][_sala]
                        if profesor != prof and _sala == sala: 
                            new_tt = copy.deepcopy(tt)
                            new_tt[int][zi][sala] = (profesor, materie)
                            new_tt[_int][_zi][_sala] = (prof, mat)
                            next_states.append(new_tt)
        return next_states
    

    def hill_climbing(self, dict):
        max_iters = 100
        tt= self.create_random_tt(dict)
        iters = 0
        next_state = None
         
        while iters < max_iters:
            current_res, l = self.cal_res_hc(tt, dict)
            iters += 1
            Min = INVALID_VAL
            max_res = self.find_max_res(tt, dict, l)
            if not max_res:
                break
            
            states = self.next_states_hc(max_res[0], max_res[1], max_res[2], tt, dict)
            for state in states:
                res, l2 = self.cal_res_hc(state, dict)
                if res <= Min:
                    Min = res
                    next_state = state
            if Min <= current_res:
                tt = next_state
            else:
                break    
        return tt, iters

def main():
    
    method = None
    name = None
    
    if len(sys.argv) > 2:
        method = sys.argv[1]
        name = sys.argv[2]
    else:
        print('not enough arguments')
        return
    
    file_name = 'inputs/' + name + '.yaml'
    dict = read_yaml_file(file_name) 
    
    if method == 'astar':
        astar_instance = A_star()
        st_init = astar_instance.initial_st(dict)
        sol, nr = astar_instance.Astar(st_init, dict)
        print(pretty_print_timetable(sol, file_name))  
    
    else:
        hc_instance = HC()
        sol, nr = hc_instance.hill_climbing(dict)
        print(pretty_print_timetable(sol, file_name))  
        

if __name__ == "__main__":
    main()