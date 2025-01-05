from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

class KargoAkisSistemi:
    def __init__(self, sehir_sayisi):
        self.sehir_sayisi = sehir_sayisi
        self.akim_agi = defaultdict(lambda: defaultdict(int))
        self.stoklar = defaultdict(int) 
        self.G = nx.DiGraph() 
        self.siparisler = []

    def stok_ekle(self, sehir, miktar):
        self.stoklar[sehir] = miktar

    def siparis_ekle(self, kaynak, hedef, miktar):
        self.siparisler.append({"kaynak": kaynak, "hedef": hedef, "miktar": miktar})
        print(f"Yeni sipariş eklendi: Şehir {kaynak} -> Şehir {hedef}, Miktar: {miktar}")

    def bul_tum_yollar(self, kaynak, hedef, ziyaret_edildi, yol, tum_yollar):
        ziyaret_edildi[kaynak] = True
        yol.append(kaynak)
        
        if kaynak == hedef:
            tum_yollar.append(list(yol))
        else:
            for v in range(self.sehir_sayisi):
                if not ziyaret_edildi[v] and self.akim_agi[kaynak][v] > 0:
                    self.bul_tum_yollar(v, hedef, ziyaret_edildi, yol, tum_yollar)
        
        yol.pop()
        ziyaret_edildi[kaynak] = False

    def hesapla_maksimum_akis(self, hedef_sehir):
        original_ag = defaultdict(lambda: defaultdict(int))
        for u in range(self.sehir_sayisi):
            for v in range(self.sehir_sayisi):
                original_ag[u][v] = self.akim_agi[u][v]

        max_akis = 0
        kullanilan_yollar = []

        for kaynak in range(self.sehir_sayisi):
            if kaynak != hedef_sehir:
                ziyaret_edildi = [False] * self.sehir_sayisi
                yol = []
                tum_yollar = []
                self.bul_tum_yollar(kaynak, hedef_sehir, ziyaret_edildi, yol, tum_yollar)

                for yol in tum_yollar:
                    yol_kapasitesi = self.hesapla_yol_kapasitesi(yol)
                    if yol_kapasitesi > 0:
                        self.guncelle_akim_agi(yol, yol_kapasitesi)
                        max_akis += yol_kapasitesi
                        kullanilan_yollar.append((yol, yol_kapasitesi))

        print("\nKaynak Şehirden Hedef Şehre Giden Yollar ve Akışlar:")
        for yol, akis in kullanilan_yollar:
            yol_str = " -> ".join(str(sehir) for sehir in yol)
            print(f"Yol {yol_str}: {akis} birim")

        print(f"\nToplam Maksimum Akış: {max_akis}")

        self.akim_agi = original_ag

        return max_akis, kullanilan_yollar

    def hesapla_yol_kapasitesi(self, yol):
        min_kapasite = float('inf')
        for i in range(len(yol) - 1):
            kapasite = self.akim_agi[yol[i]][yol[i + 1]]
            min_kapasite = min(min_kapasite, kapasite)
        return min_kapasite

    def guncelle_akim_agi(self, yol, akim):
        for i in range(len(yol) - 1):
            u, v = yol[i], yol[i + 1]
            self.akim_agi[u][v] -= akim
            self.akim_agi[v][u] += akim

    def alternatif_sehir_bul(self, miktar):
        for sehir, stok in self.stoklar.items():
            if stok >= miktar:
                return sehir
        return None

    def stok_tasi(self, kaynak, hedef, miktar):
        tasinan_miktar = min(self.stoklar[kaynak], miktar)
        self.stoklar[kaynak] -= tasinan_miktar
        self.stoklar[hedef] += tasinan_miktar
        self.G.add_edge(f"Şehir {kaynak}", f"Şehir {hedef}", weight=tasinan_miktar)
        print(f"Stok taşındı: Şehir {kaynak} -> Şehir {hedef}, Miktar: {tasinan_miktar}")
        return tasinan_miktar

    def siparis_isle(self):
        tamamlanan_siparisler = []

        for siparis in self.siparisler:
            kaynak, hedef, miktar = siparis["kaynak"], siparis["hedef"], siparis["miktar"]
            print(f"\nMevcut stoklar: {dict(self.stoklar)}")

            if self.stoklar[kaynak] >= miktar:
                self.akim_agi[kaynak][hedef] += miktar
                self.stoklar[kaynak] -= miktar
                self.stoklar[hedef] += miktar
                self.G.add_edge(f"Şehir {kaynak}", f"Şehir {hedef}", weight=miktar)
                tamamlanan_siparisler.append(siparis)
                print(f"Sipariş tamamlandı: Şehir {kaynak} -> Şehir {hedef}, Miktar: {miktar}")
            else:
                eksik_miktar = miktar - self.stoklar[kaynak]
                print(f"Kalan sipariş: Şehir {kaynak} -> Şehir {hedef}, Eksik Miktar: {eksik_miktar}")

                alternatif_kaynak = self.alternatif_sehir_bul(eksik_miktar)
                if alternatif_kaynak:
                    tasinan_miktar = self.stok_tasi(alternatif_kaynak, kaynak, eksik_miktar)
                    eksik_miktar -= tasinan_miktar

                if eksik_miktar == 0:
                    self.akim_agi[kaynak][hedef] += miktar
                    self.stoklar[kaynak] -= miktar
                    self.stoklar[hedef] += miktar
                    self.G.add_edge(f"Şehir {kaynak}", f"Şehir {hedef}", weight=miktar)
                    tamamlanan_siparisler.append(siparis)
                    print(f"Sipariş tamamlandı: Şehir {kaynak} -> Şehir {hedef}, Miktar: {miktar}")
                else:
                    siparis["miktar"] = eksik_miktar
                    print(f"Sipariş gerçekleştirilemedi: Eksik Miktar {eksik_miktar}")

        for siparis in tamamlanan_siparisler:
            self.siparisler.remove(siparis)

    def grafi_ciz(self):
        if not self.G.edges:
            print("Graf çizilemedi: Hiçbir akış bulunmuyor.")
            return

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G, pos, node_color='lightblue', node_size=2000, alpha=0.7)
        nx.draw_networkx_edges(self.G, pos, edge_color='gray', width=2, arrowsize=20)
        nx.draw_networkx_labels(self.G, pos, font_size=10)
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels)
        plt.title("Şehirler Arası Kargo Akış Ağı")
        plt.axis('off')
        plt.show()

def ornek_kullanim():
    sistem = KargoAkisSistemi(4)
    sistem.stok_ekle(0, 10)
    sistem.stok_ekle(1, 15) 
    sistem.stok_ekle(2, 25) 
    sistem.stok_ekle(3, 0)  

    sistem.siparis_ekle(0, 1, 10)
    sistem.siparis_ekle(0, 2, 15)
    sistem.siparis_ekle(1, 3, 8)
    sistem.siparis_ekle(2, 3, 12)
    sistem.siparis_ekle(0, 3, 14)

    print("\nSiparişler işleniyor...")
    sistem.siparis_isle()

    print("\nSon Stok Durumu:", dict(sistem.stoklar))

    print("\nKalan siparişler:")
    if not sistem.siparisler:
        print("Kalan sipariş yok")
    else:
        for siparis in sistem.siparisler:
            print(siparis)
            
    hedef_sehir = 3 
    sistem.hesapla_maksimum_akis(hedef_sehir)

    sistem.grafi_ciz()

ornek_kullanim()