"""
Tema: Sistem Kasir

Nama: Restu Azmi Firmansah
NIM: 14012500101
Kelas: 3B-KOM
Mata Kuliah: Pemprograman Berbasis Objek
"""


class Produk:
    """Class untuk merepresentasikan produk yang dijual di toko."""

    # Class attribute
    jumlah_produk = 0

    def __init__(self, kode: str, nama: str, harga: int, stok: int):
        # Encapsulation dengan private attributes (__)
        self.__kode = kode.strip().upper()
        self.__nama = ""
        self.__harga = 0
        self.__stok = 0

        # Validasi melalui setter
        self.nama = nama
        self.harga = harga
        self.stok = stok

        Produk.jumlah_produk += 1

    # --- Property & Setter (Encapsulation) ---
    @property
    def kode(self) -> str:
        return self.__kode

    @property
    def nama(self) -> str:
        return self.__nama

    @nama.setter
    def nama(self, nilai: str) -> None:
        if not nilai or not nilai.strip():
            raise ValueError("Nama produk tidak boleh kosong.")
        self.__nama = nilai.strip()

    @property
    def harga(self) -> int:
        return self.__harga

    @harga.setter
    def harga(self, nilai: int) -> None:
        if nilai < 0:
            raise ValueError("Harga produk tidak boleh negatif.")
        self.__harga = int(nilai)

    @property
    def stok(self) -> int:
        return self.__stok

    @stok.setter
    def stok(self, nilai: int) -> None:
        if nilai < 0:
            raise ValueError("Stok produk tidak boleh negatif.")
        self.__stok = int(nilai)

    # --- Instance Methods ---
    def tambah_stok(self, jumlah: int) -> None:
        if jumlah <= 0:
            raise ValueError("Jumlah penambahan stok harus lebih dari 0.")
        self.stok += jumlah

    def kurangi_stok(self, jumlah: int) -> None:
        if jumlah <= 0:
            raise ValueError("Jumlah pengurangan stok harus lebih dari 0.")
        if jumlah > self.stok:
            raise ValueError(f"Stok {self.nama} tidak mencukupi (tersisa {self.stok}).")
        self.stok -= jumlah

    def info(self) -> str:
        return (
            f"[{self.kode}] {self.nama:<20} | "
            f"Harga: {self.format_rupiah(self.harga):>12} | Stok: {self.stok}"
        )

    # --- Class Methods ---
    @classmethod
    def total_produk(cls) -> int:
        return cls.jumlah_produk

    @classmethod
    def dari_dict(cls, data: dict) -> "Produk":
        """Alternative constructor untuk membuat objek Produk dari dictionary."""
        return cls(
            kode=data["kode"],
            nama=data["nama"],
            harga=data["harga"],
            stok=data["stok"],
        )

    # --- Static Method ---
    @staticmethod
    def format_rupiah(nominal: int | float) -> str:
        angka = int(round(nominal))
        return f"Rp{angka:,}".replace(",", ".")


class Kasir:
    """Class untuk mengelola transaksi kasir, keranjang belanja, dan pembayaran."""

    # Class attributes
    nama_toko = "Toko Serba Ada"
    pajak_ppn = 0.11  # 11%
    total_transaksi_selesai = 0

    def __init__(self, nama_kasir: str):
        # Encapsulation dengan private attributes (__)
        self.__nama_kasir = nama_kasir.strip() or "Kasir"
        self.__keranjang: list[dict] = []
        self.__diskon_persen = 0.0

    # --- Property & Setter ---
    @property
    def nama_kasir(self) -> str:
        return self.__nama_kasir

    @property
    def diskon_persen(self) -> float:
        return self.__diskon_persen

    @diskon_persen.setter
    def diskon_persen(self, nilai: float) -> None:
        if nilai < 0 or nilai > 100:
            raise ValueError("Diskon harus berada di antara 0% sampai 100%.")
        self.__diskon_persen = float(nilai)

    @property
    def keranjang(self) -> list[dict]:
        # Mengembalikan salinan list agar data internal tetap terlindungi
        return list(self.__keranjang)

    # --- Instance Methods ---
    def tambah_ke_keranjang(self, produk: Produk, jumlah: int) -> None:
        if jumlah <= 0:
            raise ValueError("Jumlah beli harus lebih dari 0.")

        for item in self.__keranjang:
            if item["produk"].kode == produk.kode:
                total_diminta = item["jumlah"] + jumlah
                if total_diminta > produk.stok:
                    raise ValueError(
                        f"Stok {produk.nama} tidak cukup. "
                        f"Di keranjang: {item['jumlah']}, stok tersedia: {produk.stok}."
                    )
                item["jumlah"] = total_diminta
                return

        if jumlah > produk.stok:
            raise ValueError(
                f"Stok {produk.nama} tidak mencukupi (tersedia {produk.stok})."
            )
        self.__keranjang.append({"produk": produk, "jumlah": jumlah})

    def hapus_dari_keranjang(self, kode_produk: str) -> bool:
        kode = kode_produk.strip().upper()
        for idx, item in enumerate(self.__keranjang):
            if item["produk"].kode == kode:
                self.__keranjang.pop(idx)
                return True
        return False

    def hitung_subtotal(self) -> int:
        return sum(item["produk"].harga * item["jumlah"] for item in self.__keranjang)

    def hitung_diskon(self) -> int:
        return int(round(self.hitung_subtotal() * (self.__diskon_persen / 100)))

    def hitung_pajak(self) -> int:
        setelah_diskon = self.hitung_subtotal() - self.hitung_diskon()
        return int(round(setelah_diskon * Kasir.pajak_ppn))

    def hitung_total(self) -> int:
        return self.hitung_subtotal() - self.hitung_diskon() + self.hitung_pajak()

    def proses_pembayaran(self, uang_bayar: int) -> str:
        if not self.__keranjang:
            raise ValueError("Keranjang belanja masih kosong.")

        total = self.hitung_total()
        kembalian = self.hitung_kembalian(total, uang_bayar)

        # Kurangi stok masing-masing produk
        for item in self.__keranjang:
            item["produk"].kurangi_stok(item["jumlah"])

        Kasir.total_transaksi_selesai += 1
        struk = self.__buat_struk(total, uang_bayar, kembalian)

        # Reset keranjang & diskon setelah transaksi berhasil
        self.__keranjang.clear()
        self.__diskon_persen = 0.0
        return struk

    def __buat_struk(self, total: int, uang_bayar: int, kembalian: int) -> str:
        garis = "=" * 48
        pemisah = "-" * 48
        baris = [
            garis,
            f"{Kasir.nama_toko.center(48)}",
            f"Kasir: {self.nama_kasir}".center(48),
            garis,
        ]
        for item in self.__keranjang:
            produk = item["produk"]
            jumlah = item["jumlah"]
            sub = produk.harga * jumlah
            baris.append(f"{produk.nama}")
            baris.append(
                f"  {jumlah} x {Produk.format_rupiah(produk.harga):<12}"
                f"{Produk.format_rupiah(sub):>30}"
            )
        baris.extend(
            [
                pemisah,
                f"{'Subtotal':<24}{Produk.format_rupiah(self.hitung_subtotal()):>24}",
                f"{f'Diskon ({self.diskon_persen:.0f}%)':<24}"
                f"{Produk.format_rupiah(self.hitung_diskon()):>24}",
                f"{f'PPN ({Kasir.pajak_ppn * 100:.0f}%)':<24}"
                f"{Produk.format_rupiah(self.hitung_pajak()):>24}",
                pemisah,
                f"{'TOTAL':<24}{Produk.format_rupiah(total):>24}",
                f"{'Bayar':<24}{Produk.format_rupiah(uang_bayar):>24}",
                f"{'Kembalian':<24}{Produk.format_rupiah(kembalian):>24}",
                garis,
                "Terima kasih telah berbelanja!".center(48),
                garis,
            ]
        )
        return "\n".join(baris)

    # --- Class Methods ---
    @classmethod
    def ubah_pajak(cls, pajak_baru: float) -> None:
        if pajak_baru < 0 or pajak_baru > 1:
            raise ValueError("Pajak PPN harus berupa desimal antara 0 dan 1 (misal 0.11).")
        cls.pajak_ppn = pajak_baru

    @classmethod
    def info_toko(cls) -> str:
        return (
            f"Toko: {cls.nama_toko} | "
            f"PPN: {cls.pajak_ppn * 100:.0f}% | "
            f"Transaksi Selesai: {cls.total_transaksi_selesai}"
        )

    # --- Static Method ---
    @staticmethod
    def hitung_kembalian(total: int, uang_bayar: int) -> int:
        if uang_bayar < total:
            kurang = Produk.format_rupiah(total - uang_bayar)
            raise ValueError(f"Uang pembayaran kurang sebesar {kurang}.")
        return uang_bayar - total


def jalankan_aplikasi():
    # Membuat object dari class Produk (termasuk menggunakan @classmethod dari_dict)
    daftar_produk = [
        Produk("P001", "Beras 5kg", 75000, 10),
        Produk("P002", "Minyak Goreng 2L", 38000, 15),
        Produk("P003", "Gula Pasir 1kg", 17500, 20),
        Produk.dari_dict({"kode": "P004", "nama": "Kopi Bubuk 200g", "harga": 24000, "stok": 12}),
    ]

    # Membuat object dari class Kasir
    kasir = Kasir("Andi")

    while True:
        print("\n=== SISTEM KASIR SEDERHANA ===")
        print(Kasir.info_toko())
        print(f"Total jenis produk terdaftar: {Produk.total_produk()}")
        print("1. Lihat Daftar Produk")
        print("2. Tambah Produk ke Keranjang")
        print("3. Lihat Keranjang")
        print("4. Atur Diskon (%)")
        print("5. Bayar & Cetak Struk")
        print("6. Ubah Harga / Stok Produk (Test Setter)")
        print("0. Keluar")

        pilihan = input("Pilih menu (0-6): ").strip()

        if pilihan == "1":
            print("\n--- DAFTAR PRODUK ---")
            for p in daftar_produk:
                print(p.info())

        elif pilihan == "2":
            kode = input("Masukkan kode produk (misal P001): ").strip().upper()
            produk_ditemukan = next((p for p in daftar_produk if p.kode == kode), None)
            if not produk_ditemukan:
                print("Produk tidak ditemukan.")
                continue
            try:
                jumlah = int(input(f"Masukkan jumlah beli untuk {produk_ditemukan.nama}: "))
                kasir.tambah_ke_keranjang(produk_ditemukan, jumlah)
                print(f"Berhasil menambahkan {jumlah}x {produk_ditemukan.nama} ke keranjang.")
            except ValueError as e:
                print(f"Error: {e}")

        elif pilihan == "3":
            print("\n--- KERANJANG BELANJA ---")
            if not kasir.keranjang:
                print("Keranjang masih kosong.")
            else:
                for item in kasir.keranjang:
                    p = item["produk"]
                    j = item["jumlah"]
                    print(f"- {p.nama} ({j}x) = {Produk.format_rupiah(p.harga * j)}")
                print(f"Subtotal : {Produk.format_rupiah(kasir.hitung_subtotal())}")
                print(f"Diskon   : {Produk.format_rupiah(kasir.hitung_diskon())} ({kasir.diskon_persen:.0f}%)")
                print(f"PPN      : {Produk.format_rupiah(kasir.hitung_pajak())}")
                print(f"Total    : {Produk.format_rupiah(kasir.hitung_total())}")

        elif pilihan == "4":
            try:
                diskon = float(input("Masukkan diskon (%): "))
                kasir.diskon_persen = diskon
                print(f"Diskon diatur menjadi {kasir.diskon_persen:.0f}%.")
            except ValueError as e:
                print(f"Error: {e}")

        elif pilihan == "5":
            if not kasir.keranjang:
                print("Keranjang masih kosong.")
                continue
            total = kasir.hitung_total()
            print(f"Total yang harus dibayar: {Produk.format_rupiah(total)}")
            try:
                bayar = int(input("Masukkan nominal uang bayar: "))
                struk = kasir.proses_pembayaran(bayar)
                print("\n" + struk)
            except ValueError as e:
                print(f"Error: {e}")

        elif pilihan == "6":
            kode = input("Masukkan kode produk yang ingin diubah: ").strip().upper()
            produk_ditemukan = next((p for p in daftar_produk if p.kode == kode), None)
            if not produk_ditemukan:
                print("Produk tidak ditemukan.")
                continue
            try:
                harga_baru = int(input("Masukkan harga baru: "))
                stok_baru = int(input("Masukkan stok baru: "))
                produk_ditemukan.harga = harga_baru
                produk_ditemukan.stok = stok_baru
                print("Data produk berhasil diperbarui:")
                print(produk_ditemukan.info())
            except ValueError as e:
                print(f"Error: {e}")

        elif pilihan == "0":
            print("Terima kasih telah menggunakan Sistem Kasir.")
            break
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    jalankan_aplikasi()
