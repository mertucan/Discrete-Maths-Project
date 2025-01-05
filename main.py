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

    def bfs(self, kaynak, hedef, yol):
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
    
    def bul_tum_yollar(self, kaynak, hedef, ziyaret_edildi, yol, tum_yollar):
        """Kaynaktan hedefe giden tüm olası yolları bulur"""
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

    def hesapla_maksimum_akis(self, hedef_sehir):
        # Orijinal ağı yedekle
        original_ag = defaultdict(lambda: defaultdict(int))
        for u in range(self.sehir_sayisi):
            for v in range(self.sehir_sayisi):
                original_ag[u][v] = self.akim_agi[u][v]

        max_akis = 0
        kullanilan_yollar = []

        # Her kaynak şehir için maksimum akışı hesapla
        for kaynak in range(self.sehir_sayisi):
            if kaynak != hedef_sehir:
                # Tüm olası yolları bul
                ziyaret_edildi = [False] * self.sehir_sayisi
                yol = []
                tum_yollar = []
                self.bul_tum_yollar(kaynak, hedef_sehir, ziyaret_edildi, yol, tum_yollar)

                # Her yol için akış hesapla
                for yol in tum_yollar:
                    yol_kapasitesi = self.hesapla_yol_kapasitesi(yol)
                    if yol_kapasitesi > 0:
                        self.guncelle_akim_agi(yol, yol_kapasitesi)
                        max_akis += yol_kapasitesi
                        kullanilan_yollar.append((yol, yol_kapasitesi))

        # Sonuçları yazdır
        print("Kaynak Şehirden Hedef Şehre Giden Yollar ve Akışlar:")
        for yol, akis in kullanilan_yollar:
            yol_str = " -> ".join(str(sehir) for sehir in yol)
            print(f"Yol {yol_str}: {akis} birim")

        print(f"\nToplam Maksimum Akış: {max_akis}")

        # Orijinal ağı geri yükle
        self.akim_agi = original_ag

        return max_akis, kullanilan_yollar

    def _bul_kullanilan_yollar(self, onceki_ag, sonraki_ag, kaynak, hedef):
        """
        İki ağ arasındaki farkı kullanarak kullanılan yolları bulur
        """
        yollar = []
        def dfs(node, path, flow):
            if node == hedef:
                yollar.append((path[:], flow))
                return
            for next_node in range(self.sehir_sayisi):
                akis_farki = onceki_ag[node][next_node] - sonraki_ag[node][next_node]
                if akis_farki > 0 and next_node not in path:
                    path.append(next_node)
                    dfs(next_node, path, min(flow, akis_farki))
                    path.pop()
        
        dfs(kaynak, [kaynak], float('inf'))
        return yollar

    def hesapla_yol_kapasitesi(self, yol):
        """Verilen yolun minimum kapasitesini hesaplar"""
        min_kapasite = float('inf')
        for i in range(len(yol) - 1):
            kapasite = self.akim_agi[yol[i]][yol[i + 1]]
            min_kapasite = min(min_kapasite, kapasite)
        return min_kapasite

    def guncelle_akim_agi(self, yol, akim):
        """Ağdaki akışı günceller"""
        for i in range(len(yol) - 1):
            u, v = yol[i], yol[i + 1]
            self.akim_agi[u][v] -= akim
            self.akim_agi[v][u] += akim

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
            
    # Hedef şehir için maksimum akış hesapla
    hedef_sehir = 3 
    sistem.hesapla_maksimum_akis(hedef_sehir)

    sistem.grafi_ciz()

ornek_kullanim()