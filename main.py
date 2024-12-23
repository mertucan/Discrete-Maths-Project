class City:
    def __init__(self, name):
        self.name = name
        self.current_stock = 0  # Şu an depoda bulunan yük miktarı
        self.outgoing = []  # [(hedef_şehir, yük)]

    def add_delivery(self, destination, weight):
        self.outgoing.append((destination, weight))


def process_deliveries(cities):
    step = 1
    while True:
        print(f"\n{'='*30}")
        print(f"Adım {step}: Teslimat İşlemleri")
        print(f"{'='*30}")
        deliveries_completed = True  # Her adımda teslimat tamamlandığı varsayılacak

        for city in cities:
            for destination, weight in city.outgoing[:]:  # Şu anki teslimatlar
                print(f"\n[İşlem Başlatıldı] {city.name} -> {destination.name} ({weight} yük)")

                if city.current_stock >= weight:
                    # Eğer yeterli yük varsa, teslimat yapılır
                    city.current_stock -= weight
                    destination.current_stock += weight
                    city.outgoing.remove((destination, weight))
                    print(f"  → {city.name} şehrinden {destination.name} şehrine {weight} yük gönderildi.")
                    print(f"  → Teslimat Tamamlandı: ({weight} yük) başarıyla teslim edildi.")
                else:
                    # Yeterli yük yoksa, eksik miktarı belirle
                    required_weight = weight - city.current_stock
                    total_available_weight = 0
                    donors = []

                    # Eksik yük için uygun donör şehirler
                    for donor in cities:
                        if donor != city and donor.current_stock > 0:
                            donors.append(donor)
                            total_available_weight += donor.current_stock

                    if total_available_weight >= required_weight:
                        # Donör şehirlerden yük aktarımı yapılır
                        while required_weight > 0 and donors:
                            donor = max(donors, key=lambda x: x.current_stock)  # En yüksek stoka sahip şehir
                            donors.remove(donor)

                            if donor.current_stock >= required_weight:
                                donor.current_stock -= required_weight
                                city.current_stock += required_weight
                                print(f"  → {donor.name} şehrinden {city.name} şehrine {required_weight} yük transfer edildi.")
                                required_weight = 0
                            else:
                                city.current_stock += donor.current_stock
                                required_weight -= donor.current_stock
                                print(f"  → {donor.name} şehrinden {city.name} şehrine {donor.current_stock} yük transfer edildi.")
                                donor.current_stock = 0
                        
                        # Eksik yük tamamlanamazsa teslimat yapılmaz
                        if required_weight > 0:
                            print(f"  → {city.name} şehrinden {destination.name} şehrine yük gönderilemedi! Eksik miktar: {required_weight}.")
                            city.outgoing.remove((destination, weight))
                    else:
                        print(f"  → {city.name} şehrinden {destination.name} şehrine yük gönderilemedi! Yeterli donör şehir yok.")
        
        # Teslimatlar tamamlandıysa döngüyü sonlandır
        if all(len(city.outgoing) == 0 for city in cities):
            print("\n" + "="*30)
            print("Tüm teslimatlar tamamlandı.")
            print("="*30)
            break

        step += 1
        print("-" * 30)

        if step > 5:  # Sonsuz döngüyü önlemek için sınır
            print("\nHata: Sonsuz döngüyü girildi!")
            break


def print_deliveries(cities):
    print("\nTeslimat Durumları:")
    for city in cities:
        print(f"{city.name} -> Depodaki Yük: {city.current_stock}")


def print_initial_deliveries(cities):
    print("\nTeslimatlar Başlangıç Durumu:")
    for city in cities:
        for destination, weight in city.outgoing:
            print(f"  {city.name} şehrinden {destination.name} şehrine {weight} yük gönderilecek.")


def main():
    # Şehirleri ve teslimatları tanımla
    city1 = City("A")
    city2 = City("B")
    city3 = City("C")
    city4 = City("D")

    # Teslimatları ekle
    city1.add_delivery(city2, 120)
    city1.add_delivery(city3, 50)
    city2.add_delivery(city4, 80)
    city3.add_delivery(city4, 60)

    # Şehirleri listele
    cities = [city1, city2, city3, city4]

    # Başlangıçta teslimat bilgilerini yazdır
    print_initial_deliveries(cities)

    # İlk yük miktarlarını belirle
    city1.current_stock = 50  # Yük miktarı eksik (100 eksik)
    city2.current_stock = 150  # Yük miktarı fazla
    city3.current_stock = 30
    city4.current_stock = 0

    # Teslimatları başlat
    process_deliveries(cities)

    # Teslimat durumlarını ekrana yazdır
    print_deliveries(cities)


if __name__ == "__main__":
    main()
