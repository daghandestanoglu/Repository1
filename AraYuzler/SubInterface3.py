def AltMenu3():
    import turtle

    print("╔════════════════════════╗")
    print("║       Çizimler         ║")
    print("╠════════════════════════╣")
    print("║ 1-) Kare               ║")
    print("║ 2-) Üçgen              ║")
    print("║ 3-) Daire              ║")
    print("║                        ║")
    print("║  0-Geri Dön            ║")
    print("╚════════════════════════╝")

    choice = input("Lütfen bir seçenek girin (0-3): ").strip()

    if choice == "0":
        return

    screen = turtle.Screen()
    screen.title("Çizim")
    t = turtle.Turtle()

    if choice == "1":
        for _ in range(4):
            t.forward(100)
            t.right(90)
    elif choice == "2":
        for _ in range(3):
            t.forward(100)
            t.right(120)
    elif choice == "3":
        t.circle(50)
    else:
        print("Geçersiz giriş!")
        screen.bye()
        AltMenu3()
        return

    # Çizim bitti, kullanıcıdan input al
    print("\nÇizim tamamlandı!")
    print("Ana menüye dönmek için 0'a basın: ", end="")
    while input().strip() != "0":
        print("Ana menüye dönmek için 0'a basın: ", end="")

    screen.bye()  # Turtle penceresini kapat
    return #ile ana menüye döner

if __name__ == "__main__":
    AltMenu3()