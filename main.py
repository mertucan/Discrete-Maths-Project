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
                            print(f"  → {city.name} şehrinden {destination.name} şehrine yük gönderilemedi!")
                            print(f"    → Sebep: Eksik miktar: {required_weight}. Teslimat gerçekleştirilemedi.")
                            city.outgoing.remove((destination, weight))
                    else:
                        print(f"  → {city.name} şehrinden {destination.name} şehrine yük gönderilemedi!")
                        print(f"    → Sebep: Yeterli donör şehir yok. Eksik yük tamamlanamadı.")
        
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
    print("\n[Teslimat Durumları]")
    for city in cities:
        print(f"{city.name} -> Depodaki Yük: {city.current_stock}")


def print_initial_deliveries(cities):
    print("\n[Teslimatlar Başlangıç Durumu]")
    for city in cities:
        for destination, weight in city.outgoing:
            print(f"  {city.name} şehrinden {destination.name} şehrine {weight} yük gönderilecek.")


def get_user_input():
    choice = int(input("\nLütfen bir seçenek girin:\n1 - Hazır örneği görmek için\n2 - Kendi örneğinizi girmek için\n\nSeçiminizi yapın (1/2): "))
    if choice == 1:
        # Hazır örnek
        print("Hazır örnek üzerinden devam ediliyor...")
        cities = [City("A"), City("B"), City("C"), City("D")]
        deliveries = [
            (cities[0], cities[1], 120),  # A -> B
            (cities[0], cities[2], 50),   # A -> C
            (cities[1], cities[3], 80),   # B -> D
            (cities[2], cities[3], 60)    # C -> D
        ]
        stocks = [50, 150, 30, 0]  # Şehirlerin başlangıç stokları
        return cities, deliveries, stocks
    elif choice == 2:
        # Kullanıcıdan giriş al
        while True:
            num_cities = int(input("Kaç şehir olacak? (En az 2 şehir olmalı): "))
            if num_cities < 2:
                print("Hata: En az 2 şehir girmelisiniz.")
            else:
                break

        cities = []
        for i in range(num_cities):
            while True:
                city_name = input(f"{i+1}. şehrin ismini girin: ")
                # Aynı şehir isminden başka bir şehir eklenmemeli
                if city_name in [city.name for city in cities]:
                    print("Hata: Bu şehir ismi zaten mevcut. Farklı bir şehir ismi girin.")
                else:
                    cities.append(City(city_name))
                    break

        # Şehirlerin başlangıç stokları
        print("\nHer şehire ait başlangıç stoklarını girin:")
        stocks = []
        for i, city in enumerate(cities):
            stock = int(input(f"{city.name} şehri için stok miktarını girin: "))
            stocks.append(stock)

        # Teslimatlar
        deliveries = []
        num_deliveries = int(input("Kaç teslimat yapılacak? "))
        for _ in range(num_deliveries):
            while True:
                print("\nTeslimat formatı: <gönderen şehir adı> <hedef şehir adı> <yük miktarı>")
                sender_name = input("Gönderen şehri ismiyle seçin: ")
                recipient_name = input("Hedef şehri ismiyle seçin: ")

                # Şehir isminin doğru olduğuna emin ol
                valid_cities = [city.name for city in cities]
                if sender_name not in valid_cities:
                    print(f"Hata: {sender_name} ismi geçerli bir şehir değil.")
                elif recipient_name not in valid_cities:
                    print(f"Hata: {recipient_name} ismi geçerli bir şehir değil.")
                else:
                    weight = int(input("Yük miktarını girin: "))
                    sender_city = next(city for city in cities if city.name == sender_name)
                    recipient_city = next(city for city in cities if city.name == recipient_name)
                    deliveries.append((sender_city, recipient_city, weight))
                    break

        return cities, deliveries, stocks


def main():
    cities, deliveries, stocks = get_user_input()

    # Şehirler ve stoklar
    for i, city in enumerate(cities):
        city.current_stock = stocks[i]

    # Başlangıç stoklarını debug formatında yazdır
    print("\n[Başlangıç Stok Durumu]")
    for city, stock in zip(cities, stocks):
        print(f"  {city.name} şehri için başlangıç stoğu: {stock}")

    # Teslimatları ekle
    for sender_city, recipient_city, weight in deliveries:
        sender_city.add_delivery(recipient_city, weight)

    # Başlangıçta teslimat bilgilerini yazdır
    print_initial_deliveries(cities)

    # Teslimatları başlat
    process_deliveries(cities)

    # Teslimat durumlarını ekrana yazdır
    print_deliveries(cities)


if __name__ == "__main__":
    main()
