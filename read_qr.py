import cv2

img = cv2.imread("qr.png")  # mets le vrai nom du fichier

if img is None:
    print("❌ Image introuvable")
    exit()

detector = cv2.QRCodeDetector()
data, points, _ = detector.detectAndDecode(img)

if data:
    print("✅ QR détecté")
    print("Contenu :", data)
else:
    print("❌ Aucun QR détecté")
