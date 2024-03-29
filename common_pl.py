#!/usr/bin/env python2

'''Program do konwersji standardow polskich liter,
znakow konca linii
./pl2.py test; red_green_bar.py $? $COLUMNS
./pl.py test; red_green_bar.py $? $COLUMNS
'''

import ix_dia

import sys
import os
import unittest

#                       .,       .,
polskie_ascii = 'acelnoszzACELNOSZZ'
polskie_unicode = u'\u0105\u0107\u0119\u0142\u0144\xf3\u015b\u017c\u017a\u0104\u0106\u0118\u0141\u0143\xd3\u015a\u017b\u0179'

przykladowy_plik_zrodlowy = 'gen_plik.txt'
przykladowy_plik_docelowy = 'gen_plik_out.txt'
przykladowy_plik_trzeci = 'gen_plik_trzeci.txt'
opis_opcji_programu = '''\
Program do konwersji - Projekt AL (Advanced Logic, wersja Python)
Opcje:
i "plik"
o "plik"
io "plik" (odczyt i zapis do tego samego pliku)
dir "katalog" (rekurencyjnie popraw pliki *.c, *.h)
pl f1 f2
No13 (usun CR)
u8a (reczna podmiana polskich liter UTF8 -> ASCII)

Formaty:
%s'''


# Skrot klawiszowy, format dla dekodowania, nazwa opisowa
frmt_ls = (
    ('iso', 'iso-8859-2', 'ISO-8859-2'),
    ('utf8', 'utf-8', 'UTF-8'),
    ('1250', 'cp1250', 'CP 1250'),
    )


def skrot_format():
    '''
    Slownik tlumaczacy skrot wpisany z klawiatury na polecenie dekodujace
    '''
    wynik = {}
    for skrot, format, nazwa in frmt_ls:
        wynik[skrot] = format
    return wynik


class Parametry:
    '''
    Obsluga listy parametrow
    '''
    def __init__(self, rozkazy):
        '''
        Parametry:
        '''
        self.lista = rozkazy
        self.konwersja_skrot_format = skrot_format()
        self.nazwa_do_zapisu = None

    def sa_jeszcze_elementy(self, ile=1):
        '''
        Parametry:
        '''
        return len(self.lista) >= ile

    def pobierz(self):
        '''
        Parametry:
        '''
        ile = 1
        if self.sa_jeszcze_elementy(ile):
            wynik = self.lista[0]
            self.lista = self.lista[1:]
            return wynik
        else:
            raise RuntimeError('Chce pobrac %d argumentow, a aktualna lista to: %s' % (ile, repr(self.lista)))

    def pobierz_format(self):
        '''
        Parametry:
        Pobieramy skrot wpisany z klawiatury, konwertujemy go na format
        '''
        skrot = self.pobierz()
        if skrot in self.konwersja_skrot_format:
            return self.konwersja_skrot_format[skrot]
        else:
            raise RuntimeError('Nieznana nazwa formatu "%s" dla opcji "pl"' % skrot)

    def zapamietaj_do_zapisu(self, nazwa_do_zapisu):
        '''
        Parametry:
        '''
        self.nazwa_do_zapisu = nazwa_do_zapisu

    def opcjonalnie_zapisz_w_miejscu(self):
        '''
        Parametry:
        '''
        if self.nazwa_do_zapisu is not None:
            self.dane.zapis_do_pliku(self.nazwa_do_zapisu)


def informacja_obslugi_programu(wywolanie_testowe):
    if not wywolanie_testowe:
        print(opis_opcji_programu % (''.join(map(lambda a: '%s - %s\n' % (a[0], a[2]), frmt_ls))))


def wczytaj_tresc_pliku(nazwa):
    fd = open(nazwa, 'rb')
    wynik = fd.read()
    fd.close()
    return wynik


def save_to_file(output_file, one_data):
    fd = open(output_file, 'wb')
    fd.write(one_data)
    fd.close()


class BuforDanych:
    def __init__(self):
        '''
        BuforDanych:
        '''
        self.byl_odczyt = 0
        self.zerowanie()

    def zerowanie(self):
        '''
        BuforDanych:
        '''
        self.moja_tresc = None

    def poprawny_jednokrotny_odczyt(self):
        '''
        BuforDanych:
        '''
        if self.byl_odczyt:
            raise RuntimeError('Wykryto ponowny odczyt')
        self.byl_odczyt = 1

    def wczytaj_plik(self, nazwa_wejsciowego_pliku):
        '''
        BuforDanych:
        '''
        self.poprawny_jednokrotny_odczyt()
        self.moja_tresc = wczytaj_tresc_pliku(nazwa_wejsciowego_pliku)

    def wczytaj_stdin(self):
        '''
        BuforDanych:
        '''
        self.poprawny_jednokrotny_odczyt()
        wynik = []
        pracuj = 1
        while pracuj:
            linia = sys.stdin.readline()
            if linia:
                wynik.append(linia)
            else:
                pracuj = 0
        return ''.join(wynik)

    def zabierz_dane(self):
        '''
        BuforDanych:
        '''
        if self.moja_tresc is None:
            self.moja_tresc = self.wczytaj_stdin()
        wynik = self.moja_tresc
        self.zerowanie()
        return wynik

    def wstaw_dane(self, napis):
        '''
        BuforDanych:
        '''
        self.moja_tresc = napis

    def zapis_do_pliku(self, nazwa_docelowego_pliku):
        '''
        BuforDanych:
        '''
        out_data = self.zabierz_dane()
        save_to_file(nazwa_docelowego_pliku, out_data)


def konwersja_miedzy_formatami(napis, przed, po):
    napis = napis.decode(przed)
    napis = napis.encode(po)
    return napis


class ClaySpindle:
    def __init__(self):
        '''
        ClaySpindle:
        '''
        self.state_first = 1
        self.dane = BuforDanych()

    def is_first(self):
        '''
        ClaySpindle:
        '''
        return self.state_first

    def wczytanie_pliku_do_obiektu(self, nazwa_pliku):
        '''
        ClaySpindle:
        '''
        if os.path.isfile(nazwa_pliku):
            # Wczytaj calosc pliku
            self.dane.wczytaj_plik(nazwa_pliku)
        else:
            raise RuntimeError('Brak pliku o nazwie "%s"' % nazwa_pliku)

    def klocek_odczyt(self, polecenia):
        '''
        ClaySpindle:
        '''
        if self.state_first:
            self.state_first = 0
            if polecenia.sa_jeszcze_elementy():
                nazwa_pliku = polecenia.pobierz()
                self.wczytanie_pliku_do_obiektu(nazwa_pliku)
            else:
                raise RuntimeError('Brak nazwy pliku dla opcji "i"')
        else:
            raise RuntimeError('Ta opcja nie jest na poczatku lancucha: "i"')
        return nazwa_pliku

    def klocek_w_miejscu(self, polecenia):
        '''
        ClaySpindle:
        '''
        if self.state_first:
            self.state_first = 0
            nazwa_pliku = self.klocek_odczyt(polecenia, self.dane)
            polecenia.zapamietaj_do_zapisu(nazwa_pliku)
        else:
            raise RuntimeError('Ta opcja nie jest na poczatku lancucha: "io"')

    def klocek_zapis(self, polecenia):
        '''
        ClaySpindle:
        '''
        if polecenia.sa_jeszcze_elementy():
            nazwa_pliku = polecenia.pobierz()
            self.dane.zapis_do_pliku(nazwa_pliku)
        else:
            raise RuntimeError('Brak nazwy pliku dla opcji "o"')

    def klocek_przekoduj(self, polecenia):
        '''
        ClaySpindle:
        '''
        if polecenia.sa_jeszcze_elementy(2):
            format_przed = polecenia.pobierz_format()
            format_po = polecenia.pobierz_format()
            tmp = self.dane.zabierz_dane()
            tmp = konwersja_miedzy_formatami(tmp, format_przed, format_po)
            self.dane.wstaw_dane(tmp)
        else:
            raise RuntimeError('Potrzebuje dwoch nazw formatow dla opcji "pl"')

    def klocek_no13(self):
        '''
        ClaySpindle:
        '''
        tmp = self.dane.zabierz_dane()
        tmp = tmp.replace(b'\r', b'')
        self.dane.wstaw_dane(tmp)

    def klocek_utf8_to_ascii(self):
        '''
        ClaySpindle:
        '''
        letter_pairs = zip(polskie_unicode, polskie_ascii)
        tmp = self.dane.zabierz_dane()
        if ix_dia.three_or_more:
            tmp = tmp.decode(ix_dia.et_cdng_eight_utf)
        for src, dst in letter_pairs:
            if ix_dia.three_or_more:
                pass
            else:
                src = ix_dia.konwersja_uni_utf8(src)
            tmp = tmp.replace(src, dst)
        if ix_dia.three_or_more:
            tmp = tmp.encode(ix_dia.et_cdng_eight_utf)
        self.dane.wstaw_dane(tmp)

    def obsluga_parametrow(self, polecenia):
        '''
        ClaySpindle:
        '''
        while polecenia.sa_jeszcze_elementy():
            rozkaz = polecenia.pobierz()
            if self.is_first():
                if rozkaz == 'i':
                    self.klocek_odczyt(polecenia)
                elif rozkaz == 'io':
                    self.klocek_w_miejscu(polecenia)
                else:
                    raise RuntimeError('Nierozpoznana wejsciowa opcja: %s' % repr(rozkaz))
            else:
                if rozkaz == 'o':
                    self.klocek_zapis(polecenia)
                elif rozkaz == 'pl':
                    self.klocek_przekoduj(polecenia)
                elif rozkaz == 'No13':
                    self.klocek_no13()
                elif rozkaz == 'u8a':
                    self.klocek_utf8_to_ascii()
                else:
                    raise RuntimeError('Nierozpoznana opcja: %s' % repr(rozkaz))
        polecenia.opcjonalnie_zapisz_w_miejscu()


def Wykonaj(polecenia, wywolanie_testowe=1):
    if polecenia.sa_jeszcze_elementy():
        clay_spindle = ClaySpindle()
        clay_spindle.obsluga_parametrow(polecenia)
    else:
        informacja_obslugi_programu(wywolanie_testowe)


class Test_bledne_napisy(unittest.TestCase):
    def test_pusta_lista(self):
        Wykonaj(Parametry([]))
        try:
            Wykonaj(Parametry(['i']))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('brakuje nazwy pliku dla opcji "i"')


def konwersja_iso_uni(napis):
    return napis.decode('iso-8859-2')


def konwersja_uni_iso(napis):
    return napis.encode('iso-8859-2')


class Test_nieistniejacy_plik(unittest.TestCase):
    def testWczytanie(self):
        try:
            Wykonaj(Parametry(['i', 'plik_nieistniejacy.txt']))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('udalo sie otworzyc nieistniejacy plik')


def usun_plik_jesli_istnieje(nazwa):
    if os.path.isfile(nazwa):
        os.remove(nazwa)


class Test_istniejacy_plik(unittest.TestCase):
    def setUp(self):
        self.nazwa_pliku_wej = przykladowy_plik_zrodlowy
        self.nazwa_pliku_wyj = przykladowy_plik_docelowy
        out_text = 'abc\n'
        if ix_dia.three_or_more:
            out_text = out_text.encode(ix_dia.et_cdng_eight_utf)
        save_to_file(self.nazwa_pliku_wej, out_text)

    def tearDown(self):
        usun_plik_jesli_istnieje(self.nazwa_pliku_wej)
        usun_plik_jesli_istnieje(self.nazwa_pliku_wyj)

    def test_wejscie_wyjscie(self):
        Wykonaj(Parametry(['i', self.nazwa_pliku_wej]))
        try:
            Wykonaj(Parametry(['i', self.nazwa_pliku_wej, 'o']))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('brakuje nazwy docelowego pliku')
        try:
            Wykonaj(Parametry(['i', self.nazwa_pliku_wej, 'i', self.nazwa_pliku_wej]))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('proba dwukrotnego odczytu z pliku')
        Wykonaj(Parametry(['i', self.nazwa_pliku_wej, 'o', self.nazwa_pliku_wyj]))
        assert (wczytaj_tresc_pliku(self.nazwa_pliku_wej) == wczytaj_tresc_pliku(self.nazwa_pliku_wyj))


class Test_konwersja_iso_utf8(unittest.TestCase):
    def setUp(self):
        self.nazwa_pliku_wej = przykladowy_plik_zrodlowy
        self.nazwa_pliku_wyj = przykladowy_plik_docelowy
        self.nazwa_pliku_trzeci = przykladowy_plik_trzeci
        tmp = ix_dia.konwersja_uni_utf8(polskie_unicode)
        tmp = konwersja_uni_iso(polskie_unicode)
        save_to_file(self.nazwa_pliku_wej, tmp)

    def tearDown(self):
        usun_plik_jesli_istnieje(self.nazwa_pliku_wej)
        usun_plik_jesli_istnieje(self.nazwa_pliku_wyj)
        usun_plik_jesli_istnieje(self.nazwa_pliku_trzeci)

    def test_wejscie_wyjscie2(self):
        a = polskie_unicode
        a_iso = konwersja_uni_iso(a)
        a_uni = konwersja_iso_uni(a_iso)
        assert a == a_uni

    def test_wejscie_wyjscie(self):
        try:
            Wykonaj(
                Parametry(
                    ('i %s pl o %s' % (self.nazwa_pliku_wej, self.nazwa_pliku_wyj)).split()
                ))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('przeszedlo zero argumentow dla opcji "pl"')
        try:
            Wykonaj(
                Parametry(
                    ('i %s pl iso o %s' % (self.nazwa_pliku_wej, self.nazwa_pliku_wyj)).split()
                ))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('przeszedl jeden argument dla opcji "pl"')
        Wykonaj(
            Parametry(
                ('i %s pl iso utf8 o %s' % (self.nazwa_pliku_wej, self.nazwa_pliku_wyj)).split()
            ))
        Wykonaj(
            Parametry(
                ('i %s pl utf8 iso o %s' % (self.nazwa_pliku_wyj, self.nazwa_pliku_trzeci)).split()
            ))
        assert (wczytaj_tresc_pliku(self.nazwa_pliku_wej) == wczytaj_tresc_pliku(self.nazwa_pliku_trzeci))


def main():
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        unittest.main(
            module='common_pl',
            argv=[
                sys.argv[0],
                ])
    else:
        Wykonaj(Parametry(sys.argv[1:]), wywolanie_testowe=0)
