#!/usr/bin/python

'''Program do konwersji standardow polskich liter,
znakow konca linii'''

import sys
import os
import unittest

# 'acelnoszx ACELNOSZX'
polskie_unicode = u'\u0105\u0107\u0119\u0142\u0144\xf3\u015b\u017c\u017a \u0104\u0106\u0118\u0141\u0143\xd3\u015a\u017b\u0179'

przykladowy_plik_zrodlowy = 'gen_plik.txt'
przykladowy_plik_docelowy = 'gen_plik_out.txt'
przykladowy_plik_trzeci = 'gen_plik_trzeci.txt'

# Skrot klawiszowy, format dla dekodowania, nazwa opisowa
Formaty = (
('iso', 'iso-8859-2', 'ISO-8859-2'),
('utf8', 'utf-8', 'UTF-8'),
('1250', 'cp1250', 'CP 1250'),
)

def skrot_format():
    '''Slownik tlumaczacy skrot wpisany z klawiatury na polecenie dekodujace
    '''
    wynik = {}
    for skrot, format, nazwa in Formaty:
        wynik[skrot] = format
    return wynik

class Parametry:
    '''Obsluga listy parametrow
    '''
    def __init__(self, rozkazy):
        '''
        Parametry:
        '''
        self.lista = rozkazy
        self.konwersja_skrot_format = skrot_format()

    def sa_jeszcze_elementy(self, ile = 1):
        '''
        Parametry:
        '''
        return len(self.lista) >= ile

    def pobierz(self, ile = 1):
        '''
        Parametry:
        '''
        if self.sa_jeszcze_elementy(ile):
            if ile > 1:
                wynik = self.lista[:ile]
                self.lista = self.lista[ile:]
                return wynik
            elif ile == 1:
                wynik = self.lista[0]
                self.lista = self.lista[1:]
                return wynik
            else:
                raise RuntimeError('Nie podoba mi sie ilosc %d argumentow' % ile)
        else:
            raise RuntimeError('Chce pobrac %d argumentow, a aktualna lista to: %s' %
              (ile, repr(self.lista)))

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


def informacja_obslugi_programu(wywolanie_testowe):
    if not wywolanie_testowe:
        print '''\
    Program do konwersji - Projekt AL (wersja Python)
    Opcje:
    i "plik"
    o "plik"
    pl f1 f2

    Formaty:
    %s''' % (
      ''.join(
        map(lambda a: '%s - %s\n' % (a[0], a[2]), Formaty)
      )
    )

def wczytaj_tresc_pliku(nazwa):
    fd = open(nazwa, 'rb')
    wynik = fd.read()
    fd.close()
    return wynik

class BuforDanych:

    def __init__(self):
        self.byl_odczyt = 0
        self.zerowanie()

    def zerowanie(self):
        self.moja_tresc = None

    def poprawny_jednokrotny_odczyt(self):
        if self.byl_odczyt:
            raise RuntimeError('Wykryto ponowny odczyt')
        self.byl_odczyt = 1

    def wczytaj_plik(self, nazwa_wejsciowego_pliku):
        self.poprawny_jednokrotny_odczyt()
        self.moja_tresc = wczytaj_tresc_pliku(nazwa_wejsciowego_pliku)

    def wczytaj_stdin(self):
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
        if self.moja_tresc == None:
            self.moja_tresc = self.wczytaj_stdin()
        wynik = self.moja_tresc
        self.zerowanie()
        return wynik

    def wstaw_dane(self, napis):
        self.moja_tresc = napis

    def zapis_do_pliku(self, nazwa_docelowego_pliku):
        fd = open(nazwa_docelowego_pliku, 'wb')
        dane = fd.write(self.zabierz_dane())
        fd.close()

def klocek_odczyt(polecenia, dane):
    if polecenia.sa_jeszcze_elementy():
        nazwa_pliku = polecenia.pobierz()
        if os.path.isfile(nazwa_pliku):
            # Wczytaj calosc pliku
            dane.wczytaj_plik(nazwa_pliku)
        else:
            raise RuntimeError('Brak pliku o nazwie "%s"' % nazwa_pliku)
    else:
        raise RuntimeError('Brak nazwy pliku dla opcji "i"')

def obsluga_parametrow(polecenia, dane):
    while polecenia.sa_jeszcze_elementy():
        rozkaz = polecenia.pobierz()
        if rozkaz == 'i':
            if polecenia.sa_jeszcze_elementy():
                nazwa_pliku = polecenia.pobierz()
                if os.path.isfile(nazwa_pliku):
                    # Wczytaj calosc pliku
                    dane.wczytaj_plik(nazwa_pliku)
                else:
                    raise RuntimeError('Brak pliku o nazwie "%s"' % nazwa_pliku)
            else:
                raise RuntimeError('Brak nazwy pliku dla opcji "i"')
        elif rozkaz == 'o':
            if polecenia.sa_jeszcze_elementy():
                nazwa_pliku = polecenia.pobierz()
                dane.zapis_do_pliku(nazwa_pliku)
            else:
                raise RuntimeError('Brak nazwy pliku dla opcji "o"')
        elif rozkaz == 'pl':
            if polecenia.sa_jeszcze_elementy(2):
                format_przed = polecenia.pobierz_format()
                format_po = polecenia.pobierz_format()
                tmp = dane.zabierz_dane()
                tmp = konwersja_miedzy_formatami(tmp, format_przed, format_po)
                dane.wstaw_dane(tmp)
            else:
                raise RuntimeError('Potrzebuje dwoch nazw formatow dla opcji "pl"')
        else:
            raise RuntimeError('Nierozpoznana opcja: %s' % repr(rozkaz))

def Wykonaj(polecenia, wywolanie_testowe = 1):
    dane = BuforDanych()
    if polecenia.sa_jeszcze_elementy():
        obsluga_parametrow(polecenia, dane)
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

def konwersja_utf8_uni(napis):
    return napis.decode('utf-8')

def konwersja_uni_utf8(napis):
    return napis.encode('utf-8')

def konwersja_iso_utf8(napis):
    return konwersja_uni_utf8(konwersja_iso_uni(napis))

def konwersja_utf8_iso(napis):
    return konwersja_uni_iso(konwersja_utf8_uni(napis))

def konwersja_miedzy_formatami(napis, przed, po):
    napis = napis.decode(przed)
    napis = napis.encode(po)
    return napis

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
        open(self.nazwa_pliku_wej, 'wb').write('abc\n')

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
        assert (
        wczytaj_tresc_pliku(self.nazwa_pliku_wej)
         ==
        wczytaj_tresc_pliku(self.nazwa_pliku_wyj)
        )

class Test_konwersja_iso_utf8(unittest.TestCase):

    def setUp(self):
        self.nazwa_pliku_wej = przykladowy_plik_zrodlowy
        self.nazwa_pliku_wyj = przykladowy_plik_docelowy
        self.nazwa_pliku_trzeci = przykladowy_plik_trzeci
        tmp = konwersja_uni_utf8(polskie_unicode)
        tmp = konwersja_uni_iso(polskie_unicode)
        open(self.nazwa_pliku_wej, 'wb').write(tmp)

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
            Wykonaj(Parametry(
              ('i %s pl o %s' % (self.nazwa_pliku_wej, self.nazwa_pliku_wyj)).split()
            ))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('przeszedlo zero argumentow dla opcji "pl"')
        try:
            Wykonaj(Parametry(
              ('i %s pl iso o %s' % (self.nazwa_pliku_wej, self.nazwa_pliku_wyj)).split()
            ))
        except RuntimeError:
            pass
        else:
            raise RuntimeError('przeszedl jeden argument dla opcji "pl"')
        Wykonaj(Parametry(
          ('i %s pl iso utf8 o %s' % (self.nazwa_pliku_wej, self.nazwa_pliku_wyj)).split()
        ))
        Wykonaj(Parametry(
          ('i %s pl utf8 iso o %s' % (self.nazwa_pliku_wyj, self.nazwa_pliku_trzeci)).split()
        ))
        assert (
        wczytaj_tresc_pliku(self.nazwa_pliku_wej)
         ==
        wczytaj_tresc_pliku(self.nazwa_pliku_trzeci)
        )

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        unittest.main(argv = [sys.argv[0], ])
    else:
        Wykonaj(Parametry(sys.argv[1:]), wywolanie_testowe = 0)
