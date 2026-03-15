def AltMenu3():
    import turtle
    import importlib

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

    if choice not in ("1", "2", "3"):
        print("Geçersiz giriş!")
        return

    # ✅ Turtle modülünü sıfırla — önceki pencere kapatılmış olsa bile temiz başlar
    importlib.reload(turtle)

    try:
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

        print("\nÇizim tamamlandı!")
        while input("Ana menüye dönmek için 0'a basın: ").strip() != "0":
            pass

    except turtle.Terminator:
        pass  # Kullanıcı pencereyi kapattıysa sessizce çık

    finally:
        try:
            turtle.bye()
        except Exception:
            pass
if __name__ == "__main__":
    AltMenu3()