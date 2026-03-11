import OyunlarProje.tetris
import OyunlarProje.SnakeGame
def AltMenu2():
    print("╔════════════════════════╗")
    print("║     Oyunlar            ║")
    print("╠════════════════════════╣")
    print("║ 1-) Tetris             ║")
    print("║ 2-) Snake              ║")
    print("║ 3-) Zindan             ║")
    print("║                        ║")
    print("║                        ║")
    print("║                        ║")
    print("║                        ║")
    print("║  0-Geri Dön            ║")
    print("╚════════════════════════╝")

    secim = input("Seçiminiz nedir?: ")
    print(f"{secim}. seçeneği seçtiniz.")
    if secim == "1":
        OyunlarProje.tetris.run_game()
    elif secim == "2":
        OyunlarProje.SnakeGame.run_snake()
    #elif secim == "3":

if __name__ == "__main__":
    AltMenu2()
    