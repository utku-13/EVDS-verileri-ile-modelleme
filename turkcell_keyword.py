# Turkcell Google Trends Analizi
# pytrends kütüphanesi kullanarak Google Trends verilerini çekme

import os
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
from dotenv import load_dotenv
import seaborn as sns

# Environment variables yükle
load_dotenv()

class TurkcellTrendsAnalyzer:
    def __init__(self):
        """Google Trends analiz sınıfını başlat"""
        self.pytrends = TrendReq(hl='tr-TR', tz=180)  # Türkiye lokasyonu
        self.keyword = 'turkcell'
        self.data = None
        
    def get_interest_over_time(self, start_year=2022, end_year=2023, daily=False):
        """
        Belirtilen yıllar arasında Turkcell kelimesinin arama sıklığını getir
        daily=True ise günlük veri alır (sadece 1 yıl için)
        """
        try:
            # Günlük veri isteniyor ve 1 yıldan fazla ise uyarı ver
            if daily and (end_year - start_year) > 1:
                print("⚠️  Günlük veri için maksimum 1 yıl seçebilirsiniz. Son yıl alınacak.")
                start_year = end_year - 1
            
            # Zaman aralığını ayarla
            if daily:
                # Günlük veri için
                timeframe = f'{start_year}-01-01 {end_year}-12-31'
                print(f"📅 Günlük veri alınıyor: {timeframe}")
            else:
                # Haftalık veri için (eski yöntem)
                timeframe = f'{start_year}-01-01 {end_year}-12-31'
                print(f"📅 Haftalık veri alınıyor: {timeframe}")
            
            # Anahtar kelimeyi ayarla
            self.pytrends.build_payload([self.keyword], 
                                      cat=0, 
                                      timeframe=timeframe, 
                                      geo='TR',  # Türkiye
                                      gprop='')
            
            # Zaman içinde ilgi verilerini al
            self.data = self.pytrends.interest_over_time()
            
            if not self.data.empty:
                # 'isPartial' sütununu kaldır (varsa)
                if 'isPartial' in self.data.columns:
                    self.data = self.data.drop(columns=['isPartial'])
                
                print(f"✅ {start_year}-{end_year} arası Turkcell trend verileri başarıyla alındı")
                print(f"📊 Veri boyutu: {self.data.shape}")
                print(f"📅 Tarih aralığı: {self.data.index.min()} - {self.data.index.max()}")
                return self.data
            else:
                print("❌ Veri bulunamadı")
                return None
                
        except Exception as e:
            print(f"❌ Hata oluştu: {e}")
            return None
    
    def get_interest_by_region(self):
        """
        Turkcell kelimesinin bölgelere göre arama sıklığını getir
        """
        try:
            if self.data is None:
                print("⚠️  Önce interest_over_time() metodunu çalıştırın")
                return None
                
            # Bölgesel ilgi verilerini al
            regional_data = self.pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
            
            if not regional_data.empty:
                print("✅ Bölgesel trend verileri başarıyla alındı")
                print(f"📊 Bölge sayısı: {len(regional_data)}")
                return regional_data.sort_values(by=self.keyword, ascending=False)
            else:
                print("❌ Bölgesel veri bulunamadı")
                return None
                
        except Exception as e:
            print(f"❌ Bölgesel veri alınırken hata oluştu: {e}")
            return None
    
    def plot_interest_over_time(self):
        """
        Zaman içinde ilgi grafiğini çiz
        """
        if self.data is None or self.data.empty:
            print("⚠️  Çizilecek veri bulunamadı")
            return
            
        plt.figure(figsize=(12, 6))
        plt.plot(self.data.index, self.data[self.keyword], linewidth=2, color='#e31e24')  # Turkcell kırmızısı
        plt.title(f'Turkcell Google Trends Analizi (Türkiye)', fontsize=16, fontweight='bold')
        plt.xlabel('Tarih', fontsize=12)
        plt.ylabel('Arama İlgisi (0-100)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # İstatistikleri göster
        max_date = self.data[self.keyword].idxmax()
        max_value = self.data[self.keyword].max()
        min_value = self.data[self.keyword].min()
        avg_value = self.data[self.keyword].mean()
        
        plt.text(0.02, 0.98, 
                f'📈 En yüksek: {max_value} ({max_date.strftime("%Y-%m-%d")})\n'
                f'📉 En düşük: {min_value}\n'
                f'📊 Ortalama: {avg_value:.1f}', 
                transform=plt.gca().transAxes, 
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.show()
    
    def plot_regional_interest(self, regional_data, top_n=10):
        """
        Bölgesel ilgi grafiğini çiz
        """
        if regional_data is None or regional_data.empty:
            print("⚠️  Çizilecek bölgesel veri bulunamadı")
            return
            
        # En yüksek ilgiye sahip bölgeleri al
        top_regions = regional_data.head(top_n)
        
        plt.figure(figsize=(12, 8))
        colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_regions)))
        bars = plt.barh(range(len(top_regions)), top_regions[self.keyword], color=colors)
        
        plt.yticks(range(len(top_regions)), top_regions.index)
        plt.xlabel('Arama İlgisi (0-100)', fontsize=12)
        plt.title(f'Turkcell - En Çok Aranan {top_n} Bölge (Türkiye)', fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        
        # Değerleri çubukların üzerine yaz
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                    f'{width}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def get_summary_stats(self):
        """
        Özet istatistikleri göster
        """
        if self.data is None or self.data.empty:
            print("⚠️  Analiz edilecek veri bulunamadı")
            return
            
        stats = self.data[self.keyword].describe()
        
        print("\n" + "="*50)
        print("📊 TURKCELL GOOGLE TRENDS ÖZETİ")
        print("="*50)
        print(f"📅 Tarih Aralığı: {self.data.index.min().strftime('%Y-%m-%d')} - {self.data.index.max().strftime('%Y-%m-%d')}")
        print(f"📈 En Yüksek İlgi: {stats['max']:.0f}")
        print(f"📉 En Düşük İlgi: {stats['min']:.0f}")
        print(f"📊 Ortalama İlgi: {stats['mean']:.1f}")
        print(f"📐 Standart Sapma: {stats['std']:.1f}")
        print(f"🎯 Medyan: {stats['50%']:.1f}")
        
        # En yüksek ilgi tarihi
        max_date = self.data[self.keyword].idxmax()
        print(f"🚀 En Yüksek İlgi Tarihi: {max_date.strftime('%Y-%m-%d')}")
        print("="*50)

def main():
    """
    Ana analiz fonksiyonu
    """
    print("🔍 Turkcell Google Trends Analizi Başlıyor...")
    print("-" * 50)
    
    # Analyzer oluştur
    analyzer = TurkcellTrendsAnalyzer()
    
    # Kullanıcıya seçenek sun
    print("\n📊 Veri türü seçin:")
    print("1️⃣ Haftalık veri (2022-2025) - Uzun dönem analizi")
    print("2️⃣ Günlük veri (2024) - Detaylı yıllık analizi")
    print("3️⃣ Günlük veri (Son 12 ay) - En güncel veriler")
    
    choice = input("\nSeçiminizi yapın (1/2/3): ").strip()
    
    if choice == "2":
        print("\n1️⃣ 2024 yılı günlük trend verilerini alıyor...")
        trend_data = analyzer.get_interest_over_time(2024, 2025, daily=True)
        output_file = 'turkcell_trends_2024_daily.csv'
    elif choice == "3":
        print("\n1️⃣ Son 12 ay günlük trend verilerini alıyor...")
        # Son 12 ay için özel timeframe
        analyzer.pytrends.build_payload(['turkcell'], cat=0, timeframe='today 12-m', geo='TR', gprop='')
        trend_data = analyzer.pytrends.interest_over_time()
        if not trend_data.empty and 'isPartial' in trend_data.columns:
            trend_data = trend_data.drop(columns=['isPartial'])
        analyzer.data = trend_data
        output_file = 'turkcell_trends_last_12m_daily.csv'
    else:
        print("\n1️⃣ Haftalık trend verilerini alıyor (2022-2025)...")
        trend_data = analyzer.get_interest_over_time(2022, 2025, daily=False)
        output_file = 'turkcell_trends_2022_2025_weekly.csv'
    
    if trend_data is not None:
        # Özet istatistikleri göster
        analyzer.get_summary_stats()
        
        # Zaman grafiğini çiz
        print("\n2️⃣ Zaman içinde trend grafiği çiziliyor...")
        analyzer.plot_interest_over_time()
        
        # Bölgesel verileri al
        print("\n3️⃣ Bölgesel trend verilerini alıyor...")
        regional_data = analyzer.get_interest_by_region()
        
        if regional_data is not None:
            print("\n📋 En çok aranan 10 bölge:")
            print(regional_data.head(10))
            
            # Bölgesel grafiği çiz
            print("\n4️⃣ Bölgesel trend grafiği çiziliyor...")
            analyzer.plot_regional_interest(regional_data, top_n=15)
        
        # Veriyi CSV olarak kaydet
        trend_data.to_csv(output_file)
        print(f"\n💾 Veriler '{output_file}' dosyasına kaydedildi")
        
        if regional_data is not None:
            regional_output = 'turkcell_regional_trends.csv'
            regional_data.to_csv(regional_output)
            print(f"💾 Bölgesel veriler '{regional_output}' dosyasına kaydedildi")
    
    print("\n✅ Analiz tamamlandı!")

if __name__ == "__main__":
    # Gerekli import'ları kontrol et
    try:
        import numpy as np
        main()
    except ImportError as e:
        print(f"❌ Eksik kütüphane: {e}")
        print("📦 Gerekli kütüphaneleri yüklemek için: pip install pytrends pandas matplotlib seaborn numpy")
