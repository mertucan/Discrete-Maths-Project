from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt


class KargoAkisSistemi:
    def __init__(self, sehir_sayisi):
        self.sehir_sayisi = sehir_sayisi
        self.akim_agi = defaultdict(lambda: defaultdict(int))  # Akış ağı (flow network)
        self.stoklar = defaultdict(int)  # Şehirlerin stok bilgisi
        self.G = nx.DiGraph()  # NetworkX grafiği (yönlü graf)
        self.siparisler = []  # Kalan siparişlerin takibi için

    def stok_ekle(self, sehir, miktar):
        self.stoklar[sehir] = miktar

    def siparis_ekle(self, kaynak, hedef, miktar):
        self.siparisler.append({"kaynak": kaynak, "hedef": hedef, "miktar": miktar})
        print(f"Yeni sipariş eklendi: Şehir {kaynak} -> Şehir {hedef}, Miktar: {miktar}")

    def bfs(self, kaynak, hedef, yol):
        """
        Breadth-First Search (BFS) ile bir yol bulur.
        """
        ziyaret_edilen = [False] * self.sehir_sayisi
        kuyruk = [kaynak]
        ziyaret_edilen[kaynak] = True

        while kuyruk:
            u = kuyruk.pop(0)
            for v in range(self.sehir_sayisi):
                if not ziyaret_edilen[v] and self.akim_agi[u][v] > 0:
                    kuyruk.append(v)
                    ziyaret_edilen[v] = True
                    yol[v] = u
                    if v == hedef:
                        return True
        return False

    def ford_fulkerson(self, kaynak, hedef):
        yol = [-1] * self.sehir_sayisi
        max_akim = 0

        while self.bfs(kaynak, hedef, yol):
            yol_akimi = float("inf")
            v = hedef

            while v != kaynak:
                u = yol[v]
                yol_akimi = min(yol_akimi, self.akim_agi[u][v])
                v = yol[v]

            v = hedef
            while v != kaynak:
                u = yol[v]
                self.akim_agi[u][v] -= yol_akimi
                self.akim_agi[v][u] += yol_akimi
                v = yol[v]

            max_akim += yol_akimi

        return max_akim

    def alternatif_sehir_bul(self, miktar):
        """
        Alternatif stok bulunan şehirlerden birini döndürür.
        """
        for sehir, stok in self.stoklar.items():
            if stok >= miktar:
                return sehir
        return None

    def stok_tasi(self, kaynak, hedef, miktar):
        """
        Alternatif bir kaynaktan belirtilen miktarda stoğu eksik noktaya taşır.
        """
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

            # Şehirlerin mevcut stoklarını yazdır
            print(f"\nMevcut stoklar: {dict(self.stoklar)}")

            if self.stoklar[kaynak] >= miktar:
                # Stok yeterli, sipariş tamamlanır
                self.akim_agi[kaynak][hedef] += miktar
                self.stoklar[kaynak] -= miktar
                self.stoklar[hedef] += miktar  # Hedef şehrin stoğunu artır
                self.G.add_edge(f"Şehir {kaynak}", f"Şehir {hedef}", weight=miktar)
                tamamlanan_siparisler.append(siparis)
                print(f"Sipariş tamamlandı: Şehir {kaynak} -> Şehir {hedef}, Miktar: {miktar}")
            else:
                # Stok yetersiz, alternatif stok taşınır
                eksik_miktar = miktar - self.stoklar[kaynak]
                print(f"Kalan sipariş: Şehir {kaynak} -> Şehir {hedef}, Eksik Miktar: {eksik_miktar}")

                alternatif_kaynak = self.alternatif_sehir_bul(eksik_miktar)
                if alternatif_kaynak:
                    tasinan_miktar = self.stok_tasi(alternatif_kaynak, kaynak, eksik_miktar)
                    eksik_miktar -= tasinan_miktar

                if eksik_miktar == 0:
                    # Alternatif stokla sipariş tamamlandı
                    self.akim_agi[kaynak][hedef] += miktar
                    self.stoklar[kaynak] -= miktar
                    self.stoklar[hedef] += miktar  # Hedef şehrin stoğunu artır
                    self.G.add_edge(f"Şehir {kaynak}", f"Şehir {hedef}", weight=miktar)
                    tamamlanan_siparisler.append(siparis)
                    print(f"Sipariş tamamlandı: Şehir {kaynak} -> Şehir {hedef}, Miktar: {miktar}")
                else:
                    # Siparişin kalan miktarı tekrar beklemeye alınır
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

# Kullanım Örneği
def ornek_kullanim():
    sistem = KargoAkisSistemi(4)
    sistem.stok_ekle(0, 10)  # Şehir 0 stoğu: 10
    sistem.stok_ekle(1, 15)  # Şehir 1 stoğu: 15
    sistem.stok_ekle(2, 25)  # Şehir 2 stoğu: 25
    sistem.stok_ekle(3, 0)   # Şehir 3 stoğu: 0

    sistem.siparis_ekle(0, 1, 10)
    sistem.siparis_ekle(0, 2, 15)
    sistem.siparis_ekle(1, 3, 8)
    sistem.siparis_ekle(2, 3, 12)

    print("\nSiparişler işleniyor...")
    sistem.siparis_isle()

    # Son stok durumu yazdırılır
    print("\nSon Stok Durumu:", dict(sistem.stoklar))

    print("\nKalan siparişler:")
    if not sistem.siparisler:
        print("Kalan sipariş yok")
    else:
        for siparis in sistem.siparisler:
            print(siparis)

    sistem.grafi_ciz()

ornek_kullanim()